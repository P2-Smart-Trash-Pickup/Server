from copy import deepcopy
import json
import time
from milp.gen_data import generate_distance_matrix,gen_data_or
from milp.vrp_tabu_optimized import near_neighbor_gen, sum_distance 
from milp.vrp_or import solve_vrp_google
from tqdm import tqdm
from PIL import Image,ImageDraw

def get_penalty(i:int,j:int,distance_matrix:list[list[int]],penalty_matrix:list[list[int]],penalty:float) -> float:
    org_distance = distance_matrix[i][j]
    return org_distance + penalty*penalty_matrix[i][j]*org_distance

def sum_demands(route:list[int],demands:list[float]) -> float:
    return sum([demands[i] for i in route])
def two_op(route:list[int],_:list[int],distance_matrix:list[list[int]],penalty_matrix:list[list[int]],penalty:float) -> tuple[float,int,int]:
    best_delta = 0

    best_i = 0 
    best_j = 0 
    
    for i in range(1,len(route)-2):
        for j in range(i+1,len(route)-1):
            point_i = route[i]
            point_i_p = route[i+1]
            point_j = route[j]
            point_j_p = route[j+1]

            old_edge_i = get_penalty(point_i,point_i_p,distance_matrix,penalty_matrix,penalty)
            old_edge_j = get_penalty(point_j,point_j_p,distance_matrix,penalty_matrix,penalty)

            new_edge_ij = get_penalty(point_i,point_j,distance_matrix,penalty_matrix,penalty)

            new_edge_ij_plus = get_penalty(point_i_p,point_j_p,distance_matrix,penalty_matrix,penalty)

            delta_cost = (new_edge_ij+new_edge_ij_plus) - (old_edge_i+old_edge_j)

            if delta_cost < best_delta:
                best_i = i
                best_j = j
                best_delta = delta_cost

    return best_delta,best_i,best_j


def relocate(route_1:list[int],route_2:list[int],distance_matrix:list[list[int]],penalty_matrix:list[list[int]],penalty:float) -> tuple[float,int,int]:


    customers_1 = route_1[1:-1]
    best_improvement = 0
    best_best_k = 0 
    best_best_i = 0 
    for k in range(len(customers_1)):

        customers_1 = route_1[1:-1]
        best_insertion = float("inf")
        best_k = 0 
        best_i = 0 
        for i in range(len(route_2)-1):
            point_k = customers_1[k]
            point_i = route_2[i] 
            point_j = route_2[i+1] 

            distance_i_k = get_penalty(point_i,point_k,distance_matrix,penalty_matrix,penalty) 

            distance_k_j = get_penalty(point_k,point_j,distance_matrix,penalty_matrix,penalty) 

            distance_i_j = get_penalty(point_i,point_j,distance_matrix,penalty_matrix,penalty) 

            insertion_saving = distance_i_k + distance_k_j - distance_i_j 
            if insertion_saving < best_insertion:
                best_insertion = insertion_saving
                best_k = k+1
                best_i = i+1
        if best_insertion >= float("inf"):
            continue

        pre_cost = get_penalty(route_1[best_k-1],route_1[best_k],distance_matrix,penalty_matrix,penalty) + get_penalty(route_1[best_k],route_1[best_k+1],distance_matrix,penalty_matrix,penalty) 
        
        pre_cost_2 = get_penalty(route_2[best_i-1],route_2[best_i],distance_matrix,penalty_matrix,penalty) 

        sum_pre_cost = pre_cost + pre_cost_2

        new_cost = get_penalty(route_1[best_k-1],route_1[best_k+1],distance_matrix,penalty_matrix,penalty) + get_penalty(route_2[best_i-1],route_1[best_k],distance_matrix,penalty_matrix,penalty) + get_penalty(route_1[best_k],route_2[best_i],distance_matrix,penalty_matrix,penalty) 

        split_diff = new_cost - sum_pre_cost


        if split_diff< best_improvement:
            best_improvement =split_diff 
            best_best_k = best_k 
            best_best_i = best_i 
    return best_improvement,best_best_k,best_best_i

