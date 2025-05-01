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
    travel_time = [0] * Route.num_routes
    link_flow = [0] * Route.num_routes
    avg_travel_time = [0] * Route.num_routes
    avg_link_flow = [0] * Route.num_routes

    # Initialization. n=0
    print("counter = 0")
    for iRoute in range(0, Route.num_routes):
        travel_time[iRoute] = routes[iRoute].brp_func(0)
    print("travel time: ", travel_time)

    min_index = travel_time.index(min(travel_time))
    link_flow[min_index] = Route.travel_demand
    print("link flow: ", link_flow)
    avg_travel_time = list(map(lambda x, y: x + y, avg_travel_time, travel_time))
    avg_link_flow = list(map(lambda x, y: x + y, avg_link_flow, link_flow))

    temp_tau = [0] * Route.num_routes
    for counter in range(1, 4):
        print(f"\ncounter = {counter}")
        for iRoute in range(0, Route.num_routes):
            temp_tau[iRoute] = routes[iRoute].brp_func(link_flow[iRoute])
        print("tempt tau: ", temp_tau)
        travel_time = list(map(lambda x, y: round(0.75 * x + 0.25 * y, 1), travel_time, temp_tau))
        print("travel time: ", travel_time)

        link_flow[min_index] = 0
        min_index = travel_time.index(min(travel_time))
        link_flow[min_index] = Route.travel_demand
        print("link flow: ", link_flow)
        avg_travel_time = list(map(lambda x, y: x + y, avg_travel_time, travel_time))
        avg_link_flow = list(map(lambda x, y: x + y, avg_link_flow, link_flow))

    print("\naverage")
    avg_link_flow = list(map(lambda x: x / 4, avg_link_flow))
    for iRoute in range(0, Route.num_routes):
        avg_travel_time[iRoute] = routes[iRoute].brp_func(avg_link_flow[iRoute])
    print("link flow: ", avg_link_flow)
    print("travel time: ", avg_travel_time)


def solve_ue():
    routes = data_reader()
    capacity_restriction(routes)


if __name__ == '__main__':
    solve_ue()
