"""Install pinned upstream mcp-solver and diagnose each startup layer."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

from math_setup import checked_path, register, run, save

COMMIT = "24b7d6fb1d5e361eeb8558b6119ca8e8cb083a3a"
REPOSITORY = "https://github.com/szeider/mcp-solver.git"
PINS = ["mcp==1.30.0", "anyio==4.16.0", "agentic-python-coder==3.4.3", "uv==0.11.21"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "check", "register", "serve"])
    parser.add_argument("--register", action="store_true")
    parser.add_argument("--fresh", action="store_true")
    args = parser.parse_args()
    if not (3, 13) <= sys.version_info[:2] < (3, 15):
        raise ValueError("mcp-solver v4 requires Python 3.13 or 3.14; use an allowed installed interpreter")
    root = Path(__file__).resolve().parents[1]
    if Path(run(["git", "-C", str(root), "rev-parse", "--show-toplevel"]).strip()).resolve() != root:
        raise ValueError("install harness into actual task Git root first")
    base = checked_path(root, ".harness/work/solver-tools")
    state = checked_path(root, ".harness/work/solver-tools/selected.json")
    selected = json.loads(state.read_text()) if state.exists() else None
    if args.action in ("register", "serve"):
        if not selected or selected.get("verified") is not True:
            raise ValueError("complete solver check required before registration/start")
        if args.action == "register":
            register(root, "kty_math_solver", "solver_setup.py")
            return
        python = selected["python"]
        os.environ["MCP_SOLVER_DEV"] = selected["source"]
        os.environ["PATH"] = str(Path(python).parent) + os.pathsep + os.environ.get("PATH", "")
        os.environ["UV_PYTHON_DOWNLOADS"] = "never"
        os.execv(python, [python, "-m", "mcp_solver.agent.mcp_server"])
    if args.action == "check" and not selected:
        raise ValueError("install first")
    base.mkdir(parents=True, exist_ok=True)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "passed": False,
              "codex_native": "unverified", "cofa_probe": "not_independently_observed",
              "source_commit": COMMIT, "stages": {}}
    try:
        report["current_stage"] = "dependencies"
        if args.action == "install" and (args.fresh or not selected):
            folder = Path(tempfile.mkdtemp(prefix="installation-", dir=base))
            source = folder / "source"
            run(["git", "clone", "--no-checkout", REPOSITORY, str(source)], timeout=120)
            run(["git", "-C", str(source), "checkout", "--detach", COMMIT])
            run([sys.executable, "-m", "venv", str(folder / "venv")])
            python = str(folder / "venv/bin/python")
            run([python, "-m", "pip", "install", "--disable-pip-version-check", *PINS,
                 str(source / "minion"), str(source) + "[agent]"], timeout=300)
            selected = {"python": python, "source": str(source), "verified": False}
            save(state, selected)
        python, source = selected["python"], Path(selected["source"])
        report["python"], report["source"] = python, str(source)
        if run(["git", "-C", str(source), "rev-parse", "HEAD"]).strip() != COMMIT:
            raise ValueError("source commit differs")
        if run(["git", "-C", str(source), "status", "--porcelain"]).strip():
            raise ValueError("source has local edits; preserve and review before using")
        run([python, "-m", "pip", "check"])
        report["resolved_packages"] = run([python, "-m", "pip", "freeze"]).splitlines()
        for stage in ("thread", "asyncio-thread", "anyio-thread", "engine", "solver"):
            report["current_stage"] = stage
            save(base / "latest-check.json", report)
            timeout = 20 if "thread" in stage else 90
            report["stages"][stage] = json.loads(run([
                python, "-B", str(root / ".harness/solver_probe.py"), stage, str(source)], timeout=timeout))
        selected["verified"] = True
        save(state, selected)
        report["passed"] = True
        if args.register:
            report["current_stage"] = "registration"
            register(root, "kty_math_solver", "solver_setup.py")
            report["project_config_registered"] = True
    except Exception as exc:
        report["passed"] = False
        report["error"] = str(exc)
        if (selected and report.get("python") == selected["python"]
                and report.get("current_stage") != "registration"):
            selected["verified"] = False
            save(state, selected)
        raise
    finally:
        save(checked_path(root, ".harness/work/solver-tools/latest-check.json"), report)
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("solver installation/check failed: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