def exchange(route_1:list[int],route_2:list[int],distance_matrix:list[list[int]],penalty_matrix:list[list[int]],penalty:float) -> tuple[float,int,int]:

    best_best_improvement = 0
    best_best_i = 0
    best_best_j = 0
    for i in range(1,len(route_1)-1):
        pre_point_i = route_1[i-1]
        current_point_i = route_1[i]
        next_point_i = route_1[i+1]

        old_cost_i = get_penalty(pre_point_i,current_point_i,distance_matrix,penalty_matrix,penalty) + get_penalty(current_point_i,next_point_i,distance_matrix,penalty_matrix,penalty) 
        best_improvement = 0
        best_i = 0
        best_j = 0
        for j in range(1,len(route_2)-1): 
            pre_point_j = route_2[j-1]
            current_point_j = route_2[j]
            next_point_j = route_2[j+1]

            old_cost_j = get_penalty(pre_point_j,current_point_j,distance_matrix,penalty_matrix,penalty) + get_penalty(current_point_j,next_point_j,distance_matrix,penalty_matrix,penalty) 

            new_cost_1 = get_penalty(pre_point_i,current_point_j,distance_matrix,penalty_matrix,penalty) + get_penalty(current_point_j,next_point_i,distance_matrix,penalty_matrix,penalty) 

            new_cost_2 = get_penalty(pre_point_j,current_point_i,distance_matrix,penalty_matrix,penalty) + get_penalty(current_point_i,next_point_j,distance_matrix,penalty_matrix,penalty) 

            old_cost = old_cost_i + old_cost_j
            new_cost = new_cost_2 + new_cost_1

            improvement = new_cost - old_cost
            if improvement < best_improvement:
                best_improvement = improvement
                best_i = i
                best_j = j
        if best_improvement < best_best_improvement:
            best_best_improvement = best_improvement
            best_best_i = best_i
            best_best_j = best_j
    return best_best_improvement, best_best_i, best_best_j

def cross(route_1:list[int],route_2:list[int],distance_matrix:list[list[int]],penalty_matrix:list[list[int]],penalty:float) -> tuple[float,int,int]:

    best_best_improvement = 0
    best_best_i = 0
    best_best_j = 0
    for i in range(len(route_1)-1):
        current_point_i = route_1[i]
        next_point_i = route_1[i+1]

        old_cost_i = get_penalty(current_point_i,next_point_i,distance_matrix,penalty_matrix,penalty)
        best_improvement = 0
        best_i = 0
        best_j = 0
        for j in range(len(route_2)-1): 
            current_point_j = route_2[j]
            next_point_j = route_2[j+1]

            old_cost_j = get_penalty(current_point_j,next_point_j,distance_matrix,penalty_matrix,penalty) 

            new_cost_1 = get_penalty(current_point_j,next_point_i,distance_matrix,penalty_matrix,penalty) 

            new_cost_2 = get_penalty(current_point_i,next_point_j,distance_matrix,penalty_matrix,penalty) 

            old_cost = old_cost_i + old_cost_j
            new_cost = new_cost_2 + new_cost_1


            improvement = new_cost - old_cost
            if improvement < best_improvement:
                best_improvement = improvement
                best_i = i
                best_j = j
        if best_improvement < best_best_improvement:
            best_best_improvement = best_improvement
            best_best_i = best_i
            best_best_j = best_j
    return best_best_improvement, best_best_i, best_best_j

def implement_2_opt(routes:list[list[int]],chosen_i:int,chosen_j:int,route1_idx:int,_:int):
    route = routes[route1_idx]
    route = route[:chosen_i+1] + route[chosen_i+1:chosen_j+1][::-1] + route[chosen_j+1:]
    routes[route1_idx] = route

    return routes

def implement_relocate(routes:list[list[int]],chosen_i:int,chosen_j:int,route1_idx:int,route2_idx:int):
    out_point = routes[route1_idx].pop(chosen_i)
    routes[route2_idx].insert(chosen_j,out_point)

    return routes

def implement_exchange(routes:list[list[int]],chosen_i:int,chosen_j:int,route1_idx:int,route2_idx:int):
    route1 = routes[route1_idx]
    route2 = routes[route2_idx]
    route1[chosen_i],route2[chosen_j] = route2[chosen_j],route1[chosen_i]
    routes[route1_idx] = route1
    routes[route2_idx] = route2

    return routes

def implement_cross(routes:list[list[int]],chosen_i:int,chosen_j:int,route1_idx:int,route2_idx:int):
    route1 = routes[route1_idx]
    route2 = routes[route2_idx]
    route1[chosen_i+1:],route2[chosen_j+1:] = route2[chosen_j+1:],route1[chosen_i+1:]
    routes[route1_idx] = route1
    routes[route2_idx] = route2

    return routes


def pass_constraints_2_opt(_routes:list[list[int]],_chosen_i:int,_chosen_j:int,_route1_idx:int,_:int,_demands:list[float],_vehicle_capacity:float):
    return True 

