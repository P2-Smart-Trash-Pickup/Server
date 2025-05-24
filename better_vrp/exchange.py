import random
from copy import copy

from calculate_energy import calculate_route_energy, calculate_segment_energy_points
from help_heuristics import (
    get_max_empty,
    get_penalty,
    is_weekend,
    sum_route_dist,
    sum_route_time,
    sum_route_weight_volume,
    update_weight_matrix,
    volume_to_weight,
)
from nearest_neighbor import near_neighbor_gen
from test_vrp import gen_test, gen_test_dist
from vehicle import Vehicle


def calculate_diff_exchange(
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    route1: list[int],
    route2: list[int],
    point_1: int,
    point_2: int,
    r_1_idx: int,
    r_2_idx: int,
    r1_vehicle: Vehicle,
    r2_vehicle: Vehicle,
    r1_weights: list[float],
    r2_weights: list[float],
    r1_penalty_matrix: list[list[int]],
    r2_penalty_matrix: list[list[int]],
    penalty: float,
    stop_delay: float,
) -> tuple[float, float, float, float, float, float]:
    # Get points
    pre_1_val = route1[r_1_idx - 1]
    next_1_val = route1[r_1_idx + 1]

    pre_2_val = route2[r_2_idx - 1]
    next_2_val = route2[r_2_idx + 1]

    extra_1_mass = sum_route_weight_volume(route1[: r_1_idx + 1], r1_weights)
    extra_2_mass = sum_route_weight_volume(route2[: r_2_idx + 1], r1_weights)

    p_1_m_1 = r1_weights[point_1]
    p_1_m_2 = r2_weights[point_1]

    p_2_m_1 = r1_weights[point_2]
    p_2_m_2 = r2_weights[point_2]

    old_1_pre_cost, old_1_pen_pre_cost, old_1_pre_time = (
        calculate_segment_energy_points(
            point1=pre_1_val,
            point2=point_1,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r1_vehicle,
            penalty_matrix=r1_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_1_mass - p_1_m_1,
        )
    )
    old_1_next_cost, old_1_pen_next_cost, old_1_next_time = (
        calculate_segment_energy_points(
            point1=point_1,
            point2=next_1_val,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r1_vehicle,
            penalty_matrix=r1_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_1_mass,
        )
    )

    old_2_pre_cost, old_2_pen_pre_cost, old_2_pre_time = (
        calculate_segment_energy_points(
            point1=pre_2_val,
            point2=point_2,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r2_vehicle,
            penalty_matrix=r2_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_2_mass - p_2_m_2,
        )
    )
    old_2_next_cost, old_2_pen_next_cost, old_2_next_time = (
        calculate_segment_energy_points(
            point1=point_2,
            point2=next_2_val,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r2_vehicle,
            penalty_matrix=r2_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_2_mass,
        )
    )

    new_1_pre_cost, new_1_pen_pre_cost, new_1_pre_time = (
        calculate_segment_energy_points(
            point1=pre_1_val,
            point2=point_2,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r1_vehicle,
            penalty_matrix=r1_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_1_mass - p_1_m_1,
        )
    )
    new_1_next_cost, new_1_pen_next_cost, new_1_next_time = (
        calculate_segment_energy_points(
            point1=point_2,
            point2=next_1_val,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r1_vehicle,
            penalty_matrix=r1_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_1_mass - p_1_m_1 + p_2_m_1,
        )
    )

    new_2_pre_cost, new_2_pen_pre_cost, new_2_pre_time = (
        calculate_segment_energy_points(
            point1=pre_2_val,
            point2=point_1,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r2_vehicle,
            penalty_matrix=r2_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_2_mass - p_2_m_2,
        )
    )
    new_2_next_cost, new_2_pen_next_cost, new_2_next_time = (
        calculate_segment_energy_points(
            point1=point_1,
            point2=next_2_val,
            elevation_matrix=elevation_matrix,
            time_matrix=time_matrix,
            vehicle=r2_vehicle,
            penalty_matrix=r2_penalty_matrix,
            penalty=penalty,
            extra_mass=extra_2_mass - p_2_m_2 + p_1_m_2,
        )
    )

    old_1_cost = old_1_pre_cost + old_1_next_cost
    old_2_cost = old_2_pre_cost + old_2_next_cost
    new_1_cost = new_1_pre_cost + new_1_next_cost
    new_2_cost = new_2_pre_cost + new_2_next_cost
    old_1_pen_cost = old_1_pen_pre_cost + old_1_pen_next_cost
    old_2_pen_cost = old_2_pen_pre_cost + old_2_pen_next_cost
    new_1_pen_cost = new_1_pen_pre_cost + new_1_pen_next_cost
    new_2_pen_cost = new_2_pen_pre_cost + new_2_pen_next_cost

    diff_1_cost = new_1_cost - old_1_cost
    diff_2_cost = new_2_cost - old_2_cost

    diff_1_pen_cost = new_1_pen_cost - old_1_pen_cost
    diff_2_pen_cost = new_2_pen_cost - old_2_pen_cost

    old_1_time = old_1_pre_time + old_1_next_time
    old_2_time = old_2_pre_time + old_2_next_time

    new_1_time = new_1_pre_time + new_1_next_time
    new_2_time = new_2_pre_time + new_2_next_time

    diff_1_time = new_1_time - old_1_time
    diff_2_time = new_2_time - old_2_time

    return (
        diff_1_cost,
        diff_2_cost,
        diff_1_pen_cost,
        diff_2_pen_cost,
        diff_1_time,
        diff_2_time,
    )


