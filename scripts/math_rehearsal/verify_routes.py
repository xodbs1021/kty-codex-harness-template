"""Independent standard-library route checker and exhaustive oracle."""
import itertools
import math


def validate(data, routes, objective):
    """Reject malformed solutions and recompute all task invariants."""
    if len(routes) != data['vehicles']:
        raise ValueError('vehicle count')
    seen = []
    total = 0
    for route in routes:
        if len(route) < 2 or route[0] != data['start'] or route[-1] != data['end']:
            raise ValueError('endpoints')
        if any(type(node) is not int or str(node) not in data['demands'] for node in route[1:-1]):
            raise ValueError('stop identity')
        seen.extend(route[1:-1])
        load = sum(data['demands'][str(node)] for node in route[1:-1])
        if load > data['capacity']:
            raise ValueError('capacity')
        duration = 0
        for index in range(len(route) - 1):
            duration += data['matrix'][route[index]][route[index + 1]]
        if duration > data['deadline']:
            raise ValueError('deadline')
        total += duration
    if sorted(seen) != sorted(map(int, data['demands'])):
        raise ValueError('coverage')
    if not math.isfinite(objective) or abs(total - objective) > 1e-8:
        raise ValueError('objective')
    return total


def exhaustive(data):
    """Enumerate assignments/order independently from solver candidate generation."""
    if data['vehicles'] != 2:
        raise ValueError('oracle is limited to two vehicles')
    best = None
    examined = 0
    feasible = 0
    for order in itertools.permutations(map(int, data['demands'])):
        for split in range(len(order) + 1):
            examined += 1
            routes = [[data['start'], *order[:split], data['end']],
                      [data['start'], *order[split:], data['end']]]
            # Compute independently of the solver's candidate cost function.
            objective = sum(data['matrix'][a][b] for route in routes for a, b in zip(route, route[1:]))
            try:
                validate(data, routes, objective)
            except ValueError:
                continue
            feasible += 1
            if best is None or objective < best['objective']:
                best = {'routes': routes, 'objective': objective}
    return {'examined': examined, 'feasible': feasible, 'best': best}


def mutation_checks(data):
    """Verify the checker rejects known bad outputs, not just solver successes."""
    cases = {
        'missing': ([[0, 1, 3, 5], [0, 2, 5]], 21),
        'duplicate': ([[0, 1, 3, 5], [0, 1, 4, 5]], 22),
        'capacity': ([[0, 1, 2, 3, 5], [0, 4, 5]], 23),
        'late': ([[0, 2, 1, 5], [0, 3, 4, 5]], 25),
        'objective': ([[0, 1, 3, 5], [0, 2, 4, 5]], 21),
        'endpoint': ([[5, 1, 3, 5], [0, 2, 4, 5]], 22),
    }
    rejected = {}
    for name, (routes, objective) in cases.items():
        try:
            validate(data, routes, objective)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise AssertionError(f'checker accepted {name}')
    return rejected
