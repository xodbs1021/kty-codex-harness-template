#!/usr/bin/env bash
# Non-mutating portable checker; accepts --root for a directly read package.
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR
exec python3 -B "${SCRIPT_DIR}/check_style.py" "$@"