def pass_constraints_relocate(routes:list[list[int]],chosen_i:int,_:int,route1_idx:int,route2_idx:int,demands:list[float],vehicle_capacity:float):
    route1 = routes[route1_idx]
    route2 = routes[route2_idx]

    route_1_demand = sum_demands(route1,demands)
    route_2_demand = sum_demands(route2,demands)

    point_1_demand = demands[route1[chosen_i]]

    if (route_1_demand - point_1_demand ) > vehicle_capacity or (route_2_demand + point_1_demand) > vehicle_capacity:
        return False
    return True

def pass_constraints_exchange(routes:list[list[int]],chosen_i:int,chosen_j:int,route1_idx:int,route2_idx:int,demands:list[float],vehicle_capacity:float):
    route1 = routes[route1_idx]
    route2 = routes[route2_idx]

    route_1_demand = sum_demands(route1,demands)
    route_2_demand = sum_demands(route2,demands)

    point_1_demand = demands[route1[chosen_i]]
    point_2_demand = demands[route2[chosen_j]]

    if (route_1_demand - point_1_demand + point_2_demand) > vehicle_capacity or (route_2_demand - point_2_demand + point_1_demand) > vehicle_capacity:
        return False
    return True

def pass_constraints_cross(routes:list[list[int]],chosen_i:int,chosen_j:int,route1_idx:int,route2_idx:int,demands:list[float],vehicle_capacity:float):
    route1 = routes[route1_idx]
    route2 = routes[route2_idx]

    route_1_demand = sum_demands(route1,demands)
    route_2_demand = sum_demands(route2,demands)

    point_1_demand = sum_demands(route1[chosen_i+1:],demands) 
    point_2_demand = sum_demands(route2[chosen_j+1:],demands) 

    if (route_1_demand - point_1_demand + point_2_demand) > vehicle_capacity or (route_2_demand - point_2_demand + point_1_demand) > vehicle_capacity:
        return False
    return True

def get_best_heurestic_move(routes:list[list[int]],distance_matrix:list[list[int]],penalty_matrix:list[list[int]],demands:list[float],vehicle_capacity:float,penalty:float,heurestic,pass_function) -> tuple[int,int,int,int,int]:

    best_improvement = 0
    chosen_k = 0 
    chosen_i = 0
    route1_idx = 0
    route2_idx = 0
    for route_idx in range(len(routes)):
        for route_idx2 in range(len(routes)):
            if route_idx == route_idx2:
                continue
            route_1 = routes[route_idx]

            route_2 = routes[route_idx2]

            improvement,k,i= heurestic(route_1,route_2,distance_matrix,penalty_matrix,penalty)
            if improvement < best_improvement:

                if not pass_function(routes,k,i,route_idx,route_idx2,demands,vehicle_capacity):
                    continue
                best_improvement = improvement
                chosen_k = k
                chosen_i = i
                route1_idx = route_idx
                route2_idx = route_idx2

    return best_improvement,chosen_k,chosen_i,route1_idx,route2_idx

def local_search(routes:list[list[int]],distance_matrix:list[list[int]],penalty_matrix:list[list[int]],demands:list[float],vehicle_capacity:float,penalty:float,heurestics):

    best_improvement = 0
    best_heu = heurestics[0][1] 
    best_i = 0
    best_j = 0
    best_1 = 0
    best_2 = 0

    for heurestic in heurestics:
        improvement,chosen_i,chosen_j,route1_idx,route2_idx = get_best_heurestic_move(routes,distance_matrix,penalty_matrix,demands,vehicle_capacity,penalty,heurestic[0],heurestic[2])
        if improvement< best_improvement:
            best_improvement = improvement
            best_heu = heurestic[1]
            best_i = chosen_i
            best_j = chosen_j
            best_1 = route1_idx
            best_2 = route2_idx
        #improvements.append((improvement,lambda :heurestic[1](routes,chosen_i,chosen_j,route1_idx,route2_idx)))
    if best_improvement < 0:
        best_heu(routes,best_i,best_j,best_1,best_2)

def find_penalty_feature(routes:list[list[int]],distance_matrix:list[list[int]],penalty_matrix:list[list[int]]) -> list[tuple[int,int]]:
    worst_ratio = 0
    worst_features = []
    for route_idx in range(len(routes)):
        route = routes[route_idx]
        for i in range(len(route)-1):
            point = route[i]
            next_point = route[i+1]
            penalty_amount = penalty_matrix[point][next_point]
            distance = distance_matrix[point][next_point]

            ratio = distance/(penalty_amount+1)

            if ratio == worst_ratio:
                worst_features.append((point,next_point))
            elif ratio > worst_ratio:
                worst_ratio = ratio
                worst_features = [(point,next_point)]

    return worst_features

