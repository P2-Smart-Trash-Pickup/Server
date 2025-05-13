from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print("SUi")
    total_distance = 0
    total_load = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = f'Route for vehicle {vehicle_id}:\n'
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += f' {node_index} Load({route_load}) -> '
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += f' {manager.IndexToNode(index)} Load({route_load})\n'
        plan_output += f'Distance of the route: {route_distance}m\n'
        plan_output += f'Load of the route: {route_load}\n'
        print(plan_output)
        total_distance += route_distance
        total_load += route_load
    print(f'Total distance of all routes: {total_distance}m')
    print(f'Total load of all routes: {total_load}')
def create_data_model():
    """Stores the data for the problem."""
    data = {}
    
    # Distance matrix (can be replaced with actual distances)
    data['distance_matrix'] = [
        [0, 548, 776, 696, 582, 274, 502, 194, 308, 194],
        [548, 0, 684, 308, 194, 502, 730, 354, 696, 742],
        [776, 684, 0, 992, 878, 502, 274, 810, 468, 742],
        [696, 308, 992, 0, 114, 650, 878, 502, 844, 890],
        [582, 194, 878, 114, 0, 536, 764, 388, 730, 776],
        [274, 502, 502, 650, 536, 0, 228, 308, 194, 240],
        [502, 730, 274, 878, 764, 228, 0, 536, 194, 468],
        [194, 354, 810, 502, 388, 308, 536, 0, 342, 388],
        [308, 696, 468, 844, 730, 194, 194, 342, 0, 274],
        [194, 742, 742, 890, 776, 240, 468, 388, 274, 0]
    ]
    
    # Pickups and deliveries (pickup index, delivery index)
    data['pickups_deliveries'] = [
        (1, 6),
        (2, 7),
        (3, 8),
        (4, 9),
    ]
    
    # Demands (positive for pickups, negative for deliveries)
    data['demands'] = [0, 1, 1, 1, 1, -1, -1, -1, -1, -1]
    
    # Vehicle capacities
    data['vehicle_capacities'] = [2, 2, 2]
    
    # Number of vehicles
    data['num_vehicles'] = 3
    
    # Depot location (start and end of routes)
    data['depot'] = 0
    
    return data
def main():
    """Solve the CVRP with pickup and delivery."""
    # Instantiate the data problem
    data = create_data_model()
    # Create the routing index manager
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'],
        data['depot']
    )
    
    # Create Routing Model
    routing = pywrapcp.RoutingModel(manager)
    
    # Create and register a transit callback
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]
    
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    
    # Define cost of each arc
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # Add Capacity constraint
    def demand_callback(from_index):
        """Returns the demand of the node."""
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]
    
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    dimension_name = "Capacity"
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        dimension_name
    )

    capacity_dimension = routing.GetDimensionOrDie(dimension_name)
    
    # Add Pickup and Delivery constraints
    for pickup, delivery in data['pickups_deliveries']:
        pickup_index = manager.NodeToIndex(pickup)
        delivery_index = manager.NodeToIndex(delivery)
        routing.AddPickupAndDelivery(pickup_index, delivery_index)
        routing.solver().Add(
            routing.VehicleVar(pickup_index) == routing.VehicleVar(delivery_index))
        routing.solver().Add(
            capacity_dimension.CumulVar(pickup_index ) <= 
            capacity_dimension.CumulVar(delivery_index))
   
    # Setting first solution heuristic
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH)
    search_parameters.time_limit.FromSeconds(60)

    # Solve the problem
    solution = routing.SolveWithParameters(search_parameters)
    
    # Print solution on console
    if solution:
        print_solution(data, manager, routing, solution)
    else:
        print("No solution found!")
if __name__ == '__main__':
    main()
