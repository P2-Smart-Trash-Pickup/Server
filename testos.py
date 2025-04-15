#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Copyright 2015 Tin Arm Engineering AB
# Copyright 2018 Google LLC
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Capacitated Vehicle Routing Problem (CVRP).

This is a sample using the routing library python wrapper to solve a CVRP
problem while allowing multiple trips, i.e., vehicles can return to a depot
to reset their load ("reload").

A description of the CVRP problem can be found here:
http://en.wikipedia.org/wiki/Vehicle_routing_problem.

Distances are in meters.

In order to implement multiple trips, new nodes are introduced at the same
locations of the original depots. These additional nodes can be dropped
from the schedule at 0 cost.

The max_slack parameter associated to the capacity constraints of all nodes
can be set to be the maximum of the vehicles' capacities, rather than 0 like
in a traditional CVRP. Slack is required since before a solution is found,
it is not known how much capacity will be transferred at the new nodes. For
all the other (original) nodes, the slack is then re-set to 0.

The above two considerations are implemented in `add_capacity_constraints()`.

Last, it is useful to set a large distance between the initial depot and the
new nodes introduced, to avoid schedules having spurious transits through
those new nodes unless it's necessary to reload. This consideration is taken
into account in `create_distance_evaluator()`.
"""

from functools import partial

from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2


###########################
# Problem Data Definition #
###########################
def create_data_model():
    """Stores the data for the problem"""
    data = {}
    _capacity =9  
    # Locations in block unit
    _locations = [
        (4, 4),  # depot
        (4, 4),  # unload depot_first
        (4, 4),  # unload depot_second
        (4, 4),  # unload depot_third
        (4, 4),  # unload depot_fourth
        (4, 4),  # unload depot_fifth
        (2, 0),
        (8, 0),  # locations to visit
        (0, 1),
        (1, 1),
        (5, 2),
        (7, 2),
        (3, 3),
        (6, 3),
        (5, 5),
        (8, 5),
        (1, 6),
        (2, 6),
        (3, 7),
        (6, 7),
        (0, 8),
        (7, 8),    
    ]
    # Compute locations in meters using the block dimension defined as follow
    # Manhattan average block: 750ft x 264ft -> 228m x 80m
    # here we use: 114m x 80m city block
    # src: https://nyti.ms/2GDoRIe 'NY Times: Know Your distance'
    data["locations"] = [(l[0] * 114, l[1] * 80) for l in _locations]
    data["num_locations"] = len(data["locations"])
    data["demands"] = [
        0,  # depot
        -_capacity,  # unload depot_first
        -_capacity,  # unload depot_second
        -_capacity,  # unload depot_third
        -_capacity,  # unload depot_fourth
        -_capacity,  # unload depot_fifth
        1,
        1,  # 1, 2
        1,
        1,  # 3, 4
        1,
        1,  # 5, 6
        1,
        1,  # 7, 8
        1,
        1,  # 9,10
        1,
        1,  # 11,12
        1,
        1,  # 13, 14
        1,
        1,
    ]  # 15, 16
    data["num_vehicles"] = 3
    data["vehicle_capacity"] = _capacity
    data["vehicle_max_distance"] = 10_000
    data["depot"] = 0
    return data


#######################
# Problem Constraints #
#######################
def manhattan_distance(position_1, position_2):
    """Computes the Manhattan distance between two points"""
    return abs(position_1[0] - position_2[0]) + abs(position_1[1] - position_2[1])


def create_distance_evaluator(data):
    """Creates callback to return distance between points."""
    _distances = {}
    # precompute distance between location to have distance callback in O(1)
    for from_node in range(data["num_locations"]):
        _distances[from_node] = {}
        for to_node in range(data["num_locations"]):
            if from_node == to_node:
                _distances[from_node][to_node] = 0
            # Forbid start/end/reload node to be consecutive.
            elif from_node in range(6) and to_node in range(6):
                _distances[from_node][to_node] = data["vehicle_max_distance"]
            else:
                _distances[from_node][to_node] = manhattan_distance(
                    data["locations"][from_node], data["locations"][to_node]
                )

    def distance_evaluator(manager, from_node, to_node):
        """Returns the manhattan distance between the two nodes"""
        return _distances[manager.IndexToNode(from_node)][manager.IndexToNode(to_node)]

    return distance_evaluator


def add_distance_dimension(routing, manager, data, distance_evaluator_index):
    """Add Global Span constraint"""
    del manager
    distance = "Distance"
    routing.AddDimension(
        distance_evaluator_index,
        0,  # null slack
        data["vehicle_max_distance"],  # maximum distance per vehicle
        True,  # start cumul to zero
        distance,
    )
    distance_dimension = routing.GetDimensionOrDie(distance)
    # Try to minimize the max distance among vehicles.
    # /!\ It doesn't mean the standard deviation is minimized
    distance_dimension.SetGlobalSpanCostCoefficient(100)


def create_demand_evaluator(data):
    """Creates callback to get demands at each location."""
    _demands = data["demands"]

    def demand_evaluator(manager, from_node):
        """Returns the demand of the current node"""
        return _demands[manager.IndexToNode(from_node)]

    return demand_evaluator


def add_capacity_constraints(routing, manager, data, demand_evaluator_index):
    """Adds capacity constraint"""
    vehicle_capacity = data["vehicle_capacity"]
    capacity = "Capacity"
    routing.AddDimension(
        demand_evaluator_index,
        vehicle_capacity,
        vehicle_capacity,
        True,  # start cumul to zero
        capacity,
    )

    # Add Slack for reseting to zero unload depot nodes.
    # e.g. vehicle with load 10/15 arrives at node 1 (depot unload)
    # so we have CumulVar = 10(current load) + -15(unload) + 5(slack) = 0.
    capacity_dimension = routing.GetDimensionOrDie(capacity)
    # Allow to drop reloading nodes with zero cost.
    for node in [1, 2, 3, 4, 5]:
        node_index = manager.NodeToIndex(node)
        routing.AddDisjunction([node_index], 0)

    # Allow to drop regular node with a cost.
    for node in range(6, len(data["demands"])):
        node_index = manager.NodeToIndex(node)
        capacity_dimension.SlackVar(node_index).SetValue(0)
        routing.AddDisjunction([node_index], 100_000)





###########
# Printer #
###########
def print_solution(
    data, manager, routing, assignment
):  # pylint:disable=too-many-locals
    """Prints assignment on console"""
    print(f"Objective: {assignment.ObjectiveValue()}")
    total_distance = 0
    total_load = 0
    capacity_dimension = routing.GetDimensionOrDie("Capacity")
    distance_dimension = routing.GetDimensionOrDie("Distance")
    dropped = []
    for order in range(6, routing.nodes()):
        index = manager.NodeToIndex(order)
        if assignment.Value(routing.NextVar(index)) == index:
            dropped.append(order)
    print(f"dropped orders: {dropped}")
    dropped = []
    for reload in range(1, 6):
        index = manager.NodeToIndex(reload)
        if assignment.Value(routing.NextVar(index)) == index:
            dropped.append(reload)
    print(f"dropped reload stations: {dropped}")

    for vehicle_id in range(data["num_vehicles"]):
        if not routing.IsVehicleUsed(assignment, vehicle_id):
            continue
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        load_value = 0
        distance = 0
        while not routing.IsEnd(index):
            plan_output += (
                f" {manager.IndexToNode(index)} "
                f"Load({assignment.Min(capacity_dimension.CumulVar(index))}) -> "
            )
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            distance += distance_dimension.GetTransitValue(previous_index, index, vehicle_id)
            # capacity dimension TransitVar is negative at reload stations during replenishment
            # don't want to consider those values when calculating the total load of the route
            # hence only considering the positive values
            load_value += max(0, capacity_dimension.GetTransitValue(previous_index, index, vehicle_id))
        plan_output += (
            f" {manager.IndexToNode(index)} "
            f"Load({assignment.Min(capacity_dimension.CumulVar(index))}) -> "
        )
        plan_output += f"Distance of the route: {distance}m\n"
        plan_output += f"Load of the route: {load_value}\n"
        print(plan_output)
        total_distance += distance
        total_load += load_value
    print(f"Total Distance of all routes: {total_distance}m")
    print(f"Total Load of all routes: {total_load}")


########
# Main #
########
def main():
    """Entry point of the program"""
    # Instantiate the data problem.
    data = create_data_model()

    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        data["num_locations"], data["num_vehicles"], data["depot"]
    )

    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)

    # Define weight of each edge
    distance_evaluator_index = routing.RegisterTransitCallback(
        partial(create_distance_evaluator(data), manager)
    )
    routing.SetArcCostEvaluatorOfAllVehicles(distance_evaluator_index)

    # Add Distance constraint to minimize the longuest route
    add_distance_dimension(routing, manager, data, distance_evaluator_index)

    # Add Capacity constraint
    demand_evaluator_index = routing.RegisterUnaryTransitCallback(
        partial(create_demand_evaluator(data), manager)
    )
    add_capacity_constraints(routing, manager, data, demand_evaluator_index)

    # Setting first solution heuristic (cheapest addition).
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )  # pylint: disable=no-member
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(3)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("No solution found !")


if __name__ == "__main__":
    main()
