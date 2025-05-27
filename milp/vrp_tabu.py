from vrp_clark_wright import solve_vrp_clark_wright, sum_route
from copy import deepcopy

def total_distance(distance_matrix,routes):
    total_distance = 0
    for route in routes:
        for customer in range(len(route)-1):
            total_distance += distance_matrix[route[customer]][route[customer+1]] 
        total_distance += distance_matrix[route[-2]][0]
    return total_distance
def solve_vrp_tabu(distance_matrix,demand,vehicle_capacity,max_iter,tenure):
    current_solution,best_cost= solve_vrp_clark_wright(distance_matrix,demand,vehicle_capacity) 
    best_solution = deepcopy(current_solution)
    tabu_list = {} 
    for iteration in range(max_iter):
        best_neigbor = None
        best_neighbor_cost = float("inf")
        best_exchange = None
        for route_1_index in range(len(current_solution)):
            for route_2_index in range(len(current_solution)):
                for customer_1_index in range(1,len(current_solution[route_1_index])-1):
                    for customer_2_index in range(1,len(current_solution[route_2_index])-1):

                        new_neighbor = deepcopy(current_solution)

                        new_neighbor[route_1_index][customer_1_index],new_neighbor[route_2_index][customer_2_index] = new_neighbor[route_2_index][customer_2_index], new_neighbor[route_1_index][customer_1_index]


                        in_capcity = True
                        for route in new_neighbor:
                            if sum_route(route,demand) > vehicle_capacity:
                                in_capcity = False
                                break
                        if not in_capcity:
                            continue

                        customer_1 = new_neighbor[route_1_index][customer_1_index]
                        customer_2 = new_neighbor[route_2_index][customer_2_index]
                        exchange = [customer_1,customer_2]
                        exchange.sort()
                        test_set = frozenset(exchange)

                        if test_set in tabu_list :
                            val = tabu_list[test_set]
                            if val < iteration:
                                continue

                        neighbor_cost = total_distance(distance_matrix,new_neighbor)
                        if neighbor_cost < best_neighbor_cost:
                            best_neigbor = new_neighbor
                            best_neighbor_cost = neighbor_cost
                            best_exchange = test_set 
        if best_neigbor:
            current_solution = best_neigbor
            tabu_list[best_exchange] = iteration + tenure

            if best_neighbor_cost < best_cost:
                best_solution = best_neigbor
                best_cost = best_neighbor_cost
    return best_solution,best_cost
