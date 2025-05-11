import numpy as np
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
        travel_time = np.round(self.free_travel_time * (1 + self.alpha * (flow / self.capacity) ** self.beta), 4)
        return travel_time

    @classmethod
    def init_attr(cls, num_routes: int, travel_demand: float):
        cls.num_routes = num_routes
        cls.travel_demand = travel_demand
        return
