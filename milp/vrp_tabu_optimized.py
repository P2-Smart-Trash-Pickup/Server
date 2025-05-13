from copy import deepcopy,copy
from milp.gen_data import generate_distance_matrix,get_distance,gen_data_or
import random
import time
from milp.vrp_or import solve_vrp_google

def sum_route(route:list[int],demand:list[float]) -> float:
    total_demand = 0
    for i in route:
        total_demand += demand[i]
    return total_demand 

def sum_distance(route:list[int],distance_matrix:list[list[int]]) -> float:
    total_distance = 0
    for point_idx in range(len(route)-1):
        point1 = route[point_idx]
        point2 = route[point_idx+1]
        total_distance += distance_matrix[point1][point2]
    return total_distance 

def min_distance_for_point(input_point_idx:int,different_point_idxs:list[int],distance_matrix:list[list[int]]) -> tuple[int,float]:
    best_point = 0 
    min_distance = float("inf")

    for point_idx in different_point_idxs:
        distance = distance_matrix[input_point_idx][point_idx] 
        if distance < min_distance:
            best_point = point_idx 
    return best_point,min_distance 

def random_gen(distance_matrix:list[list[int]],demand:list[float],vehicle_capacity:float) -> list[list[int]]:
    random_points = list(range(1,len(distance_matrix))) 
    random.shuffle(random_points)
    routes = [[0]]
    current_route_idx = 0
    current_demand = 0
    for point_idx in random_points: 
        if demand[point_idx] + current_demand > vehicle_capacity:
            routes[current_route_idx].append(0)
            routes.append([0])
            current_route_idx += 1
            current_demand = 0
            continue
        routes[current_route_idx].append(point_idx)
        current_demand += demand[point_idx]
    routes[current_route_idx].append(0)
    return routes

def near_neighbor_gen(distance_matrix:list[list[int]],demand:list[float],vehicle_capacity:float) -> list[list[int]]:
    unassigned_points = [i for i in range(1,len(distance_matrix))]
    routes = []
    inital_points = len(unassigned_points)
    #pbar = tqdm(total=inital_points,desc="Generating ini solution")
    pre_point_length = inital_points
    while len(unassigned_points) > 0:
        random_index = random.randint(0,len(unassigned_points)-1)
        v_i = unassigned_points.pop(random_index)
        if len(unassigned_points) == 0:
            routes.append([0,v_i,0])
            break
        v_k,_= min_distance_for_point(v_i,unassigned_points,distance_matrix)
        unassigned_points.remove(v_k)

        current_route = [0,v_i,v_k,0]
        current_load = demand[v_i] + demand[v_k]

        while True:
            best_cost = float("inf") 
            best_index = 0
            best_point = 0

            points_exists = False 
            for point_idx in unassigned_points:
                if current_load + demand[point_idx] > vehicle_capacity:
                    continue
                points_exists = True
                for current_point_idx in range(len(current_route)-1):
                    current_point = current_route[current_point_idx]
                    next_point = current_route[current_point_idx+1]
                    cost = distance_matrix[current_point][point_idx] + distance_matrix[point_idx][next_point] - distance_matrix[current_point][next_point]
                    if cost < best_cost:
                        best_cost = cost
                        best_point = point_idx
                        best_index = current_point_idx+1
            if not points_exists:
                routes.append(current_route)
                break
            else:
                unassigned_points.remove(best_point)
                current_load += demand[best_index]
                current_route.insert(best_index,best_point)
                if pre_point_length > len(unassigned_points):
                    #pbar.update(pre_point_length-len(unassigned_points))
                    pass
                pre_point_length = len(unassigned_points)
    #pbar.close()
    return routes


def generate_initial_solution(distance_matrix:list[list[int]],demands:list[float],vehicle_capacity:float,times:int) -> list[list[list[int]]]:
    solutions = []
    individual_times = int(times/2)
    for _ in range(individual_times):
        new_solution = random_gen(distance_matrix,demands,vehicle_capacity)
        solutions.append(new_solution)

    for _ in range(individual_times):
        new_solution = near_neighbor_gen(distance_matrix,demands,vehicle_capacity)
        solutions.append(new_solution)
    return solutions

