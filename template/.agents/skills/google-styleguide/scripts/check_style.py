#!/usr/bin/env python3
"""Check first-party Go formatting without writes; 2 means unverified."""

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys


SKIP = {".git", "vendor", "node_modules", ".venv", "__pycache__"}


def check(root):
    root = root.resolve(strict=True)
    names = subprocess.check_output(
        ["git", "-C", str(root), "ls-files", "--cached", "--others",
         "--exclude-standard", "-z"], stderr=subprocess.PIPE,
    )
    files = []
    for name in sorted(set(names.split(b"\0")) - {b""}):
        relative = Path(os.fsdecode(name))
        if relative.suffix != ".go" or SKIP.intersection(relative.parts):
            continue
        path = root / relative
        # Do not follow links outside the task or inspect deleted files.
        if path.is_symlink() or any(p.is_symlink() for p in path.parents if p != root):
            print("UNVERIFIED: symlink Go path: " + str(relative))
            return 2
        if path.exists():
            files.append(path)
    if not files:
        print("NOT_APPLICABLE: no first-party Go files; other styles not checked")
        return 0
    executable = shutil.which("gofmt")
    if executable is None:
        print("UNVERIFIED: gofmt unavailable")
        return 2
    failed = False
    for path in files:
        result = subprocess.run([executable, "-l", str(path)], capture_output=True,
                                text=True, timeout=30, stdin=subprocess.DEVNULL)
        if result.returncode:
            print("UNVERIFIED: gofmt failed: " + str(path.relative_to(root)))
            print(result.stderr.strip())
            return 2
        if result.stdout.strip():
            print("FAIL: " + str(path.relative_to(root)))
            failed = True
    if not failed:
        print("PASS: Go formatting (" + str(len(files)) + " files)")
    return 1 if failed else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[4])
    args = parser.parse_args()
    try:
        return check(args.root)
    except (OSError, subprocess.SubprocessError) as exc:
        print("UNVERIFIED: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
