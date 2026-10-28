#!/usr/bin/env python3
"""Prepare and inspect an isolated 15-minute practice fixture. No AI calls or trust changes."""

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


SOURCE = Path(__file__).resolve().parents[1]
TRACE_COMMAND = 'python3 "$(git rev-parse --show-toplevel)/.harness/state/practice_hook_trace.py"'
APP = '''def total(prices):
    return sum(prices) + 1


def can_read_document(user_id, document):
    return bool(user_id)
'''
TASK = """# Compatibility practice fixture — not an exam solution

Review practice_app.py without modifying it.
- total(prices): return the exact sum; empty input must return 0.
- can_read_document(user_id, document): return True only for a nonempty user_id
  equal to document['owner_id']; other users must be denied.

probe_marker.py and practice_check.py test only the verification-hook lifecycle.
Their passing result does NOT mean practice_app.py is correct or secure.
The two intentional bugs in practice_app.py must remain for independent reviews.
"""


def prepare(parent):
    if sys.version_info < (3, 9):
        raise ValueError("Python 3.9 이상이 필요합니다.")
    parent = parent.resolve(strict=True)
    if not parent.is_dir():
        raise ValueError("허용된 쓰기 가능한 부모 폴더를 지정하세요.")
    root = Path(tempfile.mkdtemp(prefix="kty-practice-", dir=parent)).resolve()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run([sys.executable, str(SOURCE / "scripts/install.py"), str(root)],
                   check=True, capture_output=True, text=True)
    (root / "PRACTICE_TASK.md").write_text(TASK)
    (root / "practice_app.py").write_text(APP)
    (root / "probe_marker.py").write_text("VALUE = 0\n")
    (root / "practice_check.py").write_text(
        "from probe_marker import VALUE\nassert VALUE == 1, 'practice marker must be 1'\n"
        "print('PRACTICE_MARKER_OK — hook lifecycle only')\n")
    with (root / ".gitignore").open("a") as stream:
        stream.write("__pycache__/\n")
    checks = {"checks": [{"name": "practice-marker-only",
                          "argv": [sys.executable, "-B", "practice_check.py"],
                          "timeout_seconds": 10}]}
    (root / ".harness/checks.json").write_text(json.dumps(checks, indent=2) + "\n")
    state = root / ".harness/state"
    shutil.copyfile(SOURCE / "scripts/practice_hook_trace.py", state / "practice_hook_trace.py")
    hooks = {"hooks": {name: [{"hooks": [{"type": "command", "command": TRACE_COMMAND,
                                         "timeout": 10}]}]
                       for name in ("SessionStart", "Stop")}}
    (root / ".codex/hooks.json").write_text(json.dumps(hooks, indent=2) + "\n")
    metadata = {"schema": 1, "purpose": "compatibility-only", "source_package": str(SOURCE),
                "runbook": str(SOURCE / "docs/practice-runbook.md"),
                "report_argv": [sys.executable, str(SOURCE / "scripts/practice_probe.py"),
                                "report", str(root)]}
    (state / "practice-fixture.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with (root / "AGENTS.md").open("a") as stream:
        stream.write("\n## 사전체험 짧은 입력\n\n"
                     "사용자의 전체 요청이 정확히 `훅 실험`, `듀얼 검수`, `결과 정리` 중 하나일 때만 "
                     ".harness/state/practice-fixture.json의 runbook 경로를 읽고 "
                     "각각 입력 2, 입력 3, 입력 4의 해당 단계만 실행한다. "
                     "이 짧은 요청은 그 단계의 상세 요청을 실행하라는 뜻이다. "
                     "그 밖의 검수 요청에는 실행표나 관찰자용 예상 결함을 읽지 않는다.\n")
    return {"fixture": str(root), "source_package": str(SOURCE),
            "next": "이 검증 폴더에서 새 Codex 세션을 열고 정상 프로젝트 신뢰와 /hooks 확인을 진행하세요."}


def report(root):
    root = root.resolve(strict=True)
    if not (root / ".harness/state/practice-fixture.json").is_file():
        raise ValueError("practice_probe.py가 만든 검증 폴더가 아닙니다.")
    state = root / ".harness/state"
    trace = state / "practice-hook-events.jsonl"
    events = [json.loads(line) for line in trace.read_text().splitlines()] if trace.exists() else []
    sessions = {}
    for event in events:
        sessions.setdefault(event["session_key"], []).append(event)
    flows = []
    for key, items in sessions.items():
        started = blocked = released = automatic = False
        for item in items:
            if item["exit_code"] != 0:
                continue
            if item["event"] == "SessionStart":
                started = True
            if item["event"] == "Stop" and started:
                if item["output"].get("decision") == "block":
                    blocked = True
                elif blocked and item.get("receipt_passed") and item["output"] == {}:
                    released = True
                    automatic = automatic or bool(item.get("stop_hook_active"))
        flows.append({"session_key": key,
                      "baseline_file_present": (state / "sessions" / (key + ".json")).is_file(),
                      "session_start_observed": started,
                      "stop_block_observed": blocked, "stop_release_after_receipt": released,
                      "automatic_continuation_observed": automatic})
    receipt_path = state / "verification.json"
    receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    fingerprint = subprocess.check_output([sys.executable, str(root / ".harness/harness.py"),
                                           "fingerprint"], text=True).strip()
    return {"fixture": str(root), "recorded_callback_count": len(events), "hook_flows": flows,
            "receipt_current": receipt.get("passed") is True and receipt.get("fingerprint") == fingerprint,
            "review_fixture_unchanged": (root / "practice_app.py").read_text() == APP,
            "dual_review_execution": "NOT_ASSESSED — inspect actual agent/process starts and responses",
            "scope": "Recorded hook callbacks and marker check only; not Probe certification or app correctness"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare").add_argument("parent", type=Path)
    commands.add_parser("report").add_argument("fixture", type=Path)
    args = parser.parse_args()
    try:
        value = prepare(args.parent) if args.command == "prepare" else report(args.fixture)
        print(json.dumps(value, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print("사전체험 준비/확인 실패: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
