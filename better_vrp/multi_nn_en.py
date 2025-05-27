import random
import json
from calculate_energy import calculate_route_energy, calculate_segment_energy_points
from gls import gls, gls_en
from vehicle import Vehicle
from help_heuristics import (
    gen_weight_day_matrix,
    sum_route_time,
    sum_route_weight_volume,
    sum_route_dist,
    get_max_empty,
    is_weekend,
    volume_to_weight,
)
from test_vrp import gen_test, gen_test_dist

from copy import copy, deepcopy
import math
from tqdm import tqdm
from file_manipulation import load_date_molok, load_moloks


def near_neighbor_compare_best_en(
    unassigned_points: list[int],
    current_route: list[int],
    time_matrix: list[list[float]],
    elevation_matrix: list[list[list[list[float]]]],
    volumes: list[float],
    weights: list[float],
    current_vehicle: Vehicle,
    sum_weight: float,
    sum_volume: float,
    sum_power: float,
    sum_time: float,
    stop_time: float,
) -> tuple[float, int, int, float, float, float]:

    best_cost = float("inf")
    best_k = 0
    best_insert = 0
    best_time_diff = 0
    k_weight = 0
    k_volume = 0
    for v_k in unassigned_points:
        v_k_weight = weights[v_k]
        v_k_volume = volumes[v_k]

        if v_k_weight + sum_weight > current_vehicle.max_capacity:
            continue
        if v_k_volume + sum_volume > current_vehicle.max_volume:
            continue

        for idx in range(len(current_route) - 1):
            current_point = current_route[idx]
            next_point = current_route[idx + 1]
            old_weights = sum_route_weight_volume(
                route=current_route[: idx + 1], weights=weights
            )
            old_distance = calculate_segment_energy_points(
                point1=current_point,
                point2=next_point,
                elevation_matrix=elevation_matrix,
                time_matrix=time_matrix,
                penalty_matrix=[],
                penalty=None,
                vehicle=current_vehicle,
                extra_mass=old_weights,
            )[0]
            old_time = time_matrix[current_point][next_point]

            new_distance_prefix = calculate_segment_energy_points(
                point1=current_point,
                point2=v_k,
                elevation_matrix=elevation_matrix,
                time_matrix=time_matrix,
                penalty_matrix=[],
                penalty=None,
                vehicle=current_vehicle,
                extra_mass=old_weights,
            )[0]

            new_distance_suffix = calculate_segment_energy_points(
                point1=v_k,
                point2=next_point,
                elevation_matrix=elevation_matrix,
                time_matrix=time_matrix,
                penalty_matrix=[],
                penalty=None,
                vehicle=current_vehicle,
                extra_mass=old_weights + v_k_weight,
            )[0]

            new_time_prefix = time_matrix[current_point][v_k]
            new_time_suffix = time_matrix[v_k][next_point]

            cost_diff = (new_distance_suffix + new_distance_prefix) - old_distance
            time_diff = (new_time_prefix + new_time_suffix) - old_time

            if sum_time + time_diff + stop_time > current_vehicle.time_constraint:
                continue
            if sum_power + cost_diff > current_vehicle.battery_capacity:
                continue
            if cost_diff < best_cost:
                k_weight = v_k_weight
                k_volume = v_k_volume
                best_cost = cost_diff
                best_k = v_k
                best_insert = idx + 1
                best_time_diff = time_diff
    return best_cost, best_k, best_insert, best_time_diff, k_weight, k_volume


