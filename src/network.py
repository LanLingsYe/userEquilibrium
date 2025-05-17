import pandas as pd


class NetworkManager:
    def __init__(self):
        self.relative_gap = 1
        self.node_num = 0
        self.link_num = 0

        self.node_id = []
        self.link_list = []

        self.free_travel_time = {}
        self.alpha = {}
        self.beta = {}
        self.capacity = {}

        self.trips = {}
        self.trips_cost = {}
        self.cost = {}
        self.flow = {}
        self.due_flow = {}

    def read_data(self, network_path, OD_path) -> None:
        network = pd.read_csv(filepath_or_buffer=network_path, encoding='UTF-8')
        OD = pd.read_csv(filepath_or_buffer=OD_path, encoding='UTF-8')

        self.node_num = len(network['Init node '].unique())
        self.link_num = network.shape[0]
        self.node_id = list(
            map(int, pd.concat([network['Init node '], network['Term node ']]).drop_duplicates().tolist()))
        self.node_num = len(self.node_id)
        self.link_list = list(zip(network['Init node '], network['Term node ']))

        self.free_travel_time = dict(zip(self.link_list, network['Free Flow Time ']))
        self.beta = dict(zip(self.link_list, network['Power']))
        self.alpha = dict(zip(self.link_list, network['B']))
        self.beta = dict(zip(self.link_list, network['Power']))
        self.capacity = dict(zip(self.link_list, network['Capacity ']))

        link_tmp = list(zip(OD['O'], OD['D']))
        self.trips = dict(zip(link_tmp, OD['T']))
        self.trips_cost = dict(zip(link_tmp, [0] * len(link_tmp)))
        self.cost = dict(zip(self.link_list, [0.0] * self.link_num))
        self.flow = dict(zip(self.link_list, [0.0] * self.link_num))
        self.due_flow = dict(zip(self.link_list, [0.0] * self.link_num))

    @staticmethod
    def brp_func(flow: float, free_travel_time: float, capacity: float, alpha: float, beta: float) -> float:
        travel_time = free_travel_time * (1 + alpha * (flow / capacity) ** beta)
        return travel_time

    def dijkstra(self, init_node: int, term_node: int) -> (list, float):
        min_dist = {}
        parent_node = {}
        pending_queue = []

        for iNode in self.node_id:
            parent_node[iNode] = None
            min_dist[iNode] = float('inf')
            pending_queue.append(iNode)
        min_dist[init_node] = 0
        pending_queue.remove(init_node)
        current_node = init_node
        current_value = 0

        while term_node in pending_queue:
            for iLink, iCost in self.cost.items():
                if current_node == iLink[0] and current_value + iCost < min_dist[iLink[1]]:
                    min_dist[iLink[1]] = current_value + iCost
                    parent_node[iLink[1]] = current_node

            current_node = min(pending_queue, key=lambda link: min_dist[link])
            current_value = min_dist[current_node]
            pending_queue.remove(current_node)

        optimal_sequence = []
        node = term_node
        path_cost = min_dist[term_node]
        while parent_node[node] is not None:
            optimal_sequence.append((parent_node[node], node))
            node = parent_node[node]
        optimal_sequence.reverse()

        return optimal_sequence, path_cost

    def obtain_cost(self, flow_new) -> {tuple: float}:
        cost_new = {}
        for iLink in self.link_list:
            cost_new[iLink] = self.brp_func(flow=flow_new[iLink], free_travel_time=self.free_travel_time[iLink],
                                            capacity=self.capacity[iLink], alpha=self.alpha[iLink],
                                            beta=self.beta[iLink])
        return cost_new

    def update_cost(self) -> None:
        self.cost = self.obtain_cost(flow_new=self.flow)

    def update_trips_cost(self) -> None:
        for iTrips in self.trips_cost.keys():
            self.trips_cost[iTrips] = self.dijkstra(init_node=iTrips[0], term_node=iTrips[1])[1]

    def update_gap(self) -> None:
        upper_value, lower_value = 0, 0
        self.update_trips_cost()
        for iLink in self.link_list:
            lower_value += self.flow[iLink] * self.cost[iLink]

        for iTrip in self.trips.keys():
            upper_value += self.trips[iTrip] * self.trips_cost[iTrip]
        self.relative_gap = 1 - upper_value / lower_value
