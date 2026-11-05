#!/usr/bin/env python3
"""Optional local math environment; never modifies global Python or trust settings."""
import argparse
import ast
import asyncio
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import traceback

DIRECT = ["sympy==1.14.0", "z3-solver==5.3.3.0"]
MCP = ["mcp-sympy==0.1.0", "mcp==1.30.0", "fastmcp==3.4.11", "anyio==4.16.0"]
SERVER = "kty_math_sympy"


def checked_path(root, relative):
    path = root / relative
    for item in [path, *path.parents]:
        if item == root:
            break
        if item.is_symlink():
            raise ValueError("symlink destination: " + str(item))
    return path


def run(argv, timeout=90):
    """Bound the whole process group, including hung MCP descendants."""
    process = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
        raise TimeoutError("timeout: " + str(argv[:3]) + "\n" + stderr[-6000:])
    if process.returncode:
        raise RuntimeError("command failed: " + str(argv[:3]) + "\n" + stderr[-6000:])
    return stdout


def save(path, data):
    temporary = path.with_suffix(".new")
    if temporary.is_symlink():
        raise ValueError("symlink destination: " + str(temporary))
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def register(root, server=SERVER, script="math_setup.py"):
    import tomllib
    path = checked_path(root, ".codex/config.toml")
    text = path.read_text() if path.exists() else ""
    expected = {"command": sys.executable,
                "args": [str(root / ".harness" / script), "serve"],
                "startup_timeout_sec": 30, "tool_timeout_sec": 30}
    parsed = tomllib.loads(text)
    existing = parsed.get("mcp_servers", {}).get(server)
    if existing is not None:
        if existing != expected:
            raise ValueError("existing " + server + " differs; preserve it and review config manually")
        return
    addition = "\n[mcp_servers." + server + "]\n" + "\n".join(
        name + " = " + json.dumps(value, ensure_ascii=False) for name, value in expected.items()) + "\n"
    tomllib.loads(text + addition)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = checked_path(root, ".codex/config.toml.kty-new")
    temporary.write_text(text + addition)
    temporary.replace(path)


def direct_check():
    import sympy
    import z3
    x = sympy.Symbol("x", real=True)
    roots = sympy.solve(x*x - 5*x + 6, x)
    if roots != [2, 3] or any(r*r - 5*r + 6 != 0 for r in roots):
        raise ValueError("SymPy substitution failed")
    y = z3.Int("y")
    solver = z3.Solver()
    solver.add(y >= 0, y <= 2, y > 2)
    if solver.check() != z3.unsat:
        raise ValueError("Z3 contradiction check failed")
    return {"sympy_roots": [int(r) for r in roots], "residuals": [0, 0], "z3": "unsat"}