def assign_no_due(
    days: list[list[list[int]]],
    no_dues: list[int],
    time_matrix: list[list[float]],
    elevation_matrix: list[list[list[list[float]]]],
    fill_rates: list[float],
    inital_fill: list[float],
    vehicles: list[Vehicle],
    days_in: list[list[int]],
    empty_intervals: list[int],
    stop_time: float,
    weight_matrix: list[list[float]],
    volume_matrix: list[list[float]],
) -> list[list[list[int]]]:
    p_bar = tqdm(total=len(no_dues))
    day_period = len(days)

    while no_dues:

        best_overall_cost = float("inf")
        best_overall_k = None
        best_day = 0
        best_route = 0
        best_insertion = 0

        for day_idx in range(len(days)):
            if is_weekend(day_idx):
                continue
            routes = days[day_idx]

            # print()
            # print(f"{day_idx} : {routes[0]}")
            weights = weight_matrix[day_idx]
            volumes = volume_matrix[day_idx]

            temp_unassigned = copy(no_dues)
            for point in no_dues:
                if day_idx in days_in[point]:
                    temp_unassigned.remove(point)
            for route_idx in range(len(routes)):
                route = routes[route_idx]
                sum_weight = sum_route_weight_volume(route, weights)
                sum_volume = sum_route_weight_volume(route, volumes)
                sum_time = sum_route_time(route, time_matrix, stop_time)
                current_vehicle = vehicles[route_idx]
                sum_power, _ = calculate_route_energy(
                    route=route,
                    elevation_matrix=elevation_matrix,
                    time_matrix=time_matrix,
                    weights=weights,
                    vehicle=current_vehicle,
                )

                best_cost, best_k, best_insert, _, _, _ = near_neighbor_compare_best_en(
                    sum_power=sum_power,
                    elevation_matrix=elevation_matrix,
                    volumes=volumes,
                    weights=weights,
                    sum_weight=sum_weight,
                    sum_volume=sum_volume,
                    current_route=route,
                    time_matrix=time_matrix,
                    current_vehicle=current_vehicle,
                    unassigned_points=temp_unassigned,
                    sum_time=sum_time,
                    stop_time=stop_time,
                )
                if best_k in days[day_idx][0] and best_cost < float("inf"):
                    print("")
                    print(f"BEST K: {best_k}")
                    print(f"DAYS IN: {days_in[best_k]}")
                    raise Exception("HOW")

                if best_cost < best_overall_cost:
                    best_overall_cost = best_cost
                    best_day = day_idx
                    best_route = route_idx
                    best_insertion = best_insert
                    best_overall_k = best_k
        if not best_overall_k:
            print("removing points")
            removed_point = False
            for i in range(len(elevation_matrix)):
                if empty_intervals[i] == 0:
                    continue
                did_optimize = empty_intervals[i] <= day_period
                while did_optimize:
                    did_optimize = False
                    temp_days = copy(days_in[i])
                    temp_days.sort()
                    for idx in range(len(temp_days)):
                        pre_day = temp_days[idx - 1]
                        cur_day = temp_days[idx]

                        next_i = (idx + 1) % len(temp_days)
                        next_day = temp_days[next_i]
                        pre_diff = 0
                        if pre_day >= cur_day:
                            pre_diff = day_period - abs(cur_day - pre_day)
                        else:
                            pre_diff = cur_day - pre_day
                        next_diff = 0
                        if cur_day >= next_day:
                            next_diff = day_period - abs(cur_day - next_day)
                        else:
                            next_diff = next_day - cur_day

                        if pre_diff + next_diff <= empty_intervals[i]:
                            removed_point = True
                            did_optimize = True
                            routes = days[cur_day]
                            for route in routes:
                                if best_overall_k in route:
                                    route.remove(best_overall_k)
                            days_in[i].remove(cur_day)
                        break

            volume_matrix = gen_weight_day_matrix(
                [0.0 for _ in elevation_matrix],
                fill_rates=fill_rates,
                day_period=day_period,
                days_in=days_in,
            )

            weight_matrix = gen_weight_day_matrix(
                [0.0 for _ in elevation_matrix],
                fill_rates=fill_rates,
                day_period=day_period,
                days_in=days_in,
            )

            for day_idx in range(len(volume_matrix)):
                for point_idx in range(len(volume_matrix[day_idx])):
                    weight_matrix[day_idx][point_idx] = volume_to_weight(
                        volume_matrix[day_idx][point_idx]
                    )
            if not removed_point:
                raise Exception("WOOSH")
            else:
                continue
        days[best_day][best_route].insert(best_insertion, best_overall_k)
        days_in[best_overall_k].append(best_day)

        volume_matrix = gen_weight_day_matrix(
            [0.0 for _ in elevation_matrix],
            fill_rates=fill_rates,
            day_period=day_period,
            days_in=days_in,
        )

        weight_matrix = gen_weight_day_matrix(
            [0.0 for _ in elevation_matrix],
            fill_rates=fill_rates,
            day_period=day_period,
            days_in=days_in,
        )

        for day_idx in range(len(volume_matrix)):
            for point_idx in range(len(volume_matrix[day_idx])):
                weight_matrix[day_idx][point_idx] = volume_to_weight(
                    volume_matrix[day_idx][point_idx]
                )

        days_in[best_overall_k].sort()
        max_empty = get_max_empty(days_in[best_overall_k], day_period)

        if max_empty <= empty_intervals[best_overall_k]:
            no_dues.remove(best_overall_k)
            p_bar.update(1)

    for day_idx in range(len(elevation_matrix)):
        if empty_intervals[day_idx] == 0:
            continue
        temp_days_in = days_in[day_idx]
        temp_empty = empty_intervals[day_idx]
        temp_max_empty = get_max_empty(temp_days_in, day_period)
        if temp_max_empty > temp_empty:
            print(f"day: {day_idx}")
            print(f"empt interval: {day_idx}")
            print(f"max empty: {day_idx}")
            raise Exception("Shizzy lizzy")

    p_bar.close()

    return days


