from pathlib import Path
import copy
from route import Route
import numpy as np


class Solver:
    epsilon = 5e-4
    max_iterations = 100

    @classmethod
    def target_func(cls, link_flow: list[float], routes: list[Route]) -> float:
        obj = 0
        for i in range(Route.num_routes):
            x = np.linspace(0, link_flow[i], int(1e6))
            y = routes[i].brp_func(x)
            dx = x[1] - x[0]
            obj += np.round(np.sum(y * dx), 4)
        return obj

    @classmethod
    def line_search(cls, link_flow: list[float], direction: list[float], routes: list[Route]) -> (float, list[float]):
        left_bound, right_bound = 0, 1
        while True:
            beta1 = round(right_bound - 0.618 * (right_bound - left_bound), 4)
            beta2 = round(left_bound + 0.618 * (right_bound - left_bound), 4)
            flow1 = list(map(lambda x, y: round(x + beta1 * (y - x), 4), link_flow, direction))
            flow2 = list(map(lambda x, y: round(x + beta2 * (y - x), 4), link_flow, direction))
            if cls.target_func(flow1, routes) > cls.target_func(flow2, routes):
                left_bound = copy.copy(beta1)
            else:
                right_bound = copy.copy(beta2)
            dx = abs(right_bound - left_bound)
            if dx <= cls.epsilon:
                break
            else:
                pass
        return (left_bound + right_bound) / 2, list(map(lambda x, y: (x + y) / 2, flow1, flow2))

    @staticmethod
    def capacity_restriction(routes: list[Route]):
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
        iteration_process += "travel time: " + ", ".join(map(lambda x: str(round(x, 1)), travel_time)) + "\n"

        min_index = travel_time.index(min(travel_time))
        link_flow[min_index] = Route.travel_demand
        iteration_process += "link flow: " + ", ".join(map(lambda x: str(round(x, 2)), link_flow)) + "\n\n"
        avg_travel_time = list(map(lambda x, y: x + y, avg_travel_time, travel_time))
        avg_link_flow = list(map(lambda x, y: x + y, avg_link_flow, link_flow))

        temp_tau = [0] * Route.num_routes
        for counter in range(1, constant_n):
            iteration_process += f"counter = {counter}\n"
            for iRoute in range(0, Route.num_routes):
                temp_tau[iRoute] = routes[iRoute].brp_func(link_flow[iRoute])
            iteration_process += "tempt tau: " + ", ".join(map(lambda x: str(round(x, 2)), temp_tau)) + "\n"
            travel_time = list(map(lambda x, y: round(0.75 * x + 0.25 * y, 4), travel_time, temp_tau))
            iteration_process += "travel time: " + ", ".join(map(lambda x: str(round(x, 1)), travel_time)) + "\n"

            link_flow[min_index] = 0
            min_index = travel_time.index(min(travel_time))
            link_flow[min_index] = Route.travel_demand
            iteration_process += "link flow: " + ", ".join(map(lambda x: str(round(x, 2)), link_flow)) + "\n\n"
            avg_travel_time = list(map(lambda x, y: x + y, avg_travel_time, travel_time))
            avg_link_flow = list(map(lambda x, y: x + y, avg_link_flow, link_flow))

        iteration_process += "average\n"
        avg_link_flow = list(map(lambda x: x / 4, avg_link_flow))
        for iRoute in range(0, Route.num_routes):
            avg_travel_time[iRoute] = routes[iRoute].brp_func(avg_link_flow[iRoute])
        iteration_process += "link flow: " + ", ".join(map(lambda x: str(round(x, 2)), link_flow)) + "\n"
        iteration_process += "travel time: " + ", ".join(map(lambda x: str(round(x, 1)), travel_time)) + "\n"
        path = Path('../result/capacity_restriction.txt')
        path.write_text(iteration_process)

    @staticmethod
    def incremental_assignment(routes: list[Route]):
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

            iteration_process += "travel time: " + ", ".join(map(lambda x: str(round(x, 1)), travel_time)) + "\n"
            iteration_process += "link flow: " + ", ".join(map(lambda x: str(round(x, 2)), link_flow)) + "\n\n"

        for iRoute in range(0, Route.num_routes):
            travel_time[iRoute] = routes[iRoute].brp_func(link_flow[iRoute])
        iteration_process += "travel time at convergence: " + ", ".join(
            map(lambda x: str(round(x, 1)), travel_time)) + "\n"
        path = Path('../result/incremental_assignment.txt')
        path.write_text(iteration_process)

    @staticmethod
    def convex_combination(routes: list[Route]):
        obj = np.inf

        iteration_process = ""
        travel_time = [0] * Route.num_routes
        link_flow = [0] * Route.num_routes
        direction = [0] * Route.num_routes

        # Initialization. n=0
        counter = 0
        iteration_process += "counter = 0\n"
        for iRoute in range(0, Route.num_routes):
            travel_time[iRoute] = routes[iRoute].brp_func(0)
        iteration_process += "travel time: " + ", ".join(map(lambda x: str(round(x, 1)), travel_time)) + "\n"

        min_index = travel_time.index(min(travel_time))
        link_flow[min_index] = Route.travel_demand
        iteration_process += "link flow: " + ", ".join(map(lambda x: str(round(x, 2)), link_flow)) + "\n\n"

        objective_array = [np.inf]
        while counter <= Solver.max_iterations:
            counter += 1
            iteration_process += f"counter = {counter}\n"
            obj = Solver.target_func(link_flow, routes)
            objective_array.append(obj)
            iteration_process += f"target function = {obj:.2f}\n"

            for iRoute in range(0, Route.num_routes):
                travel_time[iRoute] = routes[iRoute].brp_func(link_flow[iRoute])
            iteration_process += "travel time: " + ", ".join(map(lambda x: str(round(x, 1)), travel_time)) + "\n"

            min_index = travel_time.index(min(travel_time))
            direction[min_index] = Route.travel_demand
            iteration_process += "direction: " + ", ".join(map(lambda x: str(round(x, 2)), direction)) + "\n"

            (step_size, link_flow) = Solver.line_search(link_flow, direction, routes)
            direction[min_index] = 0
            iteration_process += "link flow: " + ", ".join(map(lambda x: str(round(x, 2)), link_flow)) + "\n"
            iteration_process += f"step size: {step_size:.3f}" + "\n\n"

            if objective_array[-2] - objective_array[-1] < 10 * Solver.epsilon:
                break

        path = Path('../result/convex_combination.txt')
        path.write_text(iteration_process)
