from pathlib import Path


class Route:
    num_routes = 0
    travel_demand = 0

    def __init__(self, free_travel_time: float, capacity: float, alpha: float, beta: float):
        self.free_travel_time = free_travel_time
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        return

    def brp_func(self, flow: float) -> float:
        travel_time = round(self.free_travel_time * (1 + self.alpha * (flow / self.capacity) ** self.beta), 1)
        return travel_time

    @classmethod
    def init_attr(cls, num_routes: int, travel_demand: float):
        cls.num_routes = num_routes
        cls.travel_demand = travel_demand
        return


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


def capacity_restriction(routes: list):
    constant_n = 4
    iteration_process = ""
    travel_time = [0] * Route.num_routes
    link_flow = [0] * Route.num_routes
    avg_travel_time = [0] * Route.num_routes
    avg_link_flow = [0] * Route.num_routes

    # Initialization. n=0
    iteration_process += "counter = 0\n"
    for iRoute in range(0, Route.num_routes):
        travel_time[iRoute] = routes[iRoute].brp_func(0)
    iteration_process += "travel time: " + ", ".join(map(str, travel_time)) + "\n"

    min_index = travel_time.index(min(travel_time))
    link_flow[min_index] = Route.travel_demand
    iteration_process += "link flow: " + ", ".join(map(str, link_flow)) + "\n\n"
    avg_travel_time = list(map(lambda x, y: x + y, avg_travel_time, travel_time))
    avg_link_flow = list(map(lambda x, y: x + y, avg_link_flow, link_flow))

    temp_tau = [0] * Route.num_routes
    for counter in range(1, constant_n):
        iteration_process += f"counter = {counter}\n"
        for iRoute in range(0, Route.num_routes):
            temp_tau[iRoute] = routes[iRoute].brp_func(link_flow[iRoute])
        iteration_process += "tempt tau: " + ", ".join(map(str, temp_tau)) + "\n"
        travel_time = list(map(lambda x, y: round(0.75 * x + 0.25 * y, 1), travel_time, temp_tau))
        iteration_process += "travel time: " + ", ".join(map(str, travel_time)) + "\n"

        link_flow[min_index] = 0
        min_index = travel_time.index(min(travel_time))
        link_flow[min_index] = Route.travel_demand
        iteration_process += "link flow: " + ", ".join(map(str, link_flow)) + "\n\n"
        avg_travel_time = list(map(lambda x, y: x + y, avg_travel_time, travel_time))
        avg_link_flow = list(map(lambda x, y: x + y, avg_link_flow, link_flow))

    iteration_process += "average\n"
    avg_link_flow = list(map(lambda x: x / 4, avg_link_flow))
    for iRoute in range(0, Route.num_routes):
        avg_travel_time[iRoute] = routes[iRoute].brp_func(avg_link_flow[iRoute])
    iteration_process += "link flow: " + ", ".join(map(str, link_flow)) + "\n"
    iteration_process += "travel time: " + ", ".join(map(str, travel_time)) + "\n"
    path = Path('../result/capacity_restriction.txt')
    path.write_text(iteration_process)


def incremental_assignment(routes: list):
    constant_n = 4
    iteration_process = ""
    portion = Route.travel_demand / constant_n
    travel_time = [0] * Route.num_routes
    link_flow = [0] * Route.num_routes

    for counter in range(1, constant_n + 1):
        iteration_process += f"counter = {counter}\n"
        for iRoute in range(0, Route.num_routes):
            travel_time[iRoute] = routes[iRoute].brp_func(link_flow[iRoute])
        min_index = travel_time.index(min(travel_time))
        link_flow[min_index] += portion

        iteration_process += "travel time: " + ", ".join(map(str, travel_time)) + "\n"
        iteration_process += "link flow: " + ", ".join(map(str, link_flow)) + "\n\n"

    for iRoute in range(0, Route.num_routes):
        travel_time[iRoute] = routes[iRoute].brp_func(link_flow[iRoute])
    iteration_process += "travel time at convergence: " + ", ".join(map(str, travel_time)) + "\n"
    path = Path('../result/incremental_assignment.txt')
    path.write_text(iteration_process)


def solve_ue():
    routes = data_reader()
    capacity_restriction(routes)
    incremental_assignment(routes)


if __name__ == '__main__':
    solve_ue()