async def mcp_check():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    # Synthetic input only. Does not read or send task files.
    params = StdioServerParameters(command=sys.executable, args=["-m", "mcp_sympy"])
    async with asyncio.timeout(40):
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=15)) as client:
                await client.initialize()
                names = [tool.name for tool in (await client.list_tools()).tools]
                if "sympy_solve" not in names:
                    raise ValueError("sympy_solve not exposed")
                answer = await client.call_tool("sympy_solve", {
                    "equation": "x**2-5*x+6", "variables": "x"})
                if answer.isError:
                    raise ValueError("MCP tool error: " + str(answer))
                result = answer.structuredContent
                if result is None:
                    result = "\n".join(c.text for c in answer.content if c.type == "text")
                if isinstance(result, dict):
                    result = result.get("result")
                roots = ast.literal_eval(result) if isinstance(result, str) else result
                if not isinstance(roots, list) or sorted(roots) != [2, 3]:
                    raise ValueError("unexpected roots: " + repr(roots))
                if any(r*r - 5*r + 6 != 0 for r in roots):
                    raise ValueError("MCP substitution failed")
                return {"initialize": True, "tool_list": True, "equation_call": True,
                        "roots": roots, "residuals": [0, 0], "transport": "local_sdk_stdio"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["install", "check", "register", "serve", "smoke"])
    parser.add_argument("--direct-only", action="store_true", help="SymPy/Z3 only; no MCP attempt")
    parser.add_argument("--register", action="store_true", help="register after successful local SDK check")
    parser.add_argument("--fresh", action="store_true", help="new isolated venv; preserve old environment")
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        raise ValueError("수학 설치기는 Python 3.11 이상 필요; 기본 하네스는 3.9 이상")
    if args.direct_only and (args.register or args.action in ("register", "serve")):
        raise ValueError("direct-only cannot register/serve MCP")
    if args.action == "smoke":
        import faulthandler
        faulthandler.dump_traceback_later(15)
        result = {"direct": direct_check(), "sdk_mcp": "not_requested"}
        if not args.direct_only:
            result["sdk_mcp"] = asyncio.run(mcp_check())
        faulthandler.cancel_dump_traceback_later()
        print(json.dumps(result))
        return
    root = Path(__file__).resolve().parents[1]
    if Path(run(["git", "-C", str(root), "rev-parse", "--show-toplevel"]).strip()).resolve() != root:
        raise ValueError("실제 과제 Git 루트에 하네스를 먼저 설치하세요")
    base = checked_path(root, ".harness/work/math-tools")
    state = checked_path(root, ".harness/work/math-tools/selected.json")
    selected = json.loads(state.read_text()) if state.exists() else None
    if args.action in ("serve", "register"):
        if not selected or selected.get("sdk_verified") is not True:
            raise ValueError("verified MCP environment missing; install/check first")
        if args.action == "serve":
            python = selected["python"]
            os.execv(python, [python, "-m", "mcp_sympy"])
        register(root)
        print("프로젝트 MCP 설정 등록 완료. 현재 Codex 연결·호출은 별도 미검증.")
        return
    if args.action == "check" and not selected:
        raise ValueError("no environment; run install first")
    # Only an explicit install creates an environment; checks never install packages.
    base.mkdir(parents=True, exist_ok=True)
    report = {"checked_at": datetime.now(timezone.utc).isoformat(), "passed": False,
              "codex_native": "unverified", "hook_events": "unverified",
              "mcp_solver": "separate_solver_setup_required", "direct_only": args.direct_only}
    try:
        report["current_stage"] = "dependencies"
        packages = DIRECT + ([] if args.direct_only else MCP)
        if args.action == "install" and (args.fresh or not selected or selected.get("pins") != packages):
            env = Path(tempfile.mkdtemp(prefix="env-", dir=base))
            run([sys.executable, "-m", "venv", str(env)])
            python = str(env / "bin/python")  # Do not resolve the venv symlink.
            run([python, "-m", "pip", "install", "--disable-pip-version-check", *packages], timeout=240)
        else:
            python = selected["python"]
            packages = selected["pins"]
        report["python"] = python
        run([python, "-m", "pip", "check"])
        report["current_stage"] = "direct_and_sdk" if not args.direct_only else "direct"
        # A direct-only check must not contact even a previously installed MCP.
        direct_only = args.direct_only or not any(p.startswith("mcp-sympy==") for p in packages)
        command = [python, "-B", str(Path(__file__).resolve()), "smoke"]
        if direct_only:
            command.append("--direct-only")
        report["checks"] = json.loads(run(command, timeout=60))
        report["resolved_packages"] = run([python, "-m", "pip", "freeze"]).splitlines()
        report["passed"] = True
        selected = {"python": python, "pins": packages, "sdk_verified": not direct_only}
        save(state, selected)
        if args.register:
            if direct_only:
                raise ValueError("MCP not tested; registration skipped")
            report["current_stage"] = "registration"
            register(root)
            report["project_config_registered"] = True
    except Exception as exc:
        report["passed"] = False
        report["error"] = str(exc)
        if (selected and report.get("python") == selected["python"]
                and report.get("current_stage") != "registration"):
            selected["sdk_verified"] = False
            save(state, selected)
        raise
    finally:
        save(checked_path(root, ".harness/work/math-tools/latest-check.json"), report)
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        traceback.print_exc()
        print("수학 도구 단계 실패: " + str(exc), file=sys.stderr)
        print("허용된 라이브러리 직접 호출은 별도 확인. MCP 연결 성공으로 보고하지 마세요.", file=sys.stderr)
        raise SystemExit(1)
