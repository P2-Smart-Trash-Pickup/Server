
import random
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

import math

def print_solution_google(data, manager, routing, solution,points,draw):
    """Prints solution on console."""
    total_distance = 0
    for vehicle_id in range(data["num_vehicles"]):

        if not routing.IsVehicleUsed(solution, vehicle_id):
            continue

        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        index = routing.Start(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
            new_index = manager.IndexToNode(index)

            current_point = points[node_index]
            next_point = points[new_index]

            draw.line([(current_point[0],current_point[1]),(next_point[0],next_point[1])],fill=(r,g,b))
            slope = 0
            pependicular_slope = 1
            try:
                slope = (next_point[1] - current_point[1])/(next_point[0] - current_point[0]) 
                pependicular_slope = -1/slope
            except:
                pass

            mid_width =current_point[0] + (next_point[0] - current_point[0])/2
            mid_height = current_point[1] + (next_point[1] - current_point[1])/2

            tip_width = current_point[0] + (next_point[0] - current_point[0])*0.6
            tip_height = current_point[1] + (next_point[1] - current_point[1])*0.6

            new_x_1 = mid_width + 5/math.sqrt(1+pependicular_slope**2)
            new_y_1 = mid_height + (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

            new_x_2 = mid_width - 5/math.sqrt(1+pependicular_slope**2)
            new_y_2 = mid_height - (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

            draw.polygon([(tip_width,tip_height),(new_x_1,new_y_1),(new_x_2,new_y_2)],fill=(r,g,b))
        total_distance += route_distance
    #print(f"Total distance of all routes: {total_distance}m")

def solve_vrp_google(data,points,draw,time=1):
    """Solve the CVRP problem."""
    # Instantiate the data problem.

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
    )

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Create and register a transit callback.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data["distance_matrix"][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data["demands"][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data["vehicle_capacities"],  # vehicle maximum capacities
        True,  # start cumul to zero
        "Capacity",
    )

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.FromSeconds(time)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        total_distance = 0
        for vehicle_id in range(data["num_vehicles"]):
            if not routing.IsVehicleUsed(solution,vehicle_id):
                continue
            index = routing.Start(vehicle_id)
            route_distance = 0
            while not routing.IsEnd(index):
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index,index,vehicle_id)
            total_distance += route_distance

        #print_solution_google(data, manager, routing, solution,points,draw)
        return total_distance