def insertion_procedure(sub_route:list[int],route:list[int],distance_matrix:list[list[int]]):
    if 0 in sub_route:
        raise Exception("INSERTION Depot in sub route")

    start_length = len(sub_route)+len(route)

    while len(sub_route) > 0:
        if start_length != len(route)+len(sub_route):
            raise Exception("INSERTION MISSINGP POINT")

        if route[0] != 0:
            raise Exception("INSERTION depot not beginning of route")
        elif route[-1] != 0:
            raise Exception("INSERTION depot not end of route")
        elif 0 in route[1:-1]:
            raise Exception("INSERTION depot middle of route")
        best_cost = float("inf")
        best_point = 0
        best_index = 0
        for point_idx in sub_route:
            for current_point_idx in range(len(route)-1):
                current_point = route[current_point_idx]
                next_point = route[current_point_idx+1]
                cost = distance_matrix[current_point][point_idx] + distance_matrix[point_idx][next_point] - distance_matrix[current_point][next_point]
                if cost < best_cost:
                    best_cost = cost
                    best_point = point_idx
                    best_index = current_point_idx+1
        route.insert(best_index,best_point)
        sub_route.remove(best_point)

def two_opt_procedure(route:list[int],distance_matrix:list[list[int]]):
    improved = True
    start_length = len(route)
    while improved: 
        if route[0] != 0:
            raise Exception("TWO OPT depot not beginning of route")
        elif route[-1] != 0:
            raise Exception("TWO OPT depot not end of route")
        elif 0 in route[1:-1]:
            raise Exception("TWO OPT depot middle of route")
        best_improvement = 0
        improved = False
        best_i = -1
        best_j = -1
        for i in range(1,len(route)-2):
            for j in range(i+1,len(route)-1):
                pre_point_i = route[i]
                next_point_i = route[i+1]

                pre_point_j = route[j]
                next_point_j = route[j+1]


                distance_prei_nexti = distance_matrix[pre_point_i][next_point_i]
                distance_prej_nextj = distance_matrix[pre_point_j][next_point_j]
                distance_prei_prej = distance_matrix[pre_point_i][pre_point_j]
                distance_nexti_nextj = distance_matrix[next_point_i][next_point_j]

                improvement = (distance_prei_nexti + distance_prej_nextj) - (distance_prei_prej + distance_nexti_nextj)

                if improvement > best_improvement:
                    best_improvement = improvement
                    best_i = i
                    best_j = j

        if best_improvement > 0:
            improved = True

            route[best_i+1:best_j+1] = route[best_i+1:best_j+1][::-1]
            if len(route) != start_length:
                raise Exception("TWO OPT NUM MISSING")

def TANE_generate_swap(max_interchange:int, r:list[int]) -> tuple[list[int],int]:
    r_length = len(r)
    sub_length = random.randint(1,min(max_interchange,r_length-3))

    sub_r = random.sample(r[1:-1],sub_length) 
    if 0 in sub_r:
        raise Exception("GEN SWAP 0 in SUB ROUTE")
    return sub_r,sub_length

