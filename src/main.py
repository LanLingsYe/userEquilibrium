from pathlib import Path
from route import Route
from solver import Solver


def data_reader():
    path = Path('../data/example1.txt')
    contents = path.read_text()
    lines = [line.strip() for line in contents.split('\n') if line.strip()]

    num_routes = int(lines[0].split(': ')[1])
    travel_demand = float(lines[1].split(': ')[1])
    Route.init_attr(num_routes, travel_demand)

    routes = []
    for line in lines[3:]:
        free_travel_time, capacity, alpha, beta = map(float, line.split(', '))
        routes.append(Route(free_travel_time, capacity, alpha, beta))
    return routes


def solve_ue():
    routes = data_reader()
    Solver.capacity_restriction(routes)
    Solver.incremental_assignment(routes)
    Solver.convex_combination(routes)


if __name__ == '__main__':
    solve_ue()