def gls(initial_solution:list[list[int]],distance_matrix:list[list[int]],penalty_matrix:list[list[int]],penalty:float,demands:list[float],vehicle_capacity:float,max_iter:int,time_limit:int|None=None):
    no_penalty = deepcopy(penalty_matrix)
    heurestics = [(two_op,implement_2_opt,pass_constraints_2_opt),(relocate,implement_relocate,pass_constraints_relocate),(exchange,implement_exchange,pass_constraints_exchange),(cross,implement_cross,pass_constraints_cross)]
    routes = initial_solution 

    local_search(routes,distance_matrix,penalty_matrix,demands,vehicle_capacity,penalty,heurestics)

    best_routes = deepcopy(routes)

    sum_routes = sum([sum_distance(route,distance_matrix) for route in routes])
    best_cost = sum_routes  


    start = time.time()
    #for i in tqdm (range(max_iter),desc="Optimizing"):
    for i in range(max_iter):
        if time_limit != None and time.time() -start > time_limit:
            print("Reached time limit")
            break
        new_penalty = penalty*(1-0.8*(i/max_iter))
        feture_penalties = find_penalty_feature(routes,distance_matrix,penalty_matrix)
        for feture in feture_penalties:
            penalty_matrix[feture[0]][feture[1]] += 1

        local_search(routes,distance_matrix,penalty_matrix,demands,vehicle_capacity,new_penalty,heurestics)

        sum_routes = sum([sum_distance(route,distance_matrix) for route in routes])
        cost = sum_routes  
        if cost < best_cost:
            best_routes = deepcopy(routes)
            best_cost = cost
        else:
            break


    local_search(best_routes,distance_matrix,no_penalty,demands,vehicle_capacity,penalty,heurestics)

    return best_routes


def solve_cutom_gls(distance_matrix,demands,vehicle_capacity,penalty=0.2,max_iter=2000,max_time=10):
    penalty_matrix = []
    for _ in range(len(distance_matrix)):
        temp_row = []
        for _ in range(len(distance_matrix)):
            temp_row.append(0)
        penalty_matrix.append(temp_row)

    ini_solution = near_neighbor_gen(distance_matrix,demands,vehicle_capacity)
    routes = gls(ini_solution,distance_matrix,penalty_matrix,penalty,demands,vehicle_capacity,max_iter,max_time)
    cost_routes = sum([sum_distance(route,distance_matrix) for route in routes])

    return routes,cost_routes
    
if __name__ == "__main__":
    point_amount = 100 
    vehicle_amount = 1 
    height = 1080
    width = 1920
    test_times = 10 
    total_procent_diff = 0
    #for i in tqdm(range(test_times),desc="Testing"):
    points,distance_matrix = generate_distance_matrix(point_amount,width,height)
    distance_matrix = []
    with open("data/molok_distance_matrix2.json","r") as f:
        distance_matrix = json.load(f)
    penalty_matrix = []
    for i in range(len(distance_matrix)):
        temp_row = []
        for j in range(len(distance_matrix)):
            temp_row.append(0)
        penalty_matrix.append(temp_row)
    penalty = 0.2

    demands = [0.0]
    demand_google = [0]

    for i in range(1,len(distance_matrix)):
        demands.append(1.0)
        demand_google.append(1)
    vehicle_capacity = len(distance_matrix)/vehicle_amount

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    max_time = 10
    #data = gen_data_or(distance_matrix,point_amount,vehicle_amount,demand_google)
    #google_distance = solve_vrp_google(data,points,draw,max_time)
    #print(f"Len google: {google_distance}")
    #img.save("or.png")



    max_distance = max([max(row) for row in distance_matrix])
    max_iter = 2000
    ini_solution = near_neighbor_gen(distance_matrix,demands,vehicle_capacity)
    #ini_solution = random_gen(distance_matrix,demands,vehicle_capacity)

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)
    cost_routes = sum([sum_distance(route,distance_matrix) for route in ini_solution])
    #print(f"Ini cost: f{cost_routes}")

    routes = gls(ini_solution,distance_matrix,penalty_matrix,penalty,demands,vehicle_capacity,max_iter,max_time)
    print(len(routes))


    #draw_clark_wright(points,routes,draw)

    #img.save("gls.png")

    cost_routes = sum([sum_distance(route,distance_matrix) for route in routes])
    print(f"GLS: {cost_routes}")
    #print(routes)
    #print(f"Best distance: {cost_routes}")
    #procentage_diff = ((cost_routes - google_distance) /google_distance)*100
    #total_procent_diff += procentage_diff
    #print(f"Procent worse: {procentage_diff}")
    #print(f"Procent diff: {total_procent_diff/test_times}")



