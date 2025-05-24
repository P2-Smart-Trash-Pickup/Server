import random

from calculate_energy import calculate_route_energy
from help_heuristics import get_penalty, is_weekend, sum_route_dist
from nearest_neighbor import near_neighbor_gen
from test_vrp import gen_test, gen_test_dist
from vehicle import Vehicle


def two_op_en(
    route: list[int],
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    penalty_matrix: list[list[int]],
    weights: list[float],
    vehicle: Vehicle,
    penalty: float,
) -> tuple[float, int, int]:
    best_improvement = float("inf")

    best_start_swap_index = 0
    best_end_swap_index = 0

    default_cost, pen_old_cost = calculate_route_energy(
        route=route,
        elevation_matrix=elevation_matrix,
        time_matrix=time_matrix,
        vehicle=vehicle,
        penalty_matrix=penalty_matrix,
        penalty=penalty,
        weights=weights,
    )

    for start_index in range(1, len(route) - 2):
        for end_index in range(start_index + 1, len(route) - 1):

            new_route = (
                route[: start_index + 1]
                + route[start_index + 1 : end_index + 1][::-1]
                + route[end_index + 1 :]
            )

            new_default_cost, penalized_new_cost = calculate_route_energy(
                new_route,
                elevation_matrix=elevation_matrix,
                time_matrix=time_matrix,
                vehicle=vehicle,
                penalty_matrix=penalty_matrix,
                penalty=penalty,
                weights=weights,
            )

            if new_default_cost > vehicle.battery_capacity:
                continue

            pen_cost_diff = penalized_new_cost - pen_old_cost

            if pen_cost_diff < best_improvement:
                best_improvement = pen_cost_diff
                best_start_swap_index = start_index
                best_end_swap_index = end_index

    return best_improvement, best_start_swap_index, best_end_swap_index


def two_op_en_multi_day(
    day_plan: list[list[list[int]]],
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    day_penalty_matrix: list[list[list[int]]],
    penalty: float,
    vehicles: list[Vehicle],
    stop_delay: float,
    weight_matrix: list[list[float]],
    day_volume_matrix: list[list[float]],
    days_in: list[list[int]],
    empty_interval: list[int],
) -> tuple[float, int, int, int, int, int, int]:

    best_improvement = 0
    best_i = 0
    best_j = 0
    best_day_i = 0
    best_day_j = 0
    best_route_i = 0
    best_route_j = 0

    for day_idx_i in range(len(day_plan)):
        if is_weekend(day_idx_i):
            continue
        cur_day_i = day_plan[day_idx_i]

        penalty_matrix = day_penalty_matrix[day_idx_i]
        cur_weight = weight_matrix[day_idx_i]
        for route_idx_i in range(len(cur_day_i)):
            route_i = cur_day_i[route_idx_i]
            cur_vehicle = vehicles[route_idx_i]

            temp_best_cost, temp_i, temp_j = two_op_en(
                route=route_i,
                elevation_matrix=elevation_matrix,
                time_matrix=time_matrix,
                penalty_matrix=penalty_matrix,
                weights=cur_weight,
                vehicle=cur_vehicle,
                penalty=penalty,
            )
            if temp_best_cost >= 0:
                continue
            if temp_best_cost < best_improvement:
                best_improvement = temp_best_cost
                best_i = temp_i
                best_j = temp_j
                best_day_i = day_idx_i
                best_route_i = route_idx_i

    return (
        best_improvement,
        best_i,
        best_j,
        best_route_i,
        best_route_j,
        best_day_i,
        best_day_j,
    )


