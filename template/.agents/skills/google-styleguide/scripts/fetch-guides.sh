#!/usr/bin/env bash
# Maintainer-only refresh from an explicitly reviewed immutable upstream commit.
set -euo pipefail
if [[ $# -ne 1 || ! "$1" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Usage: fetch-guides.sh <reviewed-40-character-upstream-commit>" >&2
  exit 2
fi
readonly REVISION="$1"
readonly RAW_BASE="https://raw.githubusercontent.com/google/styleguide/${REVISION}"
readonly DEST="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../references" && pwd)"
STAGING="$(mktemp -d)"
readonly STAGING
trap 'rm -rf -- "${STAGING}"' EXIT
readonly PATHS=(
  'go/guide.md' 'go/decisions.md' 'go/best-practices.md'
  'docguide/style.md' 'docguide/READMEs.md' 'shellguide.md' 'pyguide.md' 'LICENSE'
)
for upstream_path in "${PATHS[@]}"; do
  curl -fsSL "${RAW_BASE}/${upstream_path}" \
    -o "${STAGING}/${upstream_path//\//-}"
done
# No destination is changed until every download succeeds.
python3 - "${STAGING}" "${REVISION}" <<'PYTHON'
import datetime
import hashlib
import json
from pathlib import Path
import sys
stage = Path(sys.argv[1])
manifest = {"upstream_commit": sys.argv[2], "files": {
    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted(stage.iterdir()) if p.is_file()}}
(stage / "snapshot.json").write_text(json.dumps(manifest, indent=2) + "\n")
(stage / "FETCHED").write_text(datetime.datetime.now(datetime.timezone.utc).isoformat() + "\n")
PYTHON
for source in "${STAGING}"/*; do
  cp -- "${source}" "${DEST}/"
done
echo 'Updated snapshot; review upstream changes, NOTICE, and skill summary before publishing.'
