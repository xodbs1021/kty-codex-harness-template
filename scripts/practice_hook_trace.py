#!/usr/bin/env python3
"""Disposable practice hook adapter: forward the real hook and record its result."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    # This file is copied into <fixture>/.harness/state/ before use.
    root = Path(__file__).resolve().parents[2]
    if not (root / ".harness/state/practice-fixture.json").is_file():
        print("이 추적기는 준비 도구가 만든 검증 폴더 안의 복사본으로만 실행합니다.", file=sys.stderr)
        return 2
    payload = sys.stdin.read()
    result = subprocess.run([sys.executable, str(root / ".harness/harness.py"), "hook"],
                            input=payload, capture_output=True, text=True, cwd=root)
    try:
        event = json.loads(payload)
        output = json.loads(result.stdout)
        receipt_path = root / ".harness/state/verification.json"
        receipt = json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        session = str(event.get("session_id", ""))
        record = {"at": time.time(), "event": event.get("hook_event_name"),
                  "session_key": hashlib.sha256(session.encode()).hexdigest(),
                  "stop_hook_active": event.get("stop_hook_active", False),
                  "exit_code": result.returncode, "output": output,
                  "receipt_passed": receipt.get("passed") is True,
                  "receipt_fingerprint": receipt.get("fingerprint")}
        with (root / ".harness/state/practice-hook-events.jsonl").open("a") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    except (OSError, ValueError, AttributeError) as exc:
        print("Practice trace unavailable: " + str(exc), file=sys.stderr)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