def two_op_cap(
    route: list[int],
    distance_matrix: list[list[float]],
    penalty_matrix: list[list[int]],
    penalty: float,
) -> tuple[float, int, int]:
    best_delta = 0

    best_i = 0
    best_j = 0

    for i in range(1, len(route) - 2):
        for j in range(i + 1, len(route) - 1):
            point_i = route[i]
            point_i_p = route[i + 1]
            point_j = route[j]
            point_j_p = route[j + 1]
            old_cost = 0
            for uki in range(i, j + 1):
                cur_p = route[uki]
                n_p = route[uki + 1]
                old_cost += get_penalty(
                    cur_p, n_p, distance_matrix, penalty_matrix, penalty
                )

            temp_swap = [point_i] + route[i + 1 : j + 1][::-1] + [point_j_p]
            new_cost = 0
            for aky in range(len(temp_swap) - 1):
                cur_p = temp_swap[aky]
                n_p = temp_swap[aky + 1]
                new_cost += get_penalty(
                    cur_p, n_p, distance_matrix, penalty_matrix, penalty
                )

            # old_edge_i = get_penalty(point_i,point_i_p,distance_matrix,penalty_matrix,penalty)
            # old_edge_j = get_penalty(point_j,point_j_p,distance_matrix,penalty_matrix,penalty)

            # new_edge_ij = get_penalty(point_i,point_j,distance_matrix,penalty_matrix,penalty)

            # new_edge_ij_plus = get_penalty(point_i_p,point_j_p,distance_matrix,penalty_matrix,penalty)

            # delta_cost = (new_edge_ij+new_edge_ij_plus) - (old_edge_i+old_edge_j)
            delta_cost = new_cost - old_cost

            if delta_cost < best_delta:
                best_i = i
                best_j = j
                best_delta = delta_cost

    return best_delta, best_i, best_j


def two_op_days_cap(
    day_plan: list[list[list[int]]],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    day_penalty_matrix: list[list[list[int]]],
    penalty: float,
    vehicles: list[Vehicle],
    stop_delay: float,
    weight_matrix: list[list[float]],
    days_in: list[list[int]],
    empty_interval: list[int],
) -> tuple[float, int, int, int, int, int, int]:
    best_improvement = 0
    best_i = 0
    best_j = 0
    best_day_i = 0
    best_day_j = 0
    best_route_i = 0
    best_route_j = 0

    for day_idx_i in range(len(day_plan)):
        if is_weekend(day_idx_i):
            continue
        cur_day_i = day_plan[day_idx_i]

        penalty_matrix = day_penalty_matrix[day_idx_i]
        for route_idx_i in range(len(cur_day_i)):
            route_i = cur_day_i[route_idx_i]

            temp_best_cost, temp_i, temp_j = two_op_cap(
                route=route_i,
                distance_matrix=distance_matrix,
                penalty=penalty,
                penalty_matrix=penalty_matrix,
            )
            if temp_best_cost >= 0:
                continue
            if temp_best_cost < best_improvement:
                best_improvement = temp_best_cost
                best_i = temp_i
                best_j = temp_j
                best_day_i = day_idx_i
                best_route_i = route_idx_i

    return (
        best_improvement,
        best_i,
        best_j,
        best_route_i,
        best_route_j,
        best_day_i,
        best_day_j,
    )


def implement_two_op(
    routes: list[list[int]], route1_idx: int, best_i: int, best_j: int
):
    route = routes[route1_idx]
    new_route = (
        route[: best_i + 1] + route[best_i + 1 : best_j + 1][::-1] + route[best_j + 1 :]
    )
    routes[route1_idx] = new_route


def implement_two_op_days(
    day_plan: list[list[list[int]]],
    best_i: int,
    best_j: int,
    best_route_i: int,
    best_route_j: int,
    best_day_i: int,
    best_day_j: int,
    days_in: list[list[int]],
    weight_matrix: list[list[float]],
    fill_rates: list[float],
):
    day = day_plan[best_day_i]
    route = day[best_route_i]

    route = (
        route[: best_i + 1] + route[best_i + 1 : best_j + 1][::-1] + route[best_j + 1 :]
    )

    day[best_route_i] = route