def near_neighbor_multi_day_en(
    elevation_matrix: list[list[list[list[float]]]],
    due_dates: list[list[int]],
    no_due: list[int],
    time_matrix: list[list[float]],
    fill_rates: list[float],
    inital_fill: list[float],
    empty_intervals: list[int],
    vehicles: list[Vehicle],
    days_in: list[list[int]],
    day_period: int,
    stop_time: float,
    weight_matrix: list[list[float]],
    volume_matrix: list[list[float]],
) -> list[list[list[int]]]:
    days = [[] for _ in range(len(due_dates))]

    if not days:
        for i in range(day_period):
            if is_weekend(i):
                days.append([[]])
                continue
            days.append([[0, 0] for _ in vehicles])

    assign_no_due(
        days=days,
        no_dues=no_due,
        elevation_matrix=elevation_matrix,
        volume_matrix=volume_matrix,
        time_matrix=time_matrix,
        fill_rates=fill_rates,
        inital_fill=inital_fill,
        vehicles=vehicles,
        days_in=days_in,
        empty_intervals=empty_intervals,
        stop_time=stop_time,
        weight_matrix=weight_matrix,
    )
    if no_due:
        raise Exception(f"points remaining {no_due}")
    # print(f"NO DUE: {no_due}")
    # print(f"max vehicle: {sum_vehicle_capacity}")

    """
    for day,routes in enumerate(days):
        for route in routes:
            print(f"day {day}: {route}")
            print(f"all fill {day}: {sum(day_fills[day])}")
            print(f"spare capacity: {sum_vehicle_capacity - sum(day_fills[day])}")
    """
    # print(f"due dates: {due_dates}")

    return days


