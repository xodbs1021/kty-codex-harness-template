"""Read-only file installation check, separate from application/runtime checks."""
import argparse
import hashlib
import json
from pathlib import Path

from harness import ROLES

SKILLS = ("kty-harness", "google-styleguide", "google-api-design", "readable-writing")
MUTABLE = {".codex/config.toml", ".harness/project-profile.md", ".harness/checks.json",
           ".harness/task-evidence.md", ".harness/setup-status.md"}


def inspect(root):
    problems = []
    required = {"AGENTS.md", ".codex/config.toml", ".harness/setup.md",
                ".harness/project-profile.md", ".harness/checks.json",
                ".harness/task-evidence.md", ".harness/setup-status.md"}
    required.update(".codex/agents/" + name for name in ROLES.values())
    required.update(".agents/skills/" + name + "/SKILL.md" for name in SKILLS)
    try:
        inventory = json.loads((root / ".harness/state/install-inventory.json").read_text())
        manifest = json.loads((root / ".harness/state/install.json").read_text())
        if not isinstance(inventory, list) or not isinstance(manifest, dict):
            raise ValueError("invalid manifest/inventory")
        required.update(inventory)
        for name in required | set(manifest):
            path = root / name
            if Path(name).is_absolute() or ".." in Path(name).parts:
                raise ValueError("invalid manifest path")
            if any(p.is_symlink() for p in [path, *path.parents] if p != root and root in p.parents):
                problems.append(name + ": symlink")
            elif not path.is_file():
                problems.append(name + ": missing")
            elif name in manifest and name not in MUTABLE:
                # Project slots/config are user-owned, not template integrity failures.
                if hashlib.sha256(path.read_bytes()).hexdigest() != manifest[name]:
                    problems.append(name + ": modified (review local changes)")
    except (OSError, ValueError, TypeError) as exc:
        problems.append(str(exc))
    return {"files_ok": not problems, "problems": sorted(problems),
            "role_files": sum((root / ".codex/agents" / n).is_file() for n in ROLES.values()),
            "skill_files": sum((root / ".agents/skills" / n / "SKILL.md").is_file() for n in SKILLS),
            "runtime_skill_discovery": "unverified", "runtime_role_calls": "unverified",
            "hook_trust": "unverified", "hook_events": "unverified",
            "codex_mcp_calls": "unverified", "application_checks": "not_run"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = inspect(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["files_ok"] else 1)