def TANE(initial_solution:list[list[int]],vehicle_capacity:float,distance_matrix:list[list[int]],demand:list[float],max_neigbors:int,max_interchange_1:int,max_interchange_2:int) -> list[tuple[list[tuple[int,int,int]],int]]: 
    route_amount = len(initial_solution)

    neighbors = []

    for _ in range(max_neigbors):
        r1_index = random.randint(0,route_amount-1)
        r2_index = random.randint(0,route_amount-1)

        r1 = copy(initial_solution[r1_index])
        r2 = copy(initial_solution[r2_index])

        old_distance = sum_distance(r1,distance_matrix) + sum_distance(r2,distance_matrix)

        sub_r2,_ = TANE_generate_swap(max_interchange_2,r2) 
        sub_r1,_ = TANE_generate_swap(max_interchange_1,r1) 

        if sum_route(r1,demand) + sum_route(sub_r2,demand) > vehicle_capacity:
            continue

        if sum_route(r2,demand) + sum_route(sub_r1,demand) > vehicle_capacity:
            continue

        current_moves = [] 

        for point_index in sub_r2:
            r1_swap_move = (point_index, r2_index,r1_index)
            if r1_swap_move in current_moves:
                continue
            current_moves.append(r1_swap_move)

        for point_index in sub_r1:
            r2_swap_move = (point_index, r1_index,r2_index)
            if r2_swap_move in current_moves:
                continue
            current_moves.append(r2_swap_move)

        insertion_procedure(sub_r2,r1,distance_matrix)
        insertion_procedure(sub_r1,r2,distance_matrix)

        two_opt_procedure(r1,distance_matrix)
        two_opt_procedure(r2,distance_matrix)

        new_distance = sum_distance(r1,distance_matrix) + sum_distance(r2,distance_matrix)

        improvement = new_distance - old_distance

        neighbors.append((current_moves,improvement))

    return neighbors

def find_center(route:list[int],points:list[list[int]],exclude:int=-1) -> list[float]:
    centroid = [0.0,0.0]

    for point_idx in route:
        if point_idx == exclude:
            continue
        point = points[point_idx]
        centroid[0] += point[0]
        centroid[1] += point[1]
    centroid[0] = centroid[0] / len(route)
    centroid[1] = centroid[1] / len(route)

    return centroid


def TANEC(initial_solution:list[list[int]],vehicle_capacity:float,distance_matrix:list[list[int]],points:list[list[int]],demand:list[float],max_neigbors:int,max_interchange_1:int,max_interchange_2:int) -> list[tuple[list[tuple[int,int,int]],int]]: 

    route_amount = len(initial_solution)
    neighbors = []

    for _ in range(max_neigbors):
        r1_index = random.randint(0,route_amount-1)
        r2_index = random.randint(0,route_amount-1)

        r1 = copy(initial_solution[r1_index])
        r2 = copy(initial_solution[r2_index])

        old_distance = sum_distance(r1,distance_matrix) + sum_distance(r2,distance_matrix)

        C2 = find_center(r2,points)

        r1_ratios = []

        for point_idx in r1[1:-1]:
            C1 = find_center(r1,points,point_idx)
            current_point = points[point_idx]
            d1 = get_distance(C1,current_point)
            d2 = get_distance(C2,current_point)
            ratio = d1/d2
            r1_ratios.append(ratio)

        r1[1:-1] = [x for _,x in sorted(zip(r1_ratios,r1[1:-1]),reverse=True)]

        C1 = find_center(r2,points)

        r2_ratios = []

        for point_idx in r2[1:-1]:
            C2 = find_center(r2,points,point_idx)
            current_point = points[point_idx]
            d1 = get_distance(C2,current_point)
            d2 = get_distance(C1,current_point)
            ratio = d1/d2
            r2_ratios.append([point_idx,ratio])

        r2[1:-1] = [x for _,x in sorted(zip(r2_ratios,r2[1:-1]),reverse=True)]

        r1_swap_amount = random.randint(1,min(max_interchange_1,len(r1)-3))
        r2_swap_amount = random.randint(1,min(max_interchange_2,len(r2)-3))

        sub_r1 = r1[1:r1_swap_amount]
        sub_r2 = r2[1:r2_swap_amount]
        r1_times = 1
        r2_times = 1

        capacity_possible = True

        while sum_route(r1,demand) + sum_route(sub_r2,demand) > vehicle_capacity:
            end_index = r1_swap_amount*r1_times 
            if end_index > len(r1) -2:
                capacity_possible = False
                break
            sub_r2 = r2[1+r1_times*r1_swap_amount:end_index]
            r1_times += 1

        if not capacity_possible:
            continue

        capacity_possible = True

        while sum_route(r2,demand) + sum_route(sub_r1,demand) > vehicle_capacity:
            end_index = r2_swap_amount*r2_times 
            if end_index > len(r2) - 2:
                capacity_possible = False
                break
            sub_r1 = r1[1+r2_times*r2_swap_amount:end_index]
            r2_times += 1

        if not capacity_possible:
            continue

        current_move = [] 
        for point_index in sub_r2:
            r1_swap_move = (point_index, r2_index,r1_index)
            if r1_swap_move in current_move:
                continue
            current_move.append(r1_swap_move)  

        for point_index in sub_r1:
            r2_swap_move = (point_index, r1_index,r2_index)
            if r2_swap_move in current_move:
                continue
            current_move.append(r2_swap_move)  


        insertion_procedure(sub_r2,r1,distance_matrix)
        insertion_procedure(sub_r1,r2,distance_matrix)


        two_opt_procedure(r1,distance_matrix)
        two_opt_procedure(r2,distance_matrix)

        new_distance = sum_distance(r1,distance_matrix) + sum_distance(r2,distance_matrix)

        improvement = new_distance - old_distance 

        neighbors.append((current_move,improvement))

    return neighbors


