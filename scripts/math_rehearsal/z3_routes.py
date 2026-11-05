"""Self-contained synthetic route model sent to the local MCP Z3 kernel."""
import itertools
import json
import z3


def solve(matrix, demands, capacity, deadline):
    candidates = []
    for size in range(5):
        for order in itertools.permutations(range(1, 5), size):
            route = [0, *order, 5]
            cost = sum(matrix[a][b] for a, b in zip(route, route[1:]))
            if sum(demands[str(i)] for i in order) <= capacity and cost <= deadline:
                candidates.append((route, cost))
    optimizer = z3.Optimize()
    optimizer.set(timeout=5000)
    selected = [[z3.Bool(f'v{v}_r{r}') for r in range(len(candidates))] for v in range(2)]
    for row in selected:
        optimizer.add(z3.Sum([z3.If(v, 1, 0) for v in row]) == 1)
    for stop in range(1, 5):
        optimizer.add(z3.Sum([z3.If(selected[v][r], 1, 0) for v in range(2)
                             for r, (route, _) in enumerate(candidates) if stop in route[1:-1]]) == 1)
    total = z3.IntVal(0) + z3.Sum([z3.If(selected[v][r], cost, 0) for v in range(2)
                    for r, (_, cost) in enumerate(candidates)])
    goal = optimizer.minimize(total)
    state = optimizer.check()
    if state == z3.unsat:
        return {'status': 'INFEASIBLE'}
    if state != z3.sat:
        return {'status': 'UNKNOWN', 'reason': optimizer.reason_unknown()}
    solution = optimizer.model()
    low, upper = str(goal.lower()), str(goal.upper())
    return {'status': 'OPTIMAL' if low == upper else 'FEASIBLE',
            'lower': low, 'upper': upper,
            'objective': solution.eval(total).as_long(),
            'routes': [route for v in range(2) for r, (route, _) in enumerate(candidates)
                       if z3.is_true(solution.eval(selected[v][r]))]}


# Fixed synthetic fixture; kept self-contained so submit_code does not depend on host files.
matrix = [[0,2,3,8,9,10],[2,0,2,6,7,8],[3,2,0,5,6,7],
          [8,6,5,0,2,3],[9,7,6,2,0,2],[10,8,7,3,2,0]]
demands = {'1': 2, '2': 2, '3': 2, '4': 2}
print(json.dumps({name: solve(matrix, demands, cap, deadline)
                  for name, cap, deadline in [('normal',4,12),('capacity_3',3,12),('deadline_5',4,5)]}))
