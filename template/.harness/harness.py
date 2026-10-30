#!/usr/bin/env python3
"""Local verification receipts and Codex lifecycle integration (stdlib only)."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time


MODEL = "gpt-6.1-sol"
ROLES = {"kty_" + role: "kty-" + role + ".toml"
         for role in ("planner", "developer", "reviewer", "auditor")}
STATE_PREFIXES = (".harness/state/", ".harness/work/")


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE)


def fingerprint(root):
    """Include tracked deletions, untracked source, file modes and symlink text."""
    names = git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    digest = hashlib.sha256()
    for raw in sorted(set(names.split(b"\0")) - {b""}):
        name = os.fsdecode(raw)
        if name.startswith(STATE_PREFIXES):
            continue
        path = root / name
        digest.update(raw + b"\0")
        try:
            mode = path.lstat().st_mode
            digest.update(str(stat.S_IMODE(mode)).encode() + b"\0")
            if stat.S_ISLNK(mode):
                digest.update(b"link:" + os.fsencode(os.readlink(path)))
            elif stat.S_ISREG(mode):
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
            else:
                digest.update(b"non-file")
        except FileNotFoundError:
            digest.update(b"missing")
        digest.update(b"\0")
    return digest.hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + "." + str(os.getpid()) + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def read_json(path):
    return json.loads(path.read_text())


def load_checks(root):
    data = read_json(root / ".harness/checks.json")
    checks = data.get("checks") if isinstance(data, dict) else None
    if not isinstance(checks, list) or not checks:
        raise ValueError(".harness/checks.json에 실제 검증 명령을 하나 이상 등록하세요.")
    names = set()
    for check in checks:
        if not isinstance(check, dict) or not isinstance(check.get("name"), str):
            raise ValueError("각 check에는 name 문자열이 필요합니다.")
        if not check["name"].strip() or check["name"] in names:
            raise ValueError("check 이름은 비어 있지 않은 고유 문자열이어야 합니다.")
        names.add(check["name"])
        argv = check.get("argv")
        if not isinstance(argv, list) or not argv or any(
            not isinstance(arg, str) or "\0" in arg for arg in argv
        ) or not argv[0]:
            raise ValueError("argv는 실행 파일부터 시작하는 문자열 배열이어야 합니다.")
        timeout = check.get("timeout_seconds", 120)
        if type(timeout) is not int or not 1 <= timeout <= 600:
            raise ValueError("timeout_seconds는 1부터 600 사이의 정수여야 합니다.")
    return checks


def run_check(root, check):
    process = subprocess.Popen(check["argv"], cwd=root, stdin=subprocess.DEVNULL,
                               start_new_session=True)
    try:
        return process.wait(timeout=check.get("timeout_seconds", 120))
    except (subprocess.TimeoutExpired, KeyboardInterrupt):
        # A test runner may have spawned servers; stop its process group as well.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()
        raise


def verify(root):
    receipt_path = root / ".harness/state/verification.json"
    # A failed rerun must invalidate even a previously passing receipt.
    write_json(receipt_path, {"passed": False, "results": []})
    checks = load_checks(root)
    before = fingerprint(root)
    results = []
    for check in checks:
        print("검증: " + check["name"], flush=True)
        started = time.monotonic()
        try:
            code = run_check(root, check)
            error = None
        except (OSError, subprocess.TimeoutExpired) as exc:
            code, error = -1, str(exc)
            print(error, file=sys.stderr)
        results.append({"name": check["name"], "argv": check["argv"],
                        "exit_code": code, "error": error,
                        "seconds": round(time.monotonic() - started, 3)})
        if code:
            break
    after = fingerprint(root)
    passed = before == after and len(results) == len(checks) and all(
        item["exit_code"] == 0 for item in results
    )
    write_json(receipt_path, {"passed": passed, "fingerprint": after,
                              "checked_at": time.time(), "results": results})
    if before != after:
        print("검증 도중 파일이 변경됐습니다. 최신 상태에서 다시 검증하세요.", file=sys.stderr)
    print("검증 통과" if passed else "검증 실패", flush=True)
    return 0 if passed else 1


def session_path(root, event):
    session = event.get("session_id")
    if not isinstance(session, str) or not session:
        raise ValueError("hook event에 session_id가 없습니다.")
    key = hashlib.sha256(session.encode()).hexdigest()
    return root / ".harness/state/sessions" / (key + ".json")


def hook(root, event):
    name = event.get("hook_event_name")
    current = fingerprint(root)
    path = session_path(root, event)
    if name == "SessionStart":
        # Resume/compact must retain the original baseline, including pending work.
        if not path.exists():
            write_json(path, {"baseline": current})
        return {}
    if name != "Stop":
        raise ValueError("지원하지 않는 hook event입니다: " + str(name))
    try:
        baseline = read_json(path)["baseline"]
    except (OSError, ValueError, KeyError):
        baseline = None
    if baseline == current:
        return {}
    try:
        receipt = read_json(root / ".harness/state/verification.json")
        valid = receipt.get("passed") is True and receipt.get("fingerprint") == current
    except (OSError, ValueError, AttributeError):
        valid = False
    if valid:
        return {}
    reason = ("작업 파일이 변경됐지만 최신 코드의 검증 성공 기록이 없습니다. "
              ".harness/checks.json을 확인하고 python3 .harness/harness.py verify를 실행하세요. "
              "실행 불가능한 환경 제약이면 실패 사실과 남은 검증을 사용자에게 보고하세요.")
    if event.get("stop_hook_active"):
        # One reminder per continuation; don't hold the session hostage on an outage.
        return {"systemMessage": "KTY 검증 미완료: " + reason}
    return {"decision": "block", "reason": reason}


def effort_args(effort):
    # Omit the key entirely by default; let Codex resolve its effective settings.
    return [] if effort is None else ["--config", "model_reasoning_effort=" + json.dumps(effort)]


def launch(root, prompt, effort=None):
    command = ["codex", "--cd", str(root), "--model", MODEL] + effort_args(effort)
    for filename in ROLES.values():
        path = root / ".codex/agents" / filename
        if not path.is_file():
            raise ValueError("역할 설정이 없습니다. 재설치하세요: " + str(path))
    if prompt is None:
        prompt = ("AGENTS.md와 .harness/setup.md, .harness/setup-status.md를 읽고 "
                  "이전에 요청한 하네스 설치·설정의 남은 단계를 이어가라. "
                  "완료한 단계는 근거를 확인하고 반복하지 말라. "
                  "설정이 모두 끝났으면 상태만 짧게 알리고 다음 과제 요청을 기다려라.")
    command.extend(["--", prompt])
    os.execvp(command[0], command)


def readonly_role(root, role, task, effort=None):
    """Child role files cannot enforce permissions; isolate the whole CLI process."""
    filename = ROLES["kty_" + role]
    path = root / ".codex/agents" / filename
    if not path.is_file():
        raise ValueError("역할 설정이 없습니다. 재설치하세요: " + str(path))
    prompt = ("이 호출은 독립된 읽기 전용 " + role + " 작업이다. "
              "시작 전에 " + str(path) + "의 역할 지침, .harness/project-profile.md와 "
              ".harness/principles.md를 읽어 적용하라. "
              "파일을 수정하거나 권한을 확대하지 말고 결과만 응답으로 반환하라. "
              "다른 에이전트를 만들지 마라. 실행할 수 없는 검증은 그 한계를 밝혀라.\n\n"
              "검수·감사 요청:\n" + task)
    command = ["codex", "exec", "--cd", str(root), "--model", MODEL,
               *effort_args(effort), "--sandbox", "read-only", "--ephemeral", "--", prompt]
    os.execvp(command[0], command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("verify")
    commands.add_parser("fingerprint")
    commands.add_parser("hook")
    codex = commands.add_parser("codex")
    codex.add_argument("--effort", metavar="LEVEL", help="허용된 추론 강도를 명시할 때만 사용")
    codex.add_argument("prompt", nargs="?")
    for role in ("review", "audit"):
        command = commands.add_parser(role)
        command.add_argument("--effort", metavar="LEVEL", help="허용된 추론 강도를 명시할 때만 사용")
        command.add_argument("task")
    args = parser.parse_args()
    try:
        root = args.root.resolve()
        if args.command == "verify":
            return verify(root)
        if args.command == "fingerprint":
            print(fingerprint(root))
        elif args.command == "codex":
            launch(root, args.prompt, args.effort)
        elif args.command in ("review", "audit"):
            readonly_role(root, "reviewer" if args.command == "review" else "auditor", args.task,
                          args.effort)
        else:
            print(json.dumps(hook(root, json.load(sys.stdin)), ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        if args.command == "hook":
            print(json.dumps({"systemMessage": "KTY hook 실행 실패: " + str(exc)}, ensure_ascii=False))
        else:
            print("오류: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
