#!/usr/bin/env python3
"""Install only repo-local files; preserve project instructions and domain slots."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


SOURCE = Path(__file__).resolve().parents[1]
START = "<!-- kty-codex-harness:start -->"
END = "<!-- kty-codex-harness:end -->"
SLOTS = {".harness/project-profile.md", ".harness/checks.json", ".harness/task-evidence.md"}
IGNORE = ["/.harness/state/", "/.harness/work/"]
HOOK_COMMAND = 'python3 "$(git rev-parse --show-toplevel)/.harness/harness.py" hook'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, name):
    path = root / name
    for part in [path, *path.parents]:
        if part == root:
            break
        if part.is_symlink():
            raise ValueError("설치 대상이 심볼릭 링크입니다: " + str(part))
        if part != path and part.exists() and not part.is_dir():
            raise ValueError("설치 대상의 상위 경로가 폴더가 아닙니다: " + str(part))
    if path.exists() and not path.is_file():
        raise ValueError("설치 대상이 파일이 아닙니다: " + str(path))
    return path


def instructions(existing, block):
    if START in existing or END in existing:
        if existing.count(START) != 1 or existing.count(END) != 1:
            raise ValueError("AGENTS.md의 하네스 블록 마커가 중복되거나 손상됐습니다.")
        first, last = existing.index(START), existing.index(END)
        if first >= last:
            raise ValueError("AGENTS.md의 하네스 블록 순서가 잘못됐습니다.")
        return existing[:first] + block.rstrip() + existing[last + len(END):]
    return existing + ("\n\n" if existing else "") + block


def hook_config(existing):
    value = json.loads(existing) if existing else {}
    if not isinstance(value, dict) or not isinstance(value.get("hooks", {}), dict):
        raise ValueError("기존 hooks.json 형식이 올바르지 않습니다.")
    hooks = value.setdefault("hooks", {})
    for name in ("SessionStart", "Stop"):
        groups = hooks.setdefault(name, [])
        if not isinstance(groups, list):
            raise ValueError("기존 hook 그룹이 배열이 아닙니다: " + name)
        present = any(isinstance(group, dict) and any(
            isinstance(handler, dict) and handler.get("command") == HOOK_COMMAND
            for handler in group.get("hooks", [])
        ) for group in groups)
        if not present:
            groups.append({"hooks": [{"type": "command", "command": HOOK_COMMAND,
                                      "timeout": 10}]})
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def install(root, hooks=True):
    root = root.resolve(strict=True)
    actual = subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"], text=True,
    ).strip()
    if Path(actual).resolve() != root:
        raise ValueError("설치 대상은 기존 Git 작업 공간의 루트여야 합니다.")
    manifest_path = safe_path(root, ".harness/state/install.json")
    old = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    if not isinstance(old, dict):
        raise ValueError("설치 manifest 형식이 올바르지 않습니다.")
    changes = {}
    managed = {}
    for source in sorted((SOURCE / "template").rglob("*")):
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        name = source.relative_to(SOURCE / "template").as_posix()
        if name == "AGENTS.block.md":
            continue
        target = safe_path(root, name)
        content = source.read_bytes()
        if target.exists():
            current = target.read_bytes()
            if name in SLOTS or name == ".codex/config.toml":
                continue
            if current != content and old.get(name) != sha(current):
                raise ValueError("로컬 수정/기존 파일을 덮어쓸 수 없습니다: " + name)
        changes[name] = content
        managed[name] = sha(content)
    for name in ("AGENTS.md", ".gitignore"):
        path = safe_path(root, name)
        existing = path.read_text() if path.exists() else ""
        if name == "AGENTS.md":
            content = instructions(existing, (SOURCE / "template/AGENTS.block.md").read_text())
        else:
            lines = existing.splitlines()
            additions = [line for line in IGNORE if line not in lines]
            content = existing + (("\n" if existing and not existing.endswith("\n") else "")
                                  + "\n".join(additions) + "\n" if additions else "")
        changes[name] = content.encode()
    if hooks:
        path = safe_path(root, ".codex/hooks.json")
        changes[".codex/hooks.json"] = hook_config(path.read_text() if path.exists() else "").encode()
    # Validate every destination before writing anything; conflicts do not leave partial installs.
    for name, content in changes.items():
        path = safe_path(root, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        if name.endswith(".sh"):
            path.chmod(0o755)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(managed, indent=2) + "\n")
    print("설치 완료: " + str(root))
    print("모델: gpt-6.1-sol / xhigh — bash .harness/codex.sh 로 실행")
    print("프로필과 checks.json을 채운 뒤 python3 .harness/harness.py verify 실행")
    if hooks:
        print("네이티브 훅은 Codex의 /hooks에서 검토·신뢰 후 활성화됩니다.")
    else:
        print("훅 미설치: 검증 명령을 명시적으로 실행하세요.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--no-hooks", action="store_true")
    args = parser.parse_args()
    try:
        install(args.target, hooks=not args.no_hooks)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print("설치 실패: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
