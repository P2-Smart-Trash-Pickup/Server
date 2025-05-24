import random
from vehicle import Vehicle
from calculate_energy import calcualte_segment_energy, calculate_route_energy 
from help_heuristics import sum_route_time, sum_route_weight_volume
from test_vrp import gen_test
from tqdm import tqdm

def near_neighbor_gen(elevation_matrix:list[list[list[list[float]]]],time_matrix:list[list[float]],volumes:list[float],weights:list[float],vehicle:Vehicle) -> tuple[list[list[int]],list[int]]:
    unassigned_points = [i for i in range(1,len(elevation_matrix))]
    routes = []
    pbar = tqdm(total=len(unassigned_points))

    while len(unassigned_points) > 0:
        #print(len(unassigned_points))
        v_i = random.choice(unassigned_points)
        unassigned_points.remove(v_i)

        current_route = [0,v_i,0]
        current_weights = sum_route_weight_volume(current_route,weights)
        current_volumes = sum_route_weight_volume(current_route,volumes)
        vehicle.current_mass = current_weights + vehicle.initial_mass
        vehicle.current_volume = current_volumes
        current_time = sum_route_time(current_route,time_matrix)


        best_v_k = 1
        while best_v_k:

            best_v_k = None
            best_cost_diff = float("inf")
            best_insertion = 0 
            best_time_diff = 0 
            best_weight = 0
            best_volume = 0

            for v_k in unassigned_points:
                v_k_weight = weights[v_k]
                v_k_volume = volumes[v_k]
                if vehicle.current_mass + v_k_weight > vehicle.max_capacity:
                    #print("max mass")
                    continue
                if vehicle.current_volume + v_k_volume > vehicle.max_volume:
                    #print("max volume")
                    continue

                new_vehicle_mass = vehicle.current_mass + v_k_weight 

                current_power_consumption,_ = calculate_route_energy(route=current_route,elevation_matrix=elevation_matrix,time_matrix=time_matrix,vehicle=vehicle,weights=weights)

                for index in range(len(current_route)-1):
                    point = current_route[index]
                    next_point = current_route[index]
                    previous_arc = elevation_matrix[point][next_point]

                    next_arc_1= elevation_matrix[point][v_k]
                    next_arc_2= elevation_matrix[v_k][next_point]

                    previous_time = time_matrix[point][next_point]

                    next_time_1 = time_matrix[point][v_k]
                    next_time_2 = time_matrix[v_k][next_point]

                    previous_cost,_ = calcualte_segment_energy(previous_arc,previous_time,vehicle.current_mass,vehicle.acceleration) 


                    next_cost_1,_ = calcualte_segment_energy(next_arc_1,next_time_1,new_vehicle_mass,vehicle.acceleration) 
                    next_cost_2,_ = calcualte_segment_energy(next_arc_2,next_time_2,new_vehicle_mass,vehicle.acceleration) 

                    cost_diff = (next_cost_1+next_cost_2) - previous_cost
                    time_diff = (next_time_1+next_time_2) - previous_time 


                    if cost_diff + current_power_consumption > vehicle.battery_capacity:
                        #print("max power")
                        continue

                    if current_time + time_diff  > vehicle.time_constraint:
                        #print("max time")
                        continue

                    if cost_diff< best_cost_diff:
                        best_v_k = v_k
                        best_cost_diff = cost_diff
                        best_insertion = index+1
                        best_weight = v_k_weight
                        best_time_diff = time_diff  
                        best_volume = v_k_volume
            if not best_v_k:
                routes.append(current_route)
                continue
            unassigned_points.remove(best_v_k)
            pbar.update(1)
            current_route.insert(best_insertion,best_v_k)
            vehicle.current_mass += best_weight
            vehicle.current_volume += best_volume
            current_time += best_time_diff 
            #print(f"Current time: {current_time}")
            #print(f"Max time: {vehicle.time_constraint}")
    pbar.close()
    return routes,unassigned_points

if __name__ == "__main__":

    elevation_matrix,time_matrix,fill_rates,weights,vehicle,penalty_matrix = gen_test()
    routes,_ = near_neighbor_gen(elevation_matrix=elevation_matrix,time_matrix=time_matrix,volumes=fill_rates,weights=weights,vehicle=vehicle)

    for route in routes:
        print()
        print(f"point amount: {len(route)}")
        en1,_ = calculate_route_energy(route=route,time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
        print(f"cost: {en1}")


