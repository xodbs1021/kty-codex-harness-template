"""Execute seven real math libraries and an independently checked route model."""
import copy
import importlib.metadata
import itertools
import json
from pathlib import Path
import platform
import sys
import subprocess
import time

from verify_routes import exhaustive, mutation_checks, validate


def solve_routes(data, time_limit=5):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    stops = list(map(int, data['demands']))
    candidates = []
    for length in range(len(stops) + 1):
        for order in itertools.permutations(stops, length):
            if sum(data['demands'][str(i)] for i in order) > data['capacity']:
                continue
            route = [data['start'], *order, data['end']]
            cost = sum(data['matrix'][route[i]][route[i+1]] for i in range(len(route)-1))
            if cost <= data['deadline']:
                candidates.append((route, cost))
    choices = [[model.new_bool_var(f'bus_{v}_route_{r}') for r in range(len(candidates))]
               for v in range(data['vehicles'])]
    for variables in choices:
        model.add(sum(variables) == 1)
    for stop in stops:
        model.add(sum(choices[v][r] for v in range(data['vehicles'])
                      for r, (route, _) in enumerate(candidates) if stop in route[1:-1]) == 1)
    model.minimize(sum(choices[v][r] * cost for v in range(data['vehicles'])
                       for r, (_, cost) in enumerate(candidates)))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 7
    status = solver.solve(model)
    result = {'status': solver.status_name(status), 'wall_seconds': solver.wall_time,
              'candidate_count': len(candidates), 'seed': 7, 'workers': 1, 'limit_seconds': time_limit}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result.update(objective=solver.objective_value, bound=solver.best_objective_bound,
                      routes=[route for v in range(data['vehicles']) for r, (route, _) in enumerate(candidates)
                              if solver.value(choices[v][r])])
        validate(data, result['routes'], result['objective'])
    return result


def exercise_libraries():
    import sympy as sp
    import scipy.optimize
    import networkx as nx
    import cvxpy as cp
    import z3
    import highspy

    result = {}
    x = sp.Symbol('x', real=True)
    roots = sp.solve(x*x - 5*x + 6, x)
    assert roots == [2, 3] and all((x*x-5*x+6).subs(x, v) == 0 for v in roots)
    result['sympy'] = {'roots': list(map(int, roots)), 'substitution_verified': True}
    lp = scipy.optimize.linprog([-3, -2], A_ub=[[1, 1]], b_ub=[4], bounds=[(0, 2), (0, None)], method='highs')
    assert lp.success and abs(lp.fun + 10) < 1e-7
    assert all(v >= -1e-7 for v in lp.x) and sum(lp.x) <= 4+1e-7 and lp.x[0] <= 2+1e-7
    result['scipy'] = {'status': lp.message, 'x': lp.x.tolist(), 'objective': -lp.fun}
    graph = nx.DiGraph()
    graph.add_weighted_edges_from([('A','B',2),('B','C',3),('A','C',9)])
    graph.add_node('D')
    path = nx.shortest_path(graph, 'A', 'C', weight='weight')
    assert path == ['A', 'B', 'C'] and not nx.has_path(graph, 'A', 'D')
    result['networkx'] = {'path': path, 'cost': sum(graph[a][b]['weight'] for a,b in zip(path,path[1:])), 'unreachable_verified': True}
    variables = cp.Variable(2, nonneg=True)
    problem = cp.Problem(cp.Maximize(3*variables[0]+2*variables[1]), [cp.sum(variables)<=4,variables[0]<=2])
    assert problem.is_dcp()
    problem.solve(solver='HIGHS')
    assert problem.status == 'optimal' and abs(problem.value-10) < 1e-7
    assert min(variables.value)>=-1e-7 and sum(variables.value)<=4+1e-7 and variables.value[0]<=2+1e-7
    result['cvxpy'] = {'status': problem.status, 'solver': problem.solver_stats.solver_name, 'x': variables.value.tolist(), 'objective': problem.value}
    integer = z3.Int('integer')
    solver = z3.Solver()
    solver.add(integer >= 0, integer <= 2, integer > 2)
    assert solver.check() == z3.unsat
    result['z3'] = {'status': 'unsat', 'independent_reason': 'x<=2 and x>2 contradict'}
    highs = highspy.Highs()
    highs.setOptionValue('output_flag', False)
    value = highs.addVariable(lb=0, ub=2, type=highspy.HighsVarType.kInteger)
    highs.maximize(value)
    assert highs.getModelStatus() == highspy.HighsModelStatus.kOptimal
    assert abs(highs.val(value)-2)<1e-7 and abs(highs.getObjectiveValue()-2)<1e-7
    result['HiGHS'] = {'status': str(highs.getModelStatus()), 'integer': highs.val(value), 'objective': highs.getObjectiveValue()}
    return result


def main():
    started = time.monotonic()
    data = json.loads(Path(__file__).with_name('fixture.json').read_text())
    if '--routes-only' not in sys.argv:
        report = {'synthetic': True, 'python': platform.python_version(), 'platform': platform.platform(),
                  'versions': {p: importlib.metadata.version(p) for p in ['sympy','scipy','networkx','ortools','cvxpy','z3-solver','highspy']},
                  'libraries': exercise_libraries()}
        # macOS dylib names may collide when highspy and OR-Tools share a process.
        child = subprocess.run([sys.executable, '-B', __file__, '--routes-only'],
                               text=True, capture_output=True, check=True, timeout=30)
        report.update(json.loads(child.stdout))
        report['execution_isolation'] = 'OR-Tools in separate subprocess from highspy/CVXPY/SciPy'
        report['elapsed_seconds'] = time.monotonic()-started
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if len(sys.argv)>1:
            Path(sys.argv[1]).write_text(text+'\n')
        print(text)
        return
    report = {'routes': {}}
    for name, updates in [('normal', {}), ('capacity_3', {'capacity': 3}), ('deadline_5', {'deadline': 5})]:
        case = copy.deepcopy(data)
        case.update(updates)
        calculated = solve_routes(case)
        oracle = exhaustive(case)
        if oracle['best'] is None:
            assert calculated['status'] == 'INFEASIBLE', calculated
        else:
            assert calculated['status'] == 'OPTIMAL', calculated
            assert calculated['objective'] == oracle['best']['objective']
        report['routes'][name] = {'solver': calculated, 'oracle': oracle}
    assert report['routes']['normal']['solver']['objective'] == 22
    report['zero_budget'] = solve_routes(data, time_limit=0)
    assert report['zero_budget']['status'] == 'UNKNOWN'
    report['rejected_mutations'] = mutation_checks(data)
    report['elapsed_seconds'] = time.monotonic()-started
    report['passed'] = True
    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)


if __name__ == '__main__':
    main()