def SENE(initial_solution:list[list[int]],vehicle_capacity:float,distance_matrix:list[list[int]],points:list[list[int]],demand:list[float],max_no_improve:int,max_neigbors:int,max_interchange_1:int,max_interchange_2:int,min_tenure:int,max_tenure:int) -> tuple[list[list[int]],list[list[list[int]]]]:

    no_improvement = 0

    tabu_list = {}

    current_solution = initial_solution

    best_solution = deepcopy(current_solution) 
    pre_k_cost = None
    ins_list = []
    iteration = -1
    best_cost = sum([sum_distance(route,distance_matrix) for route in initial_solution])
    pre_cost = best_cost 
    while no_improvement < max_no_improve:
        iteration += 1
        #print(iteration)
        new_tabu_list = {}
        for move in tabu_list.items():
            if move[1][0] + move[1][1] > iteration:
                new_tabu_list[move[0]] = move[1]

        tabu_list = new_tabu_list
        start_tabu_list = deepcopy(tabu_list)

        best_current_move = None
        best_current_cost = float("inf")
        if no_improvement % int(5*len(points)/10) == 0:
            current_solution = deepcopy(best_solution)
            tabu_list = {move: tenure for move, tenure in tabu_list.items()
                 if move[0] in current_solution[move[1]]}  # Keep only valid moves

        best_tane_move = None 
        best_tane_improvement= float("inf")

        tane_neighbors = TANE(current_solution,vehicle_capacity,distance_matrix,demand,max_neigbors,max_interchange_1,max_interchange_2)
        for neighbor in tane_neighbors:
            moves = neighbor[0]
            cost = neighbor[1]
            if cost > best_tane_improvement:
                continue
            is_tabu = False
            for move in moves:
                tabu_move = tabu_list.get(move)
                if tabu_move:
                    is_tabu = True
                    break
            if is_tabu and cost > 0:
                continue
            best_tane_move = moves
            best_tane_improvement = cost 

        best_tanec_move = None
        best_tanec_improvement= float("inf")

        tanec_neighbors = TANEC(current_solution,vehicle_capacity,distance_matrix,points,demand,max_neigbors,max_interchange_1,max_interchange_2)

        for neighbor in tanec_neighbors:
            moves = neighbor[0]
            cost = neighbor[1]
            if cost > best_tanec_improvement:
                continue
            is_tabu = False
            for move in moves:
                tabu_move = tabu_list.get(move)
                if tabu_move:
                    is_tabu = True
                    break
            if is_tabu and cost > 0:
                continue
            best_tanec_move = moves
            best_tanec_improvement = cost 

        if best_tanec_move and best_tane_move:
            best_current_move = best_tanec_move if best_tanec_improvement < best_tane_improvement else best_tane_move
            best_current_cost = best_tanec_improvement if best_tanec_improvement < best_tane_improvement else best_tane_improvement
        elif best_tanec_move and not best_tane_move :
            best_current_move = best_tanec_move
            best_current_cost = best_tanec_improvement
        elif not best_tanec_move and best_tane_move :
            best_current_move = best_tane_move
            best_current_cost = best_tane_improvement
        else:
            if not tabu_list:
                break
            old_val = min(tabu_list.values(),key=lambda x:x[1])
            best_current_move = [key for key in tabu_list if tabu_list[key] == old_val]
            best_current_cost = None 
            for move in best_current_move:
                del tabu_list[move]

        random_tenure = random.randint(min_tenure,max_tenure)
        for move in best_current_move:
            new_move = (move[0],move[2],move[1])
            tabu_list[new_move] = [random_tenure , iteration]

        change = {}
        if len(best_current_move) == 0:
            print(best_tanec_move)
            print(best_tane_move)
            print(best_current_move)
            print(start_tabu_list)
            print(tabu_list)
            raise Exception("No best current move")

        r1_index = best_current_move[0][1]
        r2_index = best_current_move[0][2]

        change[r1_index] = []
        change[r2_index] = []

        pre_solution = deepcopy(current_solution)

        for move in best_current_move:
            point = move[0]
            route_from = move[1]
            route_to = move[2]
            if point not in current_solution[route_from]:
                continue
                """
                print(best_tane_move)
                print(best_tanec_move)
                print(best_current_move)
                print(point)
                print(current_solution[route_from])
                print(current_solution)
                print(f"Swapped to best: {swapped_to_best}")
                raise Exception("Point no in list")
                """
            current_solution[route_from].remove(point)
            change[route_to].append(point)

        insertion_procedure(change[r1_index],current_solution[r1_index],distance_matrix)
        insertion_procedure(change[r2_index],current_solution[r2_index],distance_matrix)

        best_current_distance = sum([sum_distance(route,distance_matrix) for route in current_solution])
        

        for route in current_solution:
            if 0 in route[1:-1]:
                print(current_solution)
                raise Exception("Depot in middle of route")
            elif route[0] != 0:
                print(current_solution)
                raise Exception("Depot not in beginning of route")
            elif route[-1] != 0:
                print(current_solution)
                raise Exception("Depot not in end of route")


        if sum([len(route) for route in pre_solution]) != sum([len(route) for route in current_solution]):
            raise Exception("Missing point")

        k_cost = best_current_distance - pre_cost

        if k_cost > 0 and (pre_k_cost is None or pre_k_cost <= 0):
            ins_list.append(deepcopy(pre_solution))

        pre_k_cost = best_current_cost 

        if best_current_distance < best_cost:
            best_solution = deepcopy(current_solution)
            best_cost = best_current_distance
            print(best_cost)
            no_improvement = 0
        else:
            no_improvement += 1

    return best_solution,ins_list