def exchange_en(
    route1: list[int],
    route2: list[int],
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    r1_penalty_matrix: list[list[int]],
    r2_penalty_matrix: list[list[int]],
    r1_volumes: list[float],
    r2_volumes: list[float],
    r1_weights: list[float],
    r2_weights: list[float],
    r1_vehicle: Vehicle,
    r2_vehicle: Vehicle,
    penalty: float,
    stop_delay: float,
) -> tuple[float, int, int]:
    best_improvement = float("inf")

    base_r1_weights = sum_route_weight_volume(route1, r1_weights)
    base_r1_volume = sum_route_weight_volume(route1, r1_volumes)
    base_r1_time = sum_route_time(route1, time_matrix, stop_delay)

    base_r2_weights = sum_route_weight_volume(route2, r2_weights)
    base_r2_volume = sum_route_weight_volume(route2, r2_volumes)
    base_r2_time = sum_route_time(route2, time_matrix, stop_delay)

    base_r1_power_consumption, _ = calculate_route_energy(
        route=route1,
        elevation_matrix=elevation_matrix,
        time_matrix=time_matrix,
        vehicle=r1_vehicle,
        weights=r1_weights,
    )
    base_r2_power_consumption, _ = calculate_route_energy(
        route=route2,
        elevation_matrix=elevation_matrix,
        time_matrix=time_matrix,
        vehicle=r2_vehicle,
        weights=r2_weights,
    )
    best_i = 0
    best_j = 0

    for r_1_idx in range(1, len(route1) - 1):
        point_1 = route1[r_1_idx]
        point_1_weight = r1_weights[point_1]
        point_1_volume = r1_volumes[point_1]
        if base_r2_weights + point_1_weight > r2_vehicle.max_capacity:
            continue
        if base_r2_volume + point_1_volume > r2_vehicle.max_volume:
            continue

        for r_2_idx in range(1, len(route2) - 1):
            point_2 = route2[r_2_idx]

            point_2_weight = r2_weights[point_2]
            point_2_volume = r2_volumes[point_2]

            if base_r1_weights + point_2_weight > r1_vehicle.max_capacity:
                continue
            if base_r1_volume + point_2_volume > r1_vehicle.max_volume:
                continue

            (
                diff_1_cost,
                diff_2_cost,
                diff_1_pen_cost,
                diff_2_pen_cost,
                diff_1_time,
                diff_2_time,
            ) = calculate_diff_exchange(
                elevation_matrix=elevation_matrix,
                time_matrix=time_matrix,
                route1=route1,
                route2=route2,
                point_1=point_1,
                point_2=point_2,
                r_1_idx=r_1_idx,
                r_2_idx=r_2_idx,
                penalty=penalty,
                r1_vehicle=r1_vehicle,
                r2_vehicle=r2_vehicle,
                r1_weights=r1_weights,
                r2_weights=r2_weights,
                r1_penalty_matrix=r1_penalty_matrix,
                r2_penalty_matrix=r2_penalty_matrix,
                stop_delay=stop_delay,
            )
            pen_cost_diff = diff_1_pen_cost + diff_2_pen_cost

            if base_r1_power_consumption + diff_1_cost > r1_vehicle.battery_capacity:
                continue
            if base_r2_power_consumption + diff_2_cost > r2_vehicle.battery_capacity:
                continue
            if base_r1_time + diff_1_time > r1_vehicle.time_constraint:
                continue
            if base_r2_time + diff_2_time > r1_vehicle.time_constraint:
                continue

            if pen_cost_diff < best_improvement:
                best_improvement = pen_cost_diff
                best_i = r_1_idx
                best_j = r_2_idx

    return best_improvement, best_i, best_j