def implement_two_op_days_en(
    day_plan: list[list[list[int]]],
    best_i: int,
    best_j: int,
    best_route_i: int,
    best_route_j: int,
    best_day_i: int,
    best_day_j: int,
    days_in: list[list[int]],
    weight_matrix: list[list[float]],
    fill_rates: list[float],
    volume_matrix: list[list[float]],
):
    day = day_plan[best_day_i]
    route = day[best_route_i]

    route = (
        route[: best_i + 1] + route[best_i + 1 : best_j + 1][::-1] + route[best_j + 1 :]
    )

    day[best_route_i] = route


if __name__ == "__main__":

    distance_matrix, time_matrix, _, max_fill, vehicle, pen_matrix = gen_test_dist()
    # routes,_ = near_neighbor_gen(elevation_matrix=elevation_matrix,time_matrix=time_matrix,volumes=fill_rates,weights=weights,vehicle=vehicle)
    customers = [i for i in range(1, len(distance_matrix))]
    test_cust = random.sample(customers, 20)
    route1 = [0] + test_cust[:11] + [0]

    print(route1)
    # route2 = [0] + test_cust[11:] +[0]
    pre_dist_1 = sum_route_dist(distance_matrix=distance_matrix, route=route1)
    # pre_dist_2 = sum_route_dist(distance_matrix=distance_matrix,route=route2)

    print(f"pre_dist: {pre_dist_1  }")

    best_imrp, best_i, best_j = two_op_cap(
        route1, distance_matrix=distance_matrix, penalty=0.0, penalty_matrix=pen_matrix
    )
    print(best_i)
    print(best_j)
    print(f"theory: {best_imrp}")
    routes = [route1]
    implement_two_op(routes, 0, best_i, best_j)
    route1 = routes[0]
    print(route1)
    # route2 = routes[1]

    aft_dist_1 = sum_route_dist(distance_matrix=distance_matrix, route=route1)
    # aft_dist_2= sum_route_dist(distance_matrix=distance_matrix,route=route2)

    print(f"aft_dist: {aft_dist_1  }")

    print(f"act dist: {(aft_dist_1  ) - (pre_dist_1  )}")
    # elevation_matrix,time_matrix,fill_rates,weights,vehicle,penalty_matrix = gen_test()

    # routes,_ = near_neighbor_gen(elevation_matrix,time_matrix,fill_rates,weights,vehicle)
    # test_route = routes[0]
    # print(test_route)
    """
    total_height_change = 0
    for idx, point in enumerate(test_route[:-1]):
        elevations = elevation_matrix[point][test_route[idx+1]]
        sum_height = 0
        pre_distance = 0
        for ele_idx, elevation_point in enumerate(elevations):
            height = math.tan(elevation_point[1]) * (elevation_point[0] - pre_distance)
            pre_distance = elevation_point[0]
            sum_height += height 
        total_height_change += sum_height
        #print(f"point: {point}")
        #print(f"height: {sum_height}")
        #print(f"total height: {total_height_change}")
        #print()

    print(total_height_change)
    """
    """

    route_energy_pre,_ = calculate_route_energy(route=test_route,elevation_matrix=elevation_matrix,time_matrix=time_matrix,vehicle=vehicle,weights=weights)
    print(test_route)
    print(f"Energy before: {route_energy_pre}")

    route_gen_after,best_i,best_j = two_op(route=test_route,_a=[],elevation_matrix=elevation_matrix,time_matrix=time_matrix,penalty_matrix=penalty_matrix,_volumes=fill_rates,weights=weights,vehicle=vehicle,penalty=0.1)

    print(f"Energy diff theory: {route_gen_after}")
    print(f"Energy after theory: {route_energy_pre+route_gen_after}")

    implement_two_op(routes,0 ,0,best_i,best_j)

    route = routes[0]

    route_gen_after_real,_ = calculate_route_energy(route=route,elevation_matrix=elevation_matrix,time_matrix=time_matrix,vehicle=vehicle,weights=weights)

    print(f"Energy after actual: {route_gen_after_real}")

    print(f"Energy diff: {route_gen_after_real - route_energy_pre}")

    print(route)
    """