if __name__ == "__main__":
    improvement = 0

    points,distance_matrix = generate_distance_matrix(1000,1920,1080)
    vehicle_capacity = len(distance_matrix)/2
    demand = [0.0]
    for i in range(1,len(distance_matrix)):
        demand.append(1.0)
    #_,tabu_distqance = solve_vrp_tabu(distance_matrix,demand,vehicle_capacity,100,10)
    #print(f"Basic tabu {tabu_distqance}")
    #_,cw_dist = solve_vrp_clark_wright(distance_matrix,demand,vehicle_capacity)
    #print(f"CW {cw_dist}")
    data = gen_data_or(distance_matrix,len(points),2,demand)
    or_distance = solve_vrp_google(data,points,0)
    print(f"OR {or_distance}")

    routes = random_gen(distance_matrix,demand,vehicle_capacity)
    pre_distance = sum([sum_distance(route,distance_matrix) for route in  routes])

    start = time.time()
    initial_solutions = generate_initial_solution(distance_matrix,demand,vehicle_capacity,int(len(distance_matrix)**0.5))
    initial_distance = sum([sum_distance(route,distance_matrix) for route in initial_solutions[0]])
    print(f"Initial distance: {initial_distance}")
    initial_distance = sum([sum_distance(route,distance_matrix) for route in initial_solutions[-1]])
    print(f"Initial distance: {initial_distance}")
    initial_solutions_distances = []
    for solution in initial_solutions:
        initial_distance = sum([sum_distance(route,distance_matrix) for route in solution])
        initial_solutions_distances.append(initial_distance)

    print(f"Smallest inital: {min(initial_solutions_distances)}")

    best_distance = float("inf")
    sene_solutions = [] 

    m = int(sum(demand)/vehicle_capacity)
    iteration = 0
    print(len(initial_solutions))
    for solution in initial_solutions:
        print(f"STEP 1 solution: {iteration}")
        sene_solution,_ = SENE(initial_solution=solution, vehicle_capacity=vehicle_capacity,distance_matrix=distance_matrix,points=points,demand=demand,max_no_improve=len(distance_matrix),max_neigbors=5,max_interchange_2=2,max_interchange_1=2,min_tenure=5,max_tenure=10)

        sene_distance = sum([sum_distance(route,distance_matrix) for route in sene_solution])
        print(f"Distance step 1:{iteration} : {sene_distance}")
        sene_solutions.append([sene_solution,sene_distance])
        iteration += 1

    sene_solutions.sort(key=lambda x: x[1])
    print(f"Best step 1: {sene_solutions[0][1]}")
    ins_set = []

    max_neigbors = int((len(distance_matrix)*m)/2)

    new_sene_solutions = []
    ins_list = []
    iteration = 0
    for solution_pair in sene_solutions:
        print(f"STEP 2 solution: {iteration}")
        solution = solution_pair[0]
        sene_solution,sene_ins = SENE(initial_solution=solution, vehicle_capacity=vehicle_capacity,distance_matrix=distance_matrix,points=points,demand=demand,max_no_improve=len(distance_matrix)*50,max_neigbors=max_neigbors,max_interchange_2=2,max_interchange_1=2,min_tenure=10,max_tenure=20)

        sene_distance = sum([sum_distance(route,distance_matrix) for route in sene_solution])
        print(f"Distance step 2:{iteration} : {sene_distance}")
        iteration += 1

        new_sene_solutions.append([sene_solution,sene_distance])
        ins_list += sene_ins

    new_sene_solutions.sort(key=lambda x:x[1])

    #new_amount = int((len(distance_matrix)*m)**0.5)
    print(f"Len: {len(new_sene_solutions)}")
    print(f"Best step 2: {new_sene_solutions[0][1]}")
    bestest_solution = []
    print(f"Len ins list: {len(ins_list)}")
    iteration = 0
    for i in range(len(new_sene_solutions)):
        print(f"STEP 3 solution: {iteration}")
        solution = new_sene_solutions[i][0] 
        if solution in ins_list:
            print("DAMN")
            sene_solution,_ = SENE(solution,vehicle_capacity=vehicle_capacity,distance_matrix=distance_matrix,points=points,demand=demand,max_no_improve=len(distance_matrix),max_neigbors=max_neigbors,max_interchange_1=2,max_interchange_2=2,min_tenure=5,max_tenure=10)
            sene_distance = sum([sum_distance(route,distance_matrix) for route in sene_solution])
            print(f"Distance step 3:{iteration} : {sene_distance}")

            bestest_solution.append([sene_solution,sene_distance])

        iteration += 1
    print(f"OR {or_distance}")
    if bestest_solution:
        bestest_solution.sort(key=lambda x:x[1])
        print(f"Bests step 3: {bestest_solution[0][1]}")