def exchange_multi_day_en(
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
    day_period = len(day_plan)
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
        i_weights = weight_matrix[day_idx_i]
        i_pen_matrix = day_penalty_matrix[day_idx_i]
        r1_volumes = day_volume_matrix[day_idx_i]
        for day_idx_j in range(len(day_plan)):
            if is_weekend(day_idx_j):
                continue
            cur_day_j = day_plan[day_idx_j]
            j_weights = weight_matrix[day_idx_j]
            j_pen_matrix = day_penalty_matrix[day_idx_j]
            r2_volumes = day_volume_matrix[day_idx_j]

            for route_idx_i in range(len(cur_day_i)):
                route_i = cur_day_i[route_idx_i]
                vehicle_i = vehicles[route_idx_i]
                for route_idx_j in range(len(cur_day_j)):
                    route_j = cur_day_j[route_idx_j]
                    if route_idx_i == route_idx_j and day_idx_j is day_idx_i:
                        continue
                    vehicle_j = vehicles[route_idx_j]

                    temp_best_cost, temp_i, temp_j = exchange_en(
                        route1=route_i,
                        route2=route_j,
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        penalty=penalty,
                        r1_penalty_matrix=i_pen_matrix,
                        r2_penalty_matrix=j_pen_matrix,
                        r1_weights=i_weights,
                        r2_weights=j_weights,
                        stop_delay=stop_delay,
                        r2_vehicle=vehicle_j,
                        r1_vehicle=vehicle_i,
                        r1_volumes=r1_volumes,
                        r2_volumes=r2_volumes,
                    )

                    if temp_best_cost >= 0:
                        continue
                    point_i = route_i[temp_i]

                    point_j = route_j[temp_j]

                    if point_i in route_j or point_j in route_i:
                        continue

                    i_empty_interval = empty_interval[point_i]
                    j_empty_interval = empty_interval[point_j]

                    temp_i_days_in = copy(days_in[point_i])
                    if day_idx_i not in temp_i_days_in:
                        print(point_i)
                        print(temp_i_days_in)
                    temp_i_days_in.remove(day_idx_i)
                    temp_i_days_in.append(day_idx_j)
                    temp_i_days_in.sort()
                    max_i_empty = get_max_empty(temp_i_days_in, day_period)
                    if max_i_empty > i_empty_interval:
                        continue

                    temp_j_days_in = copy(days_in[point_j])
                    if day_idx_j not in temp_j_days_in:
                        print(point_j)
                        print(temp_j_days_in)
                    temp_j_days_in.remove(day_idx_j)
                    temp_j_days_in.append(day_idx_i)
                    temp_j_days_in.sort()
                    max_j_empty = get_max_empty(temp_j_days_in, day_period)
                    if max_j_empty > j_empty_interval:
                        continue

                    if temp_best_cost < best_improvement:
                        best_improvement = temp_best_cost
                        best_i = temp_i
                        best_j = temp_j
                        best_day_i = day_idx_i
                        best_day_j = day_idx_j
                        best_route_i = route_idx_i
                        best_route_j = route_idx_j

    return (
        best_improvement,
        best_i,
        best_j,
        best_route_i,
        best_route_j,
        best_day_i,
        best_day_j,
    )


def get_ex_rel(
    pre_point: int,
    cur_point: int,
    next_point: int,
    distance_matrix: list[list[float]],
    penalty_matrix: list[list[int]],
    penalty: float,
) -> float:
    return get_penalty(
        i=pre_point,
        j=cur_point,
        distance_matrix=distance_matrix,
        penalty_matrix=penalty_matrix,
        penalty=penalty,
    ) + get_penalty(
        i=cur_point,
        j=next_point,
        distance_matrix=distance_matrix,
        penalty_matrix=penalty_matrix,
        penalty=penalty,
    )


def get_time_ex(
    pre_point: int, cur_point: int, next_point: int, time_matrix: list[list[float]]
) -> float:
    return time_matrix[pre_point][cur_point] + time_matrix[cur_point][next_point]


def exchange_cap(
    route1: list[int],
    route2: list[int],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    r1_pen_matrix: list[list[int]],
    r2_pen_matrix: list[list[int]],
    penalty: float,
    r1_vehicle: Vehicle,
    r2_vehicle: Vehicle,
    stop_delay: float,
    r1_weights: list[float],
    r2_weights,
) -> tuple[float, int, int]:

    best_improvement = float("inf")

    base_weight_r2 = sum_route_weight_volume(route2, r2_weights)
    base_time_r2 = sum_route_time(route2, time_matrix, stop_delay)

    base_weight_r1 = sum_route_weight_volume(route1, r1_weights)
    base_time_r1 = sum_route_time(route1, time_matrix, stop_delay)
    best_i = 0
    best_j = 0

    for r_1_idx in range(1, len(route1) - 1):
        point_1 = route1[r_1_idx]
        point_weight_1 = r1_weights[point_1]
        pre_1 = route1[r_1_idx - 1]
        next_1 = route1[r_1_idx + 1]

        old_1_cost = get_ex_rel(
            pre_1,
            point_1,
            next_1,
            distance_matrix=distance_matrix,
            penalty_matrix=r1_pen_matrix,
            penalty=penalty,
        )
        old_1_time = get_time_ex(pre_1, point_1, next_1, time_matrix=time_matrix)

        for r_2_idx in range(1, len(route2) - 1):

            pre_2 = route2[r_2_idx - 1]
            point_2 = route2[r_2_idx]
            next_2 = route2[r_2_idx + 1]

            point_weight_2 = r2_weights[point_2]

            if (
                base_weight_r2 + point_weight_1 - point_weight_2
                > r2_vehicle.max_capacity
            ):
                continue

            if (
                base_weight_r1 + point_weight_2 - point_weight_1
                > r1_vehicle.max_capacity
            ):
                continue

            old_2_cost = get_ex_rel(
                pre_2,
                point_2,
                next_2,
                distance_matrix=distance_matrix,
                penalty_matrix=r2_pen_matrix,
                penalty=penalty,
            )

            new_1_cost = get_ex_rel(
                pre_1,
                point_2,
                next_1,
                distance_matrix=distance_matrix,
                penalty_matrix=r1_pen_matrix,
                penalty=penalty,
            )
            new_2_cost = get_ex_rel(
                pre_2,
                point_1,
                next_2,
                distance_matrix=distance_matrix,
                penalty_matrix=r1_pen_matrix,
                penalty=penalty,
            )

            new_1_time = get_time_ex(pre_1, point_2, next_1, time_matrix=time_matrix)

            diff_time_1 = new_1_time - old_1_time
            if base_time_r1 + diff_time_1 + stop_delay > r1_vehicle.time_constraint:
                continue

            new_2_time = get_time_ex(pre_2, point_1, next_2, time_matrix=time_matrix)

            old_2_time = get_time_ex(pre_2, point_2, next_2, time_matrix=time_matrix)

            diff_time_2 = new_2_time - old_2_time

            if base_time_r2 + diff_time_2 + stop_delay > r2_vehicle.time_constraint:
                continue

            pen_cost_diff = (new_2_cost + new_1_cost) - (old_2_cost + old_1_cost)

            if pen_cost_diff < best_improvement:
                best_improvement = pen_cost_diff
                best_i = r_1_idx
                best_j = r_2_idx

    return best_improvement, best_i, best_j


def exchange_days_cap(
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
    day_period = len(day_plan)
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
        i_weights = weight_matrix[day_idx_i]
        i_pen_matrix = day_penalty_matrix[day_idx_i]
        for day_idx_j in range(len(day_plan)):
            if is_weekend(day_idx_j):
                continue
            cur_day_j = day_plan[day_idx_j]
            j_weights = weight_matrix[day_idx_j]
            j_pen_matrix = day_penalty_matrix[day_idx_j]

            for route_idx_i in range(len(cur_day_i)):
                route_i = cur_day_i[route_idx_i]
                vehicle_i = vehicles[route_idx_i]
                for route_idx_j in range(len(cur_day_j)):

                    route_j = cur_day_j[route_idx_j]
                    if route_idx_i == route_idx_j and day_idx_j is day_idx_i:
                        continue
                    vehicle_j = vehicles[route_idx_j]

                    temp_best_cost, temp_i, temp_j = exchange_cap(
                        route1=route_i,
                        route2=route_j,
                        distance_matrix=distance_matrix,
                        time_matrix=time_matrix,
                        penalty=penalty,
                        r1_pen_matrix=i_pen_matrix,
                        r2_pen_matrix=j_pen_matrix,
                        r1_weights=i_weights,
                        r2_weights=j_weights,
                        stop_delay=stop_delay,
                        r2_vehicle=vehicle_j,
                        r1_vehicle=vehicle_i,
                    )

                    if temp_best_cost >= 0:
                        continue
                    point_i = route_i[temp_i]

                    point_j = route_j[temp_j]

                    if point_i in route_j or point_j in route_i:
                        continue

                    i_empty_interval = empty_interval[point_i]
                    j_empty_interval = empty_interval[point_j]

                    temp_i_days_in = copy(days_in[point_i])
                    if day_idx_i not in temp_i_days_in:
                        print(point_i)
                        print(temp_i_days_in)
                    temp_i_days_in.remove(day_idx_i)
                    temp_i_days_in.append(day_idx_j)
                    temp_i_days_in.sort()
                    max_i_empty = get_max_empty(temp_i_days_in, day_period)
                    if max_i_empty > i_empty_interval:
                        continue

                    temp_j_days_in = copy(days_in[point_j])
                    if day_idx_j not in temp_j_days_in:
                        print(point_j)
                        print(temp_j_days_in)
                    temp_j_days_in.remove(day_idx_j)
                    temp_j_days_in.append(day_idx_i)
                    temp_j_days_in.sort()
                    max_j_empty = get_max_empty(temp_j_days_in, day_period)
                    if max_j_empty > j_empty_interval:
                        continue

                    if temp_best_cost < best_improvement:
                        best_improvement = temp_best_cost
                        best_i = temp_i
                        best_j = temp_j
                        best_day_i = day_idx_i
                        best_day_j = day_idx_j
                        best_route_i = route_idx_i
                        best_route_j = route_idx_j

    return (
        best_improvement,
        best_i,
        best_j,
        best_route_i,
        best_route_j,
        best_day_i,
        best_day_j,
    )


def implement_exchange(
    routes: list[list[int]], route1_idx: int, route2_idx: int, best_i: int, best_j: int
):

    route_1 = routes[route1_idx]
    route_2 = routes[route2_idx]
    route_1[best_i], route_2[best_j] = route_2[best_j], route_1[best_i]
    routes[route1_idx] = route_1
    routes[route2_idx] = route_2


def implement_exchange_day(
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
    day_i = day_plan[best_day_i]
    day_j = day_plan[best_day_j]

    route_i = day_i[best_route_i]
    route_j = day_j[best_route_j]

    point_i = route_i[best_i]
    point_j = route_j[best_j]

    days_in[point_i].remove(best_day_i)
    days_in[point_i].append(best_day_j)

    update_weight_matrix(
        day_period=len(day_plan),
        days_in=days_in,
        point=point_i,
        weight_matrix=weight_matrix,
        fill_rates=fill_rates,
    )

    days_in[point_j].remove(best_day_j)
    days_in[point_j].append(best_day_i)

    update_weight_matrix(
        day_period=len(day_plan),
        days_in=days_in,
        point=point_j,
        weight_matrix=weight_matrix,
        fill_rates=fill_rates,
    )

    route_i[best_i], route_j[best_j] = route_j[best_j], route_i[best_i]
    if len(set(route_i)) - len(route_i) != -1:
        raise Exception("Duplicate point")
    if len(set(route_j)) - len(route_j) != -1:
        raise Exception("Duplicate point")


def implement_exchange_day_en(
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
    day_i = day_plan[best_day_i]
    day_j = day_plan[best_day_j]

    route_i = day_i[best_route_i]
    route_j = day_j[best_route_j]

    point_i = route_i[best_i]
    point_j = route_j[best_j]

    days_in[point_i].remove(best_day_i)
    days_in[point_i].append(best_day_j)

    update_weight_matrix(
        day_period=len(day_plan),
        days_in=days_in,
        point=point_i,
        weight_matrix=volume_matrix,
        fill_rates=fill_rates,
    )

    days_in[point_j].remove(best_day_j)
    days_in[point_j].append(best_day_i)

    update_weight_matrix(
        day_period=len(day_plan),
        days_in=days_in,
        point=point_j,
        weight_matrix=volume_matrix,
        fill_rates=fill_rates,
    )

    for day_idx in range(len(volume_matrix)):
        for point_idx in range(len(volume_matrix[day_idx])):
            weight_matrix[day_idx][point_idx] = volume_to_weight(
                volume_matrix[day_idx][point_idx]
            )

    route_i[best_i], route_j[best_j] = route_j[best_j], route_i[best_i]
    if len(set(route_i)) - len(route_i) != -1:
        raise Exception("Duplicate point")
    if len(set(route_j)) - len(route_j) != -1:
        raise Exception("Duplicate point")


if __name__ == "__main__":

    # elevation_matrix,time_matrix,fill_rates,weights,vehicle,penalty_matrix = gen_test()
    distance_matrix, time_matrix, _, max_fill, vehicle, pen_matrix = gen_test_dist()
    # routes,_ = near_neighbor_gen(elevation_matrix=elevation_matrix,time_matrix=time_matrix,volumes=fill_rates,weights=weights,vehicle=vehicle)
    customers = [i for i in range(1, len(distance_matrix))]
    test_cust = random.sample(customers, 20)
    route1 = [0] + test_cust[:11] + [0]
    route2 = [0] + test_cust[11:] + [0]
    pre_dist_1 = sum_route_dist(distance_matrix=distance_matrix, route=route1)
    pre_dist_2 = sum_route_dist(distance_matrix=distance_matrix, route=route2)

    print(f"pre_dist: {pre_dist_1 + pre_dist_2}")

    best_imrp, best_i, best_j = exchange_cap(
        route1,
        route2,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        r2_vehicle=vehicle,
        penalty=0.0,
        r1_pen_matrix=pen_matrix,
        r2_pen_matrix=pen_matrix,
        stop_delay=30000,
        r1_weights=max_fill,
        r2_weights=max_fill,
        r1_vehicle=vehicle,
    )
    print(f"theory: {best_imrp}")
    routes = [route1, route2]
    implement_exchange(routes, 0, 1, best_i, best_j)
    route1 = routes[0]
    route2 = routes[1]

    aft_dist_1 = sum_route_dist(distance_matrix=distance_matrix, route=route1)
    aft_dist_2 = sum_route_dist(distance_matrix=distance_matrix, route=route2)

    print(f"aft_dist: {aft_dist_1 + aft_dist_2}")

    print(f"act dist: {(aft_dist_1 + aft_dist_2) - (pre_dist_1 + pre_dist_2)}")
    """
    elevation_matrix,time_matrix,fill_rates,weights,vehicle,penalty_matrix = gen_test()
    routes,_ = near_neighbor_gen(elevation_matrix=elevation_matrix,time_matrix=time_matrix,volumes=fill_rates,weights=weights,vehicle=vehicle)
    en1,_ = calculate_route_energy(route=routes[-2],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    en2,_ = calculate_route_energy(route=routes[-1],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    old_cost = en1 + en2

    print(f"pre cost: {old_cost}")

    improvement,besti,bestj = exchange(route1=routes[-2],route2=routes[-1],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty=0.0,penalty_matrix=penalty_matrix,vehicle=vehicle,volumes=fill_rates)
    print(besti)

    print(bestj)
    implement_exchange(routes,-2,-1,besti,bestj)

    print(f"theory : {improvement}")

    en1,_ = calculate_route_energy(route=routes[-2],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    en2,_ = calculate_route_energy(route=routes[-1],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    new_cost = en1 + en2

    print(f"new cost: {new_cost}")
    print(f"diff: {new_cost-old_cost}")

    """
