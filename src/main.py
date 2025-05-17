import os
from src.network import NetworkManager
from solver import Solver

def solve_ue():
    data_dir = '..\\data'
    network_file = 'test_Network.csv'
    network_path = os.path.join(data_dir, network_file)
    OD_file = 'test_OD.csv'
    OD_path = os.path.join(data_dir, OD_file)

    traffic_network = NetworkManager()
    traffic_network.read_data(network_path, OD_path)
    traffic_network=Solver.frank_wolf(traffic_network)
    print(traffic_network.flow)

if __name__ == '__main__':
    solve_ue()
