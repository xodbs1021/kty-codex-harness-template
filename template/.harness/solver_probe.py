"""Synthetic diagnostics: threads -> inner engine -> solver -> Z3 constraints."""
import argparse
import asyncio
import faulthandler
import json
import os
from pathlib import Path
import sys
import threading


async def probe(stage):
    if stage == "asyncio-thread":
        return {"value": await asyncio.to_thread(lambda: 42)}
    if stage == "anyio-thread":
        import anyio
        return {"value": await anyio.to_thread.run_sync(lambda: 42)}
    from datetime import timedelta
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    module = "agentic_python_coder.mcp_server" if stage == "engine" else "mcp_solver.agent.mcp_server"
    params = StdioServerParameters(command=sys.executable, args=["-m", module], env=dict(os.environ))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write, read_timeout_seconds=timedelta(seconds=30)) as client:
            await client.initialize()
            names = [tool.name for tool in (await client.list_tools()).tools]
            if "submit_code" not in names:
                raise ValueError("engine missing submit_code")
            result = {"initialize": True, "tools": names}
            if stage == "engine":
                return result

            async def call(name, arguments):
                answer = await client.call_tool(name, arguments)
                if answer.isError:
                    raise ValueError(str(answer))
                if answer.structuredContent is not None:
                    return answer.structuredContent
                text = "\n".join(c.text for c in answer.content if c.type == "text")
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return text

            await call("select_backend", {"solver": "z3"})
            code = ('import json, z3\nx = z3.Int("x")\ns = z3.Solver()\n'
                    's.add(x >= 0, x <= 2, x > 2)\n'
                    'print(json.dumps({"status": str(s.check())}))\n')
            executed = await call("python_exec", {"code": code, "timeout": 15})
            output = executed.get("output", executed.get("stdout", ""))
            if executed.get("success") is not True or json.loads(output.strip()) != {"status": "unsat"}:
                raise ValueError("Z3 independent contradiction check failed: " + repr(executed))
            submitted = await call("submit_code", {"code": code})
            if submitted.get("ok") is not True:
                raise ValueError("submission syntax check failed")
            result.update({"z3": "unsat", "independent_check": "x<=2 and x>2 contradiction",
                           "submit_code": True})
            return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["thread", "asyncio-thread", "anyio-thread", "engine", "solver"])
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    # Stack dump records a hang instead of guessing at its cause; no task input.
    faulthandler.dump_traceback_later(10, repeat=False)
    os.environ["MCP_SOLVER_DEV"] = str(args.source)
    os.environ["PATH"] = str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", "")
    os.environ["UV_PYTHON_DOWNLOADS"] = "never"
    try:
        if args.stage == "thread":
            values = []
            worker = threading.Thread(target=lambda: values.append(42), daemon=True)
            worker.start()
            worker.join(timeout=5)
            if values != [42]:
                raise TimeoutError("basic threading failed")
            result = {"value": 42}
        else:
            result = asyncio.run(probe(args.stage))
        print(json.dumps(result))
    finally:
        faulthandler.cancel_dump_traceback_later()
