class Example1:
    def __init__(self):
        self.num_of_route = 3
        self.sum_travel_demand=10

    @staticmethod
    def first_performance_func(self, flow: float):
        travel_time = 10 * (1 + 0.15 * (flow / 2) ** 4)
        return travel_time

    @staticmethod
    def second_performance_func(self, flow: float):
        travel_time = 20 * (1 + 0.15 * (flow / 4) ** 4)
        return travel_time

    @staticmethod
    def third_performance_func(self, flow: float):
        travel_time = 25 * (1 + 0.15 * (flow / 3) ** 4)
        return travel_time
