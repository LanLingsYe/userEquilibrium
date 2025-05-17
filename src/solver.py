from src.network import NetworkManager
import copy


class Solver:
    epsilon = 5e-4
    max_iterations = 1000

    @staticmethod
    def all_or_nothing_assignment(traffic_network: NetworkManager) -> NetworkManager:
        for iLink in traffic_network.link_list:
            traffic_network.due_flow[iLink] = 0
        for iTrips in traffic_network.trips:
            optimal_sequence = traffic_network.dijkstra(iTrips[0], iTrips[1])[0]
            for iLink in optimal_sequence:
                traffic_network.due_flow[iLink] += traffic_network.trips[iTrips]
        return traffic_network

    @classmethod
    def line_search(cls, traffic_network: NetworkManager, direction: {tuple: float}) -> float:
        lower_bound, upper_bound = 0, 1
        step_size = (upper_bound - lower_bound) / 2
        median_value = 1

        flow_tmp = {kLink: traffic_network.flow[kLink] + lower_bound * direction[kLink] for kLink in direction}
        lower_value = sum(direction[kLink] * traffic_network.obtain_cost(flow_tmp)[kLink] for kLink in direction)
        flow_tmp = {kLink: traffic_network.flow[kLink] + upper_bound * direction[kLink] for kLink in direction}
        upper_value = sum(direction[kLink] * traffic_network.obtain_cost(flow_tmp)[kLink] for kLink in direction)
        while upper_bound - lower_bound > cls.epsilon and median_value > cls.epsilon:
            if lower_value * upper_value > 0:
                raise ValueError

            flow_tmp = {kLink: traffic_network.flow[kLink] + step_size * direction[kLink] for kLink in direction}
            median_value = sum(direction[kLink] * traffic_network.obtain_cost(flow_tmp)[kLink] for kLink in direction)
            if median_value * lower_value < 0:
                upper_bound = step_size
                upper_value = median_value
            else:
                lower_bound = step_size
                lower_value = median_value
            step_size = (upper_bound + lower_bound) / 2

        return step_size

    @classmethod
    def frank_wolf(cls, traffic_network: NetworkManager) -> NetworkManager:
        traffic_network.update_cost()
        traffic_network = cls.all_or_nothing_assignment(traffic_network)
        traffic_network.flow = copy.copy(traffic_network.due_flow)
        traffic_network.update_cost()
        traffic_network.update_gap()
        counter = 0

        while counter <= cls.max_iterations and traffic_network.relative_gap > cls.epsilon:
            traffic_network = cls.all_or_nothing_assignment(traffic_network)
            direction = {kLink: traffic_network.due_flow[kLink] - traffic_network.flow[kLink] for kLink in
                         traffic_network.due_flow}
            step_size = cls.line_search(traffic_network, direction)
            traffic_network.flow = {kLink: traffic_network.flow[kLink] + step_size * direction[kLink] for
                                    kLink in traffic_network.flow}
            traffic_network.update_cost()
            traffic_network.update_gap()
            counter += 1

        return traffic_network
