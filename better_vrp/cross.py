from calculate_energy import calculate_route_energy, calculate_segment_energy_points


from vehicle import Vehicle
from help_heuristics import (
    get_penalty,
    sum_route_dist,
    sum_route_weight_volume,
    sum_route_time,
    get_max_empty,
    is_weekend,
    update_weight_matrix,
    volume_to_weight,
)
from test_vrp import gen_test, gen_test_dist
from nearest_neighbor import near_neighbor_gen
import random
from copy import copy
from multiprocessing import Pool


def calculate_diff_cross(
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    route1: list[int],
    route2: list[int],
    point_1_idx: int,
    point_2_idx: int,
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

    old_sub_r1_route = route1[point_1_idx:]
    old_sub_r2_route = route2[point_2_idx:]

    suffix_1 = route1[point_1_idx + 1 :]
    suffix_2 = route2[point_2_idx + 1 :]

    time_moved_1 = stop_delay * len(suffix_1)
    time_moved_2 = stop_delay * len(suffix_2)

    new_sub_r1_route = [route1[point_1_idx]] + suffix_2
    new_sub_r2_route = [route2[point_2_idx]] + suffix_1

    old_r1_time = sum_route_time(old_sub_r1_route, time_matrix)
    old_r2_time = sum_route_time(old_sub_r2_route, time_matrix)

    new_r1_time = sum_route_time(new_sub_r1_route, time_matrix)
    new_r2_time = sum_route_time(new_sub_r2_route, time_matrix)

    old_r1_cost, old_r1_pen_cost = calculate_route_energy(
        route=old_sub_r1_route,
        time_matrix=time_matrix,
        elevation_matrix=elevation_matrix,
        weights=r1_weights,
        penalty_matrix=r1_penalty_matrix,
        penalty=penalty,
        vehicle=r1_vehicle,
    )

    old_r2_cost, old_r2_pen_cost = calculate_route_energy(
        route=old_sub_r2_route,
        time_matrix=time_matrix,
        elevation_matrix=elevation_matrix,
        weights=r2_weights,
        penalty_matrix=r2_penalty_matrix,
        penalty=penalty,
        vehicle=r2_vehicle,
    )

    new_r1_cost, new_r1_pen_cost = calculate_route_energy(
        route=new_sub_r1_route,
        time_matrix=time_matrix,
        elevation_matrix=elevation_matrix,
        weights=r1_weights,
        penalty_matrix=r1_penalty_matrix,
        penalty=penalty,
        vehicle=r1_vehicle,
    )

    new_r2_cost, new_r2_pen_cost = calculate_route_energy(
        route=new_sub_r2_route,
        time_matrix=time_matrix,
        elevation_matrix=elevation_matrix,
        weights=r2_weights,
        penalty_matrix=r2_penalty_matrix,
        penalty=penalty,
        vehicle=r2_vehicle,
    )

    diff_1_cost = new_r1_cost - old_r1_cost
    diff_2_cost = new_r2_cost - old_r2_cost

    diff_1_pen_cost = new_r1_pen_cost - old_r1_pen_cost
    diff_2_pen_cost = new_r2_pen_cost - old_r2_pen_cost

    diff_1_time = new_r1_time - old_r1_time + time_moved_2 - time_moved_1
    diff_2_time = new_r2_time - old_r2_time + time_moved_1 - time_moved_2

    return (
        diff_1_cost,
        diff_2_cost,
        diff_1_pen_cost,
        diff_2_pen_cost,
        diff_1_time,
        diff_2_time,
    )


def calculate_diff_cross_wrapper(arg: dict):

    elevation_matrix = arg["elevation_matrix"]
    time_matrix = arg["time_matrix"]
    route1 = arg["route1"]
    route2 = arg["route2"]
    point_1_idx = arg["point_1_idx"]
    point_2_idx = arg["point_2_idx"]
    r1_vehicle = arg["r1_vehicle"]
    r2_vehicle = arg["r2_vehicle"]
    r1_weights = arg["r1_weights"]
    r2_weights = arg["r2_weights"]
    r1_penalty_matrix = arg["r1_penalty_matrix"]
    r2_penalty_matrix = arg["r2_penalty_matrix"]
    penalty = arg["penalty"]
    stop_delay = arg["stop_delay"]

    return calculate_diff_cross(
        elevation_matrix=elevation_matrix,
        time_matrix=time_matrix,
        route1=route1,
        route2=route2,
        point_1_idx=point_1_idx,
        point_2_idx=point_2_idx,
        r1_penalty_matrix=r1_penalty_matrix,
        r2_penalty_matrix=r2_penalty_matrix,
        r1_weights=r1_weights,
        r2_weights=r2_weights,
        r1_vehicle=r1_vehicle,
        r2_vehicle=r2_vehicle,
        penalty=penalty,
        stop_delay=stop_delay,
    )


def cross_en_paralel(
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

    base_r1_time = sum_route_time(route1, time_matrix)

    base_r2_time = sum_route_time(route2, time_matrix)

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
    tasks = []
    for r_1_idx, point_1 in enumerate(route1[:-1]):
        for r_2_idx, point_2 in enumerate(route2[:-1]):
            tasks.append(
                {
                    "elevation_matrix": elevation_matrix,
                    "time_matrix": time_matrix,
                    "route1": route1,
                    "route2": route2,
                    "point_1_idx": r_1_idx,
                    "point_2_idx": r_2_idx,
                    "point_1": point_1,
                    "point_2": point_2,
                    "r1_penalty_matrix": r1_penalty_matrix,
                    "r2_penalty_matrix": r2_penalty_matrix,
                    "r1_weights": r1_weights,
                    "r2_weights": r2_weights,
                    "r1_vehicle": r1_vehicle,
                    "r2_vehicle": r2_vehicle,
                    "penalty": penalty,
                    "stop_delay": stop_delay,
                }
            )
    with Pool() as pool:
        results = pool.map(calculate_diff_cross_wrapper, tasks, chunksize=100)
    for task, result in zip(tasks, results):
        r_1_idx = task["point_1_idx"]
        r_2_idx = task["point_2_idx"]

        point_1 = task["point_1"]
        point_2 = task["point_2"]

        try:
            (
                diff_1_cost,
                diff_2_cost,
                diff_1_pen_cost,
                diff_2_pen_cost,
                diff_1_time,
                diff_2_time,
            ) = result

            pen_cost_diff = diff_1_pen_cost + diff_2_pen_cost

            if base_r1_power_consumption + diff_1_cost > r1_vehicle.battery_capacity:
                continue
            if base_r2_power_consumption + diff_2_cost > r2_vehicle.battery_capacity:
                continue
            if base_r1_time + diff_1_time > r1_vehicle.time_constraint:
                continue
            if base_r2_time + diff_2_time > r2_vehicle.time_constraint:
                continue

            if pen_cost_diff < best_improvement:
                test_r1_swap = route1[: point_1 + 1] + route2[point_2 + 1 :]
                test_r2_swap = route2[: point_2 + 1] + route1[point_1 + 1 :]

                new_r1_weight = sum_route_weight_volume(test_r1_swap, r1_weights)
                new_r2_weight = sum_route_weight_volume(test_r2_swap, r2_weights)

                new_r1_volume = sum_route_weight_volume(test_r1_swap, r1_volumes)
                new_r2_volume = sum_route_weight_volume(test_r2_swap, r2_volumes)

                if (
                    new_r1_weight > r1_vehicle.max_capacity
                    or new_r2_weight > r2_vehicle.max_capacity
                ):
                    continue

                if (
                    new_r1_volume > r1_vehicle.max_volume
                    or new_r2_volume > r2_vehicle.max_volume
                ):
                    continue

                best_improvement = pen_cost_diff
                best_i = r_1_idx
                best_j = r_2_idx
        except Exception as e:
            print(f"Task failed: {e}")
    return best_improvement, best_i, best_j


def cross_en(
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

    base_r1_time = sum_route_time(route1, time_matrix)

    base_r2_time = sum_route_time(route2, time_matrix)

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

    for r_1_idx, point_1 in enumerate(route1[:-1]):

        for r_2_idx, point_2 in enumerate(route2[:-1]):

            (
                diff_1_cost,
                diff_2_cost,
                diff_1_pen_cost,
                diff_2_pen_cost,
                diff_1_time,
                diff_2_time,
            ) = calculate_diff_cross(
                elevation_matrix=elevation_matrix,
                time_matrix=time_matrix,
                route1=route1,
                route2=route2,
                point_1_idx=r_1_idx,
                point_2_idx=r_2_idx,
                r1_penalty_matrix=r1_penalty_matrix,
                r2_penalty_matrix=r2_penalty_matrix,
                r1_weights=r1_weights,
                r2_weights=r2_weights,
                r1_vehicle=r1_vehicle,
                r2_vehicle=r2_vehicle,
                penalty=penalty,
                stop_delay=stop_delay,
            )
            pen_cost_diff = diff_1_pen_cost + diff_2_pen_cost

            if base_r1_power_consumption + diff_1_cost > r1_vehicle.battery_capacity:
                continue
            if base_r2_power_consumption + diff_2_cost > r2_vehicle.battery_capacity:
                continue
            if base_r1_time + diff_1_time > r1_vehicle.time_constraint:
                continue
            if base_r2_time + diff_2_time > r2_vehicle.time_constraint:
                continue

            if pen_cost_diff < best_improvement:
                test_r1_swap = route1[: point_1 + 1] + route2[point_2 + 1 :]
                test_r2_swap = route2[: point_2 + 1] + route1[point_1 + 1 :]

                new_r1_weight = sum_route_weight_volume(test_r1_swap, r1_weights)
                new_r2_weight = sum_route_weight_volume(test_r2_swap, r2_weights)

                new_r1_volume = sum_route_weight_volume(test_r1_swap, r1_volumes)
                new_r2_volume = sum_route_weight_volume(test_r2_swap, r2_volumes)

                if (
                    new_r1_weight > r1_vehicle.max_capacity
                    or new_r2_weight > r2_vehicle.max_capacity
                ):
                    continue

                if (
                    new_r1_volume > r1_vehicle.max_volume
                    or new_r2_volume > r2_vehicle.max_volume
                ):
                    continue

                best_improvement = pen_cost_diff
                best_i = r_1_idx
                best_j = r_2_idx

    return best_improvement, best_i, best_j


def cross_multi_day_en(
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
        i_penalty_matrix = day_penalty_matrix[day_idx_i]
        r1_volumes = day_volume_matrix[day_idx_i]
        for day_idx_j in range(len(day_plan)):
            if is_weekend(day_idx_j):
                continue
            cur_day_j = day_plan[day_idx_j]
            j_weights = weight_matrix[day_idx_j]
            j_penalty_matrix = day_penalty_matrix[day_idx_j]

            r2_volumes = day_volume_matrix[day_idx_j]

            for route_idx_i in range(len(cur_day_i)):
                route_i = cur_day_i[route_idx_i]
                vehicle_i = vehicles[route_idx_i]
                for route_idx_j in range(len(cur_day_j)):
                    route_j = cur_day_j[route_idx_j]
                    if route_idx_i == route_idx_j and route_i is route_j:
                        continue
                    vehicle_j = vehicles[route_idx_j]

                    temp_best_cost, temp_i, temp_j = cross_en_paralel(
                        route1=route_i,
                        route2=route_j,
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        penalty=penalty,
                        r1_penalty_matrix=i_penalty_matrix,
                        r2_penalty_matrix=j_penalty_matrix,
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

                    i_is_valid = True

                    for point_i in route_i[temp_i + 1 : -1]:
                        if point_i in route_j:
                            i_is_valid = False
                            break
                        i_empty_interval = empty_interval[point_i]
                        temp_i_days_in = copy(days_in[point_i])
                        if day_idx_i not in temp_i_days_in:
                            print(point_i)
                            print(temp_i_days_in)
                        temp_i_days_in.remove(day_idx_i)
                        temp_i_days_in.append(day_idx_j)
                        temp_i_days_in.sort()
                        max_i_empty = get_max_empty(temp_i_days_in, day_period)
                        if max_i_empty > i_empty_interval:
                            i_is_valid = False
                            break
                    if not i_is_valid:
                        continue

                    j_is_valid = True

                    for point_j in route_j[temp_j + 1 : -1]:
                        if point_j in route_i:
                            j_is_valid = False
                            break
                        j_empty_interval = empty_interval[point_j]
                        temp_j_days_in = copy(days_in[point_j])
                        if day_idx_j not in temp_j_days_in:
                            print(point_j)
                            print(temp_j_days_in)
                        temp_j_days_in.remove(day_idx_j)
                        temp_j_days_in.append(day_idx_i)
                        temp_j_days_in.sort()
                        max_j_empty = get_max_empty(temp_j_days_in, day_period)
                        if max_j_empty > j_empty_interval:
                            j_is_valid = False
                            break
                    if not j_is_valid:
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


def cross_cap(
    route1: list[int],
    route2: list[int],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    r1_penalty_matrix: list[list[int]],
    r2_penalty_matrix: list[list[int]],
    penalty: float,
    r1_vehicle: Vehicle,
    r2_vehicle: Vehicle,
    stop_delay: float,
    r1_weights: list[float],
    r2_weights: list[float],
) -> tuple[float, int, int]:

    best_improvement = float("inf")

    base_weight_r2 = sum_route_weight_volume(route2, r2_weights)
    base_time_r2 = sum_route_time(route2, time_matrix, stop_delay)

    base_weight_r1 = sum_route_weight_volume(route1, r1_weights)
    base_time_r1 = sum_route_time(route1, time_matrix, stop_delay)
    best_i = 0
    best_j = 0

    for r_1_idx in range(len(route1) - 1):
        point_1 = route1[r_1_idx]
        point_weight_1 = sum_route_weight_volume(route1[r_1_idx + 1 :], r1_weights)
        next_1 = route1[r_1_idx + 1]

        old_1_cost = get_penalty(
            point_1,
            next_1,
            penalty_matrix=r1_penalty_matrix,
            penalty=penalty,
            distance_matrix=distance_matrix,
        )
        old_1_time = sum(
            [
                time_matrix[route1[i]][route1[i + 1]]
                for i in range(r_1_idx + 1, len(route1) - 1)
            ]
        ) + stop_delay * (len(route1) - r_1_idx - 1)

        for r_2_idx in range(len(route2) - 1):
            point_2 = route2[r_2_idx]
            next_2 = route2[r_2_idx + 1]

            point_weight_2 = sum_route_weight_volume(route2[r_2_idx + 1 :], r2_weights)

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

            old_2_cost = get_penalty(
                point_2,
                next_2,
                penalty_matrix=r2_penalty_matrix,
                penalty=penalty,
                distance_matrix=distance_matrix,
            )
            old_2_time = (
                sum(
                    [
                        time_matrix[route2[i]][route2[i + 1]]
                        for i in range(r_2_idx + 1, len(route2) - 1)
                    ]
                )
                * stop_delay
                * (len(route2) - r_2_idx - 1)
            )

            new_1_cost = get_penalty(
                point_1,
                next_2,
                penalty_matrix=r1_penalty_matrix,
                penalty=penalty,
                distance_matrix=distance_matrix,
            )
            new_2_cost = get_penalty(
                point_2,
                next_1,
                penalty_matrix=r2_penalty_matrix,
                penalty=penalty,
                distance_matrix=distance_matrix,
            )

            if (
                base_time_r1 - old_1_time + old_2_time + stop_delay
                > r1_vehicle.time_constraint
            ):
                continue

            if (
                base_time_r2 + old_1_time - old_2_time + stop_delay
                > r2_vehicle.time_constraint
            ):
                continue

            pen_cost_diff = (new_2_cost + new_1_cost) - (old_2_cost + old_1_cost)

            if pen_cost_diff < best_improvement:
                best_improvement = pen_cost_diff
                best_i = r_1_idx
                best_j = r_2_idx

    return best_improvement, best_i, best_j


def cross_days_cap(
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
        i_penalty_matrix = day_penalty_matrix[day_idx_i]
        for day_idx_j in range(len(day_plan)):
            if is_weekend(day_idx_j):
                continue
            cur_day_j = day_plan[day_idx_j]
            j_weights = weight_matrix[day_idx_j]
            j_penalty_matrix = day_penalty_matrix[day_idx_j]

            for route_idx_i in range(len(cur_day_i)):
                route_i = cur_day_i[route_idx_i]
                vehicle_i = vehicles[route_idx_i]
                for route_idx_j in range(len(cur_day_j)):
                    route_j = cur_day_j[route_idx_j]
                    if route_idx_i == route_idx_j and route_i is route_j:
                        continue
                    vehicle_j = vehicles[route_idx_j]

                    temp_best_cost, temp_i, temp_j = cross_cap(
                        route1=route_i,
                        route2=route_j,
                        distance_matrix=distance_matrix,
                        time_matrix=time_matrix,
                        penalty=penalty,
                        r1_penalty_matrix=i_penalty_matrix,
                        r2_penalty_matrix=j_penalty_matrix,
                        r1_weights=i_weights,
                        r2_weights=j_weights,
                        stop_delay=stop_delay,
                        r2_vehicle=vehicle_j,
                        r1_vehicle=vehicle_i,
                    )
                    if temp_best_cost >= 0:
                        continue

                    i_is_valid = True

                    for point_i in route_i[temp_i + 1 : -1]:
                        if point_i in route_j:
                            i_is_valid = False
                            break
                        i_empty_interval = empty_interval[point_i]
                        temp_i_days_in = copy(days_in[point_i])
                        if day_idx_i not in temp_i_days_in:
                            print(point_i)
                            print(temp_i_days_in)
                        temp_i_days_in.remove(day_idx_i)
                        temp_i_days_in.append(day_idx_j)
                        temp_i_days_in.sort()
                        max_i_empty = get_max_empty(temp_i_days_in, day_period)
                        if max_i_empty > i_empty_interval:
                            i_is_valid = False
                            break
                    if not i_is_valid:
                        continue

                    j_is_valid = True

                    for point_j in route_j[temp_j + 1 : -1]:
                        if point_j in route_i:
                            j_is_valid = False
                            break
                        j_empty_interval = empty_interval[point_j]
                        temp_j_days_in = copy(days_in[point_j])
                        if day_idx_j not in temp_j_days_in:
                            print(point_j)
                            print(temp_j_days_in)
                        temp_j_days_in.remove(day_idx_j)
                        temp_j_days_in.append(day_idx_i)
                        temp_j_days_in.sort()
                        max_j_empty = get_max_empty(temp_j_days_in, day_period)
                        if max_j_empty > j_empty_interval:
                            j_is_valid = False
                            break
                    if not j_is_valid:
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


def implement_cross(
    routes: list[list[int]], route1_idx: int, route2_idx: int, best_i: int, best_j: int
):
    route1 = routes[route1_idx]
    route2 = routes[route2_idx]

    prefix_1 = route1[: best_i + 1]
    prefix_2 = route2[: best_j + 1]

    suffix_1 = route1[best_i + 1 :]
    suffix_2 = route2[best_j + 1 :]

    route1 = prefix_1 + suffix_2
    route2 = prefix_2 + suffix_1

    routes[route1_idx] = route1
    routes[route2_idx] = route2


def implement_cross_day(
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

    prefix_1 = route_i[: best_i + 1]
    prefix_2 = route_j[: best_j + 1]

    suffix_1 = route_i[best_i + 1 :]
    suffix_2 = route_j[best_j + 1 :]

    try:
        for point_i in suffix_1[:-1]:
            days_in[point_i].remove(best_day_i)
            days_in[point_i].append(best_day_j)

            update_weight_matrix(
                day_period=len(day_plan),
                days_in=days_in,
                point=point_i,
                weight_matrix=weight_matrix,
                fill_rates=fill_rates,
            )

        for point_j in suffix_2[:-1]:
            days_in[point_j].remove(best_day_j)
            days_in[point_j].append(best_day_i)

            update_weight_matrix(
                day_period=len(day_plan),
                days_in=days_in,
                point=point_j,
                weight_matrix=weight_matrix,
                fill_rates=fill_rates,
            )

        route1 = prefix_1 + suffix_2
        route2 = prefix_2 + suffix_1

        day_i[best_route_i] = route1
        day_j[best_route_j] = route2

        if len(set(route1)) - len(route1) != -1:
            print("Route 1")
            print(suffix_2)
            print(route1)
            raise Exception("Duplicate point")
        if len(set(route2)) - len(route2) != -1:
            print("Route 2")
            print(suffix_1)
            print(route2)
            raise Exception("Duplicate point")
    except:
        print(suffix_1)
        print(suffix_2)


def implement_cross_day_en(
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

    prefix_1 = route_i[: best_i + 1]
    prefix_2 = route_j[: best_j + 1]

    suffix_1 = route_i[best_i + 1 :]
    suffix_2 = route_j[best_j + 1 :]

    try:
        for point_i in suffix_1[:-1]:
            days_in[point_i].remove(best_day_i)
            days_in[point_i].append(best_day_j)

            update_weight_matrix(
                day_period=len(day_plan),
                days_in=days_in,
                point=point_i,
                weight_matrix=volume_matrix,
                fill_rates=fill_rates,
            )

        for point_j in suffix_2[:-1]:
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

        route1 = prefix_1 + suffix_2
        route2 = prefix_2 + suffix_1

        day_i[best_route_i] = route1
        day_j[best_route_j] = route2

        if len(set(route1)) - len(route1) != -1:
            print("Route 1")
            print(suffix_2)
            print(route1)
            raise Exception("Duplicate point")
        if len(set(route2)) - len(route2) != -1:
            print("Route 2")
            print(suffix_1)
            print(route2)
            raise Exception("Duplicate point")
    except:
        print(suffix_1)
        print(suffix_2)


if __name__ == "__main__":
    # elevation_matrix,time_matrix,fill_rates,weights,vehicle,penalty_matrix = gen_test()
    distance_matrix, time_matrix, _, max_fill, vehicle, pen_matrix = gen_test_dist()
    # routes,_ = near_neighbor_gen(elevation_matrix=elevation_matrix,time_matrix=time_matrix,volumes=fill_rates,weights=weights,vehicle=vehicle)
    customers = [i for i in range(1, len(distance_matrix))]
    test_cust = random.sample(customers, 20)
    route1 = [0] + test_cust[:11] + [0]
    route2 = [0] + test_cust[11:] + [0]

    print(route1)
    print(route2)
    pre_dist_1 = sum_route_dist(distance_matrix=distance_matrix, route=route1)
    pre_dist_2 = sum_route_dist(distance_matrix=distance_matrix, route=route2)

    print(f"pre_dist: {pre_dist_1 + pre_dist_2}")

    best_imrp, best_i, best_j = cross_cap(
        route1,
        route2,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        r2_vehicle=vehicle,
        penalty=0.0,
        r1_penalty_matrix=pen_matrix,
        r2_penalty_matrix=pen_matrix,
        stop_delay=30000,
        r1_weights=max_fill,
        r2_weights=max_fill,
        r1_vehicle=vehicle,
    )
    print(f"theory: {best_imrp}")
    routes = [route1, route2]
    implement_cross(routes, 0, 1, best_i, best_j)
    route1 = routes[0]
    route2 = routes[1]
    print(route1)
    print(route2)

    aft_dist_1 = sum_route_dist(distance_matrix=distance_matrix, route=route1)
    aft_dist_2 = sum_route_dist(distance_matrix=distance_matrix, route=route2)

    print(f"aft_dist: {aft_dist_1 + aft_dist_2}")

    print(f"act dist: {(aft_dist_1 + aft_dist_2) - (pre_dist_1 + pre_dist_2)}")
    """
    elevation_matrix,time_matrix,fill_rates,weights,vehicle,penalty_matrix = gen_test()

    routes,_ = near_neighbor_gen(elevation_matrix=elevation_matrix,time_matrix=time_matrix,volumes=fill_rates,weights=weights,vehicle=vehicle)
    en1,_ = calculate_route_energy(route=routes[0],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    en2,_ = calculate_route_energy(route=routes[1],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    old_cost = en1 + en2

    print(f"pre cost: {old_cost}")
    improvement,besti,bestj = cross(route1=routes[0],route2=routes[1],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty=0.0,penalty_matrix=penalty_matrix,vehicle=vehicle,volumes=fill_rates)
    print(besti)

    print(bestj)
    implement_cross(routes,0,1,besti,bestj)

    print(f"theory : {improvement}")
    vehicle.current_mass = vehicle.initial_mass

    en1,_ = calculate_route_energy(route=routes[0],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    en2,_ = calculate_route_energy(route=routes[1],time_matrix=time_matrix,elevation_matrix=elevation_matrix,weights=weights,penalty_matrix=penalty_matrix,penalty=0.0,vehicle=vehicle)
    new_cost = en1 + en2

    print(f"new cost: {new_cost}")
    print(f"diff: {new_cost - old_cost}")
"""
