"""Real stdio MCP calls; preserve results before checking their semantics."""
import argparse
import ast
import asyncio
import copy
from datetime import timedelta
import json
import os
import sys
from pathlib import Path
import time

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from verify_routes import exhaustive, validate


def payload(result):
    if result.isError:
        raise AssertionError(result.model_dump(mode='json'))
    if result.structuredContent is not None:
        return result.structuredContent
    text = '\n'.join(c.text for c in result.content if c.type == 'text')
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


async def run(name, base):
    evidence = base / 'evidence'
    executable = base / 'venv/bin' / name
    if name == 'mcp-optimizer':
        executable = base / 'venv-optimizer/bin/mcp-optimizer'
    if name == 'mcp-solver':
        executable = base / 'sources/mcp-solver/.venv/bin/mcp-solver-serve'
    args = ['--transport', 'stdio'] if name == 'mcp-optimizer' else []
    env = {key: os.environ[key] for key in ['PATH','HOME','TMPDIR','LANG'] if key in os.environ}
    env['MCP_SOLVER_DEV'] = str(base / 'sources/mcp-solver')
    record = {'server': name, 'transport': 'stdio', 'command': str(executable),
              'args': args, 'calls': [], 'initialized': False, 'checks': {}}
    started = time.monotonic()

    def save():
        (evidence / (name+'-calls.json')).write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n')

    try:
        with (evidence / (name+'-calls.stderr')).open('w') as err:
            params = StdioServerParameters(command=str(executable),args=args,env=env,cwd=str(base))
            async with asyncio.timeout(240):
                async with stdio_client(params, errlog=err) as (read, write):
                    async with ClientSession(read,write,read_timeout_seconds=timedelta(seconds=180)) as session:
                        record['initialize'] = (await session.initialize()).model_dump(mode='json')
                        record['initialized'] = True
                        record['tools'] = [t.name for t in (await session.list_tools()).tools]
                        save()

                        async def call(tool, arguments):
                            response = await session.call_tool(tool, arguments)
                            record['calls'].append({'tool':tool,'arguments':arguments,'result':response.model_dump(mode='json')})
                            save()
                            return payload(response)

                        if name == 'mcp-sympy':
                            result = await call('sympy_solve', {'equation':'x**2-5*x+6','variables':'x'})
                            # FastMCP versions may wrap a scalar under result.
                            if isinstance(result, dict) and 'result' in result:
                                result = result['result']
                            roots = ast.literal_eval(result) if isinstance(result,str) else result
                            assert sorted(roots)==[2,3] and all(x*x-5*x+6==0 for x in roots)
                            record['checks']['equation_substitution'] = True
                        elif name == 'mcp-optimizer':
                            lp = await call('solve_linear_program_tool', {
                                'objective':{'sense':'maximize','coefficients':{'x':3,'y':2}},
                                'variables':{'x':{'type':'continuous','lower':0,'upper':2},'y':{'type':'continuous','lower':0}},
                                'constraints':[{'expression':{'x':1,'y':1},'operator':'<=','rhs':4}],
                                'time_limit_seconds':5})
                            record['checks']['lp_response'] = lp
                            assert lp['status'] == 'optimal', lp
                            x, y = lp['variables']['x'], lp['variables']['y']
                            assert 0 <= x <= 2 and y >= 0 and x+y <= 4+1e-7
                            assert abs(3*x+2*y-10)<1e-7 and abs(lp['objective_value']-10)<1e-7
                            record['checks']['lp_independently_verified'] = True
                            # Restrict the routing test to exactly stated endpoints/time conditions.
                            request = {'locations':[{'name':'depot','demand':0},{'name':'A','demand':2},{'name':'B','demand':2}],
                                       'vehicles':[{'capacity':4}], 'distance_matrix':[[0,2,2],[2,0,1],[2,1,0]],
                                       'time_matrix':[[0,2,2],[2,0,1],[2,1,0]],'depot':0,'time_limit_seconds':1}
                            normal = await call('solve_vehicle_routing_problem', request)
                            record['checks']['closed_route_response'] = normal
                            nodes = [[s['index'] for s in r['route']] for r in normal['variables']['routes']]
                            closed_data = {'vehicles':1,'start':0,'end':0,'demands':{'1':2,'2':2},
                                           'matrix':request['distance_matrix'],'capacity':4,'deadline':100}
                            validate(closed_data,nodes,normal['objective_value'])
                            # Both possible visit orders cost 5; small independent optimality check.
                            assert normal['objective_value']==5
                            record['checks']['closed_route_independently_verified'] = True
                            tight = copy.deepcopy(request)
                            tight['vehicles'][0]['max_time'] = 1
                            bad = await call('solve_vehicle_routing_problem', tight)
                            record['checks']['max_time_1_response'] = bad
                            endpoint = copy.deepcopy(request)
                            endpoint['vehicles'][0]['end_location'] = 2
                            end_result = await call('solve_vehicle_routing_problem', endpoint)
                            record['checks']['end_location_2_response'] = end_result
                            # Record observed violations, never convert the server's optimal label into proof.
                            for label, result in [('max_time',bad),('end_location',end_result)]:
                                routes = result.get('variables',{}).get('routes',[])
                                if routes:
                                    nodes = [s['index'] for s in routes[0]['route']]
                                    duration = sum(request['time_matrix'][a][b] for a,b in zip(nodes,nodes[1:]))
                                    record['checks'][label+'_violation_observed'] = (duration>1 if label=='max_time' else nodes[-1]!=2)
                            assert record['checks'].get('max_time_violation_observed') is True
                            assert record['checks'].get('end_location_violation_observed') is True
                            record['semantic_acceptance'] = False
                            record['rejection_reason'] = 'Returned route violates max_time and end_location in separate counterexamples'
                        else:
                            await call('select_backend', {'solver':'z3'})
                            code = Path(__file__).with_name('z3_routes.py').read_text()
                            execution = await call('python_exec', {'code':code,'timeout':30})
                            record['checks']['kernel_execution'] = execution
                            save()
                            assert isinstance(execution,dict) and execution.get('success') is True, execution
                            output = execution.get('output',execution.get('stdout',''))
                            results = json.loads(output.strip())
                            data = json.loads(Path(__file__).with_name('fixture.json').read_text())
                            for case, updates in [('normal',{}),('capacity_3',{'capacity':3}),('deadline_5',{'deadline':5})]:
                                scenario = dict(data,**updates)
                                oracle = exhaustive(scenario)
                                answer = results[case]
                                if oracle['best'] is None:
                                    assert answer['status']=='INFEASIBLE'
                                else:
                                    validate(scenario, answer['routes'],answer['objective'])
                                    assert answer['status']=='OPTIMAL' and answer['objective']==oracle['best']['objective']
                            record['checks']['routes_and_oracle'] = True
                            submitted = await call('submit_code', {'code':code})
                            assert submitted.get('ok') is True, submitted
                            record['checks']['submission_compile_checked'] = True
            record['closed'] = True
            record['probe_completed'] = True
            if name != 'mcp-optimizer':
                record['semantic_acceptance'] = True
    except Exception as error:
        record['error'] = repr(error)
    record['elapsed_seconds'] = time.monotonic()-started
    save()
    print(name, 'calls=',len(record['calls']),'closed=',record.get('closed'), 'error=',record.get('error',''))
    return record


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('base', type=Path)
    parser.add_argument('server',choices=['mcp-sympy','mcp-optimizer','mcp-solver'])
    options=parser.parse_args()
    result = asyncio.run(run(options.server,options.base.resolve()))
    sys.exit(0 if result.get('probe_completed') else 1)