def multi_nn_en(
    time_matrix: list[list[float]],
    fill_rates: list[float],
    vehicles: list[Vehicle],
    inital_fill: list[float],
    day_period: int,
    empty_intervals: list[int],
    stop_time: float,
    weight_matrix: list[list[float]],
    volume_matrix: list[list[float]],
    elevation_matrix: list[list[list[list[float]]]],
) -> list[list[list[int]]]:
    due_dates = []
    no_due = [i for i in range(1, len(elevation_matrix)) if empty_intervals[i] != 0]
    days_in = [[] for _ in elevation_matrix]
    day_plan = near_neighbor_multi_day_en(
        volume_matrix=volume_matrix,
        elevation_matrix=elevation_matrix,
        inital_fill=inital_fill,
        due_dates=due_dates,
        no_due=no_due,
        time_matrix=time_matrix,
        fill_rates=fill_rates,
        empty_intervals=empty_intervals,
        vehicles=vehicles,
        days_in=days_in,
        day_period=day_period,
        stop_time=stop_time,
        weight_matrix=weight_matrix,
    )
    return day_plan


if __name__ == "__main__":
    (
        elevation_matrix,
        time_matrix,
        max_volumes,
        fill_rates,
        weights,
        vehicle,
        penalty_matrix,
    ) = gen_test()

    date_molok = load_date_molok()
    all_moloks = load_moloks()

    day_period = 14
    with open("./nord_fill.json", "r") as f:
        nord_fills = json.load(f)

    nord_days = []
    base = date_molok["2025"]
    march = base["3"]
    april = base["4"]
    m = march["31"]

    new_route = [0]
    for con in m:
        adress = con["adress"]
        for indx in range(len(all_moloks)):
            if all_moloks[indx]["adress"] == adress:
                new_route.append(indx)
                break

    new_route = list(dict.fromkeys(new_route))
    new_route.append(0)
    nord_days.append([new_route])
    for day_idx in range(1, 14):
        if day_idx == 5 or day_idx == 6 or day_idx == 12 or day_idx == 13:
            nord_days.append([[]])
            continue
        a = april[str(day_idx)]

        new_route = [0]
        for con in a:
            adress = con["adress"]
            for indx in range(len(all_moloks)):
                if all_moloks[indx]["adress"] == adress:
                    new_route.append(indx)
                    break
        new_route = list(dict.fromkeys(new_route))
        new_route.append(0)
        nord_days.append([new_route])
    # base_nord = deepcopy(nord_days)

    with open("../data/default_nord_plan.json", "w") as f:
        json.dump(nord_days, f)

    vehicle_amount = 1
    vehicles = [copy(vehicle) for _ in range(vehicle_amount)]

    nord_real_days_in = [[] for _ in all_moloks]
    for i in range(len(all_moloks)):
        for day_idx, day in enumerate(nord_days):
            for route in day:
                if i in route:
                    nord_real_days_in[i].append(day_idx)

    """
    for i in range(1, len(elevation_matrix)):
        nord_fill = nord_fills[i]
        max_f = max_volumes[i]
        fill_rates[i] = (max_f / day_period) * nord_fill
    """

    for idx in range(1, len(nord_real_days_in)):
        if len(nord_real_days_in[idx]) == 0:
            fill_rates[idx] = 0
        else:
            max_f = max_volumes[idx]
            fill_rates[idx] = (max_f / 14) * len(nord_real_days_in[idx]) * 0.5
    fill_rates[0] = 0

    stop_time = 300000
    weights = [0.0]
    empty_intervals = [0]

    for idx in range(1, len(max_volumes)):
        max_f = max_volumes[idx]
        fill_rate = fill_rates[idx]
        if fill_rate == 0:
            weights.append(0.0)
            empty_intervals.append(0)
            continue
        procent_diff = max_f / fill_rate
        empty_intervals.append(math.floor(procent_diff))
        fill_proc = random.uniform(0, procent_diff)
        # weights.append(fill_proc*fill_rate)
        weights.append(0.0)

    """
    weight_matrix = gen_weight_day_matrix(
        weights, fill_rates, day_period, nord_real_days_in
    )
    """

    """
    volume_matrix = gen_weight_day_matrix(
        [0.0 for _ in elevation_matrix],
        fill_rates=fill_rates,
        day_period=day_period,
        days_in=nord_real_days_in,
    )

    weight_matrix = gen_weight_day_matrix(
        [0.0 for _ in elevation_matrix],
        fill_rates=fill_rates,
        day_period=day_period,
        days_in=nord_real_days_in,
    )

    for day_idx in range(len(volume_matrix)):
        for point_idx in range(len(volume_matrix[day_idx])):
            weight_matrix[day_idx][point_idx] = volume_to_weight(
                volume_matrix[day_idx][point_idx]
            )

    base_volume_matrix = deepcopy(volume_matrix)
    base_weight_matrix = deepcopy(weight_matrix)

    for day_idx in range(len(volume_matrix)):
        for point_idx in range(len(volume_matrix[day_idx])):
            weight_matrix[day_idx][point_idx] = volume_to_weight(
                volume_matrix[day_idx][point_idx]
            )

    pre_nord_total_dist = sum(
        [
            sum(
                [
                    calculate_route_energy(
                        route=i,
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        weights=weight_matrix[day_idx],
                        vehicle=vehicles[r_idx],
                    )[0]
                    for r_idx, i in enumerate(routes)
                ]
            )
            for day_idx, routes in enumerate(nord_days)
        ]
    )

    print(f"pre nord dist: {pre_nord_total_dist}")

    nord_day_penalty_matrix = [
        [[0 for _ in all_moloks] for _ in all_moloks] for _ in range(day_period)
    ]

    best_nord_plan = gls_en(
        day_plan=nord_days,
        elevation_matrix=elevation_matrix,
        volume_matrix=volume_matrix,
        time_matrix=time_matrix,
        penalty=0.2,
        day_penalty_matrix=nord_day_penalty_matrix,
        vehicles=vehicles,
        stop_delay=stop_time,
        weight_matrix=weight_matrix,
        days_in=nord_real_days_in,
        empty_intervals=empty_intervals,
        max_iter=50,
        max_no_improve=100,
        debug_iter=10,
        fill_rates=fill_rates,
    )

    nord_total_dist = sum(
        [
            sum(
                [
                    calculate_route_energy(
                        route=i,
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        weights=weight_matrix[day_idx],
                        vehicle=vehicles[r_idx],
                    )[0]
                    for r_idx, i in enumerate(routes)
                ]
            )
            for day_idx, routes in enumerate(nord_days)
        ]
    )

    print(f"aft nord dist: {nord_total_dist}")
    print(f"diff nord: {nord_total_dist - pre_nord_total_dist}")

    with open("../data/optimized_nord_energy.json", "w") as f:
        json.dump(best_nord_plan, f)
    """

    nn_volume_matrix = gen_weight_day_matrix(
        [0.0 for _ in elevation_matrix],
        fill_rates=fill_rates,
        day_period=day_period,
        days_in=[[] for _ in elevation_matrix],
    )

    nn_weight_matrix = gen_weight_day_matrix(
        [0.0 for _ in elevation_matrix],
        fill_rates=fill_rates,
        day_period=day_period,
        days_in=[[] for _ in elevation_matrix],
    )

    for day_idx in range(len(nn_volume_matrix)):
        for point_idx in range(len(nn_volume_matrix[day_idx])):
            nn_weight_matrix[day_idx][point_idx] = volume_to_weight(
                nn_volume_matrix[day_idx][point_idx]
            )

    day_plan = multi_nn_en(
        volume_matrix=nn_volume_matrix,
        elevation_matrix=elevation_matrix,
        time_matrix=time_matrix,
        vehicles=vehicles,
        inital_fill=weights,
        fill_rates=fill_rates,
        day_period=day_period,
        empty_intervals=empty_intervals,
        stop_time=stop_time,
        weight_matrix=nn_weight_matrix,
    )

    real_days_in = [[] for _ in all_moloks]
    for i in range(len(all_moloks)):
        for day_idx, day in enumerate(day_plan):
            for route in day:
                if i in route:
                    real_days_in[i].append(day_idx)
                    break

    day_volume_matrix = gen_weight_day_matrix(
        [0.0 for _ in elevation_matrix],
        fill_rates=fill_rates,
        day_period=day_period,
        days_in=real_days_in,
    )

    day_weight_matrix = gen_weight_day_matrix(
        [0.0 for _ in elevation_matrix],
        fill_rates=fill_rates,
        day_period=day_period,
        days_in=real_days_in,
    )

    for day_idx in range(len(day_volume_matrix)):
        for point_idx in range(len(day_volume_matrix[day_idx])):
            day_weight_matrix[day_idx][point_idx] = volume_to_weight(
                day_volume_matrix[day_idx][point_idx]
            )

    day_penalty_matrix = [
        [[0 for _ in all_moloks] for _ in all_moloks] for _ in range(day_period)
    ]

    pre_day_diff = sum(
        [
            sum(
                [
                    calculate_route_energy(
                        route=i,
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        weights=day_weight_matrix[day_idx],
                        vehicle=vehicles[r_idx],
                    )[0]
                    for r_idx, i in enumerate(routes)
                ]
            )
            for day_idx, routes in enumerate(day_plan)
        ]
    )

    print(f"pre day dist: {pre_day_diff}")

    best_day_plan = gls_en(
        day_plan=day_plan,
        elevation_matrix=elevation_matrix,
        volume_matrix=day_volume_matrix,
        time_matrix=time_matrix,
        penalty=0.2,
        day_penalty_matrix=day_penalty_matrix,
        vehicles=vehicles,
        stop_delay=stop_time,
        weight_matrix=day_weight_matrix,
        days_in=real_days_in,
        empty_intervals=empty_intervals,
        max_iter=50,
        max_no_improve=10,
        debug_iter=10,
        fill_rates=fill_rates,
    )

    base_total_dist = sum(
        [
            sum(
                [
                    calculate_route_energy(
                        route=i,
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        weights=day_weight_matrix[day_idx],
                        vehicle=vehicles[r_idx],
                    )[0]
                    for r_idx, i in enumerate(routes)
                ]
            )
            for day_idx, routes in enumerate(best_day_plan)
        ]
    )

    print(f"aft base dist: {base_total_dist}")
    print(f"diff base: {base_total_dist- pre_day_diff}")

    real_days_in = [[] for _ in all_moloks]
    for i in range(len(all_moloks)):
        for day_idx, day in enumerate(best_day_plan):
            for route in day:
                if i in route:
                    real_days_in[i].append(day_idx)
                    break

    # print(f"diff nord: {nord_total_dist- pre_nord_total_dist}")

    """
    print("NORD")
    for dayx_idx, routes in enumerate(best_nord_plan):
        for route_idx in range(len(routes)):
            print(f"{dayx_idx}:{route_idx}: {best_nord_plan[dayx_idx][route_idx]}")
        print()
    """

    print("BASE")
    for dayx_idx, routes in enumerate(best_day_plan):
        for route_idx in range(len(routes)):
            print(f"{dayx_idx}:{route_idx}: {best_day_plan[dayx_idx][route_idx]}")
        print()
    with open(f"optimized_day_{day_period}.json", "w") as f:
        json.dump(best_day_plan, f)

    for day_idx in range(1, len(elevation_matrix)):
        if empty_intervals[day_idx] == 0:
            continue
        temp_days_in = real_days_in[day_idx]
        temp_empty = empty_intervals[day_idx]
        temp_max_empty = get_max_empty(temp_days_in, day_period)
        if temp_max_empty > temp_empty:
            print(f"day: {day_idx}")
            print(f"empt interval: {temp_empty}")
            print(f"max empty: {temp_max_empty}")
            print(f"days in: {temp_days_in}")
            raise Exception("GLS IS SUSSY")
