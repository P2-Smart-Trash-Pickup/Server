import random
import json
from calculate_energy import calculate_route_energy
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


def generate_days(
    fill_rates: list[float],
    max_fills: list[float],
    inital_fill: list[float],
    vehicles: list[Vehicle],
    day_period: int,
    day_fills: list[list[float]],
    days_in: list[list[int]],
) -> tuple[list[list[int]], list[int], list[list[float]], list[list[int]]]:

    due_dates = [[] for _ in range(day_period)]
    no_due = []
    sum_vehicle_capacity = sum([vehicle.max_capacity for vehicle in vehicles])

    for idx in tqdm(range(1, len(inital_fill)), desc="gen days"):
        current_fill = inital_fill[idx]
        max_fill = max_fills[idx]
        fill_rate = fill_rates[idx]
        empty_interval = empty_intervals[idx]
        if fill_rate == 0:
            continue

        due_date = math.floor((max_fill - current_fill) / fill_rate)

        if due_date >= day_period:
            no_due.append(idx)
            continue

        if due_date > (day_period - 1) % empty_interval:
            due_date = (day_period - 1) % empty_interval

        first_fill_date = -float("inf")
        latest_date = -float("inf")
        next_day = due_date
        pre_date = -1
        should_end = False
        while not should_end:
            if next_day <= latest_date and next_day > first_fill_date:
                break
            if next_day <= first_fill_date:
                should_end = True
                pre_date = -1

            day_fill = sum(day_fills[next_day])
            container_fill = inital_fill[idx] + fill_rates[idx] * next_day
            if day_fill + container_fill > sum_vehicle_capacity or is_weekend(next_day):
                did_swap = False
                for old_days in range(pre_date + 1, next_day)[::-1]:
                    old_fill = sum(day_fills[old_days])
                    other_fill = inital_fill[idx] + fill_rates[idx] * old_days
                    if old_fill + other_fill > sum_vehicle_capacity or is_weekend(
                        old_days
                    ):
                        continue
                    days_in[idx].append(old_days)
                    day_fills[old_days][idx] = other_fill
                    due_dates[old_days].append(idx)
                    pre_date = old_days

                    first_fill_date = (
                        old_days if first_fill_date < 0 else first_fill_date
                    )
                    latest_date = old_days if old_days > latest_date else latest_date
                    next_day = (old_days + empty_interval) % day_period

                    did_swap = True
                    break
                if not did_swap:
                    print(f"max vehicle: {sum_vehicle_capacity}")

                    for day_idx in range(len(due_dates)):
                        fill = sum(day_fills[day_idx])
                        print(f"{day_idx}: {fill}")
                    raise Exception("container placement not possible")
            else:

                days_in[idx].append(next_day)
                day_fills[next_day][idx] = container_fill
                due_dates[next_day].append(idx)
                pre_date = next_day

                first_fill_date = next_day if first_fill_date < 0 else first_fill_date
                latest_date = next_day if next_day > latest_date else latest_date
                next_day = (next_day + empty_interval) % day_period
            if empty_interval >= day_period:
                break

        did_optimize = True
        while did_optimize:
            if empty_interval >= day_period:
                break
            did_optimize = False
            inc_ind = []
            for day_idx in range(len(due_dates)):
                if idx in due_dates[day_idx]:
                    inc_ind.append(day_idx)

            for val_idx in range(len(inc_ind)):
                pre_val = inc_ind[val_idx - 1]
                cur_val = inc_ind[val_idx]
                next_val = inc_ind[(val_idx + 1) % len(inc_ind)]

                pre_diff = (
                    cur_val - pre_val
                    if cur_val > pre_val
                    else 14 - abs(cur_val - pre_val)
                )
                next_diff = (
                    next_val - cur_val
                    if next_val > cur_val
                    else 14 - abs(cur_val - next_val)
                )

                if pre_diff + next_diff <= empty_interval:
                    due_dates[cur_val].remove(idx)
                    days_in[idx].remove(cur_val)
                    day_fills[cur_val][idx] = 0
                    did_optimize = True
                    break

    return due_dates, no_due, day_fills, days_in


def near_neighbor_compare_best(
    unassigned_points: list[int],
    current_route: list[int],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    container_fills: list[float],
    current_vehicle: Vehicle,
    sum_fill: float,
    sum_time: float,
    stop_time: float,
) -> tuple[float, int, int, float, float]:

    best_cost = float("inf")
    best_k = 0
    k_fill = 0
    best_insert = 0
    best_time_diff = 0
    for v_k in unassigned_points:
        v_k_fill = container_fills[v_k]

        if v_k_fill + sum_fill > current_vehicle.max_capacity:

            continue
        for idx in range(len(current_route) - 1):
            current_point = current_route[idx]
            next_point = current_route[idx + 1]
            old_distance = distance_matrix[current_point][next_point]
            old_time = time_matrix[current_point][next_point]

            new_distance_prefix = distance_matrix[current_point][v_k]
            new_distance_suffix = distance_matrix[v_k][next_point]

            new_time_prefix = time_matrix[current_point][v_k]
            new_time_suffix = time_matrix[v_k][next_point]

            cost_diff = (new_distance_suffix + new_distance_prefix) - old_distance
            time_diff = (new_time_prefix + new_time_suffix) - old_time

            if sum_time + time_diff + stop_time > current_vehicle.time_constraint:
                continue

            if cost_diff < best_cost:
                k_fill = v_k_fill
                best_cost = cost_diff
                best_k = v_k
                best_insert = idx + 1
                best_time_diff = time_diff
    return best_cost, best_k, best_insert, best_time_diff, k_fill


def near_neighbor_gen(
    points: list[int],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    container_fills: list[float],
    vehicles: list[Vehicle],
    stop_time: float,
) -> tuple[list[list[int]], list[int]]:
    routes = []
    while points:
        if len(routes) >= len(vehicles):
            print("damn")
            break
        v_i = random.choice(points)
        points.remove(v_i)
        current_vehicle = vehicles[len(routes)]
        current_route = [0, v_i, 0]

        sum_fill = sum_route_weight_volume(current_route, container_fills)
        sum_time = sum_route_time(current_route, time_matrix, stop_time)
        while True:

            _, best_k, best_insert, best_time_diff, k_fill = near_neighbor_compare_best(
                current_route=current_route,
                distance_matrix=distance_matrix,
                time_matrix=time_matrix,
                container_fills=container_fills,
                current_vehicle=current_vehicle,
                unassigned_points=points,
                sum_fill=sum_fill,
                sum_time=sum_time,
                stop_time=stop_time,
            )
            if not best_k:
                break
            points.remove(best_k)
            current_route.insert(best_insert, best_k)
            sum_fill += k_fill
            sum_time += best_time_diff

        routes.append(current_route)

    return routes, points


def assign_no_due(
    days: list[list[list[int]]],
    no_dues: list[int],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    fill_rates: list[float],
    inital_fill: list[float],
    vehicles: list[Vehicle],
    day_fills: list[list[float]],
    days_in: list[list[int]],
    empty_intervals: list[int],
    stop_time: float,
    weight_matrix: list[list[float]],
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
            currrent_fill = weight_matrix[day_idx]
            for route_idx in range(len(routes)):
                route = routes[route_idx]
                sum_fill = sum_route_weight_volume(route, currrent_fill)
                sum_time = sum_route_time(route, time_matrix, stop_time)
                current_vehicle = vehicles[route_idx]
                best_cost, best_k, best_insert, _, _ = near_neighbor_compare_best(
                    current_route=route,
                    distance_matrix=distance_matrix,
                    time_matrix=time_matrix,
                    container_fills=currrent_fill,
                    current_vehicle=current_vehicle,
                    unassigned_points=no_dues,
                    sum_fill=sum_fill,
                    sum_time=sum_time,
                    stop_time=stop_time,
                )

                if best_cost < best_overall_cost:
                    best_overall_cost = best_cost
                    best_day = day_idx
                    best_route = route_idx
                    best_insertion = best_insert
                    best_overall_k = best_k
        if not best_overall_k:
            for i, dag in enumerate(days_in):
                print(f"{i}: {dag}")
            # print(f"YOLO: {}")
            break
        p_bar.update(1)

        days[best_day][best_route].insert(best_insertion, best_overall_k)
        days_in[best_overall_k].append(best_day)
        day_fills[best_day][best_overall_k] = weight_matrix[best_day][best_overall_k]

        temp = copy(days_in[best_overall_k])
        temp.append(best_day)
        temp.sort()
        max_empty = get_max_empty(temp, day_period)
        # print(f"overall: {best_overall_k}")
        while max_empty > empty_intervals[best_overall_k]:

            best_temp_cost = float("inf")
            temp_k = None
            temp_insert = 0
            temp_day = 0
            temp_route = 0
            for day_idx in range(len(days)):
                if is_weekend(day_idx) or day_idx in days_in[best_overall_k]:
                    continue

                routes = days[day_idx]
                currrent_fill = weight_matrix[day_idx]

                for route_idx in range(len(routes)):
                    route = routes[route_idx]
                    sum_fill = sum_route_weight_volume(route, currrent_fill)
                    sum_time = sum_route_time(route, time_matrix, stop_time)
                    current_vehicle = vehicles[route_idx]
                    best_cost, best_k, best_insert, _, _ = near_neighbor_compare_best(
                        current_route=route,
                        distance_matrix=distance_matrix,
                        time_matrix=time_matrix,
                        container_fills=currrent_fill,
                        current_vehicle=current_vehicle,
                        unassigned_points=[best_overall_k],
                        sum_fill=sum_fill,
                        sum_time=sum_time,
                        stop_time=stop_time,
                    )
                    if best_cost < best_temp_cost:
                        best_temp_cost = best_cost
                        temp_k = best_k
                        temp_insert = best_insert
                        temp_day = day_idx
                        temp_route = route_idx
            if not temp_k:
                break

            # print(f"temp: {temp_k}")
            # print(days_in)
            days_in[temp_k].append(temp_day)
            days[temp_day][temp_route].insert(temp_insert, temp_k)
            day_fills[temp_day][temp_k] = weight_matrix[temp_day][temp_k]

            temp = copy(days_in[temp_k])
            temp.append(temp_day)
            temp.sort()
            max_empty = get_max_empty(temp, day_period)
        did_optimize = empty_intervals[best_overall_k] <= day_period
        while did_optimize:
            did_optimize = False
            temp_days = copy(days_in[best_overall_k])
            temp_days.sort()
            for idx in range(len(temp_days)):
                pre_day = temp_days[idx - 1]
                cur_day = temp_days[idx]

                next_i = (idx + 1) % len(temp_days)
                next_day = temp_days[next_i]
                pre_diff = 0
                if pre_day >= cur_day:
                    pre_diff = 14 - abs(cur_day - pre_day)
                else:
                    pre_diff = cur_day - pre_day
                next_diff = 0
                if cur_day >= next_day:
                    next_diff = 14 - abs(cur_day - next_day)
                else:
                    next_diff = next_day - cur_day

                if pre_diff + next_diff <= empty_intervals[best_overall_k]:
                    did_optimize = True
                    routes = days[cur_day]
                    for route in routes:
                        if best_overall_k in route:
                            route.remove(best_overall_k)
                    day_fills[cur_day][best_overall_k] = 0
                    days_in[best_overall_k].remove(cur_day)
                    break

        no_dues.remove(best_overall_k)

    p_bar.close()

    """
    for i,day in enumerate(days_in):
        print(f"{i}: {day}")
    """

    return days


def near_neighbor_multi_day(
    due_dates: list[list[int]],
    no_due: list[int],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    fill_rates: list[float],
    inital_fill: list[float],
    empty_intervals: list[int],
    vehicles: list[Vehicle],
    day_fills: list[list[float]],
    days_in: list[list[int]],
    day_period: int,
    stop_time: float,
    weight_matrix: list[list[float]],
) -> list[list[list[int]]]:
    days = [[] for _ in range(len(due_dates))]
    sum_vehicle_capacity = sum([vehicle.max_capacity for vehicle in vehicles])

    for day_idx in range(len(due_dates))[::-1]:
        if is_weekend(day_idx):
            days[day_idx] = [[]]
            continue
        due_points = due_dates[day_idx]
        routes, empty_points = near_neighbor_gen(
            points=due_points,
            distance_matrix=distance_matrix,
            time_matrix=time_matrix,
            container_fills=day_fills[day_idx],
            vehicles=vehicles,
            stop_time=stop_time,
        )
        empty_points = copy(empty_points)
        if len(empty_points) != 0:
            for point_idx in range(len(empty_points)):
                empty_point = empty_points[point_idx]
                empty_interval = empty_intervals[empty_point]
                did_switch = False
                for old_day_idx in range(day_idx)[::-1]:
                    old_day_fill = sum(day_fills[old_day_idx])
                    fill_at_day = (
                        inital_fill[point_idx] + fill_rates[point_idx] * old_day_idx
                    )

                    temp = copy(days_in[empty_point])
                    temp.remove(day_idx)
                    temp.append(old_day_idx)
                    temp.sort()
                    max_empty = get_max_empty(temp, day_period)
                    if (
                        fill_at_day + old_day_fill > sum_vehicle_capacity
                        or is_weekend(old_day_idx)
                        or max_empty > empty_interval
                    ):
                        continue
                    days_in[empty_point].remove(day_idx)
                    days_in[empty_point].append(old_day_idx)
                    due_dates[day_idx].remove(empty_point)
                    day_fills[day_idx][empty_point] = 0

                    due_dates[old_day_idx].append(empty_point)
                    day_fills[old_day_idx][empty_point] = fill_at_day
                    did_switch = True
                    break
                if not did_switch:
                    raise Exception("FOCKY")
        days[day_idx] = routes

    if not days:
        for i in range(day_period):
            if is_weekend(i):
                days.append([[]])
                continue
            days.append([[0, 0] for _ in vehicles])

    assign_no_due(
        days=days,
        no_dues=no_due,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        fill_rates=fill_rates,
        inital_fill=inital_fill,
        vehicles=vehicles,
        day_fills=day_fills,
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


def multi_nn(
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    max_fills: list[float],
    fill_rates: list[float],
    vehicles: list[Vehicle],
    inital_fill: list[float],
    day_period: int,
    empty_intervals: list[int],
    stop_time: float,
    weight_matrix: list[list[float]],
    with_due: bool = False,
) -> list[list[list[int]]]:
    due_dates = []
    no_due = [i for i in range(1, len(max_fills)) if empty_intervals[i] != 0]
    days_in = [[] for _ in max_fills]
    day_fills = [[0.0 for _ in max_fills] for _ in max_fills]
    if with_due:
        due_dates, no_due, day_fills, days_in = generate_days(
            max_fills=max_fills,
            inital_fill=inital_fill,
            vehicles=vehicles,
            day_period=day_period,
            fill_rates=fill_rates,
            days_in=days_in,
            day_fills=day_fills,
        )
    day_plan = near_neighbor_multi_day(
        due_dates=due_dates,
        no_due=no_due,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        fill_rates=fill_rates,
        inital_fill=weights,
        empty_intervals=empty_intervals,
        vehicles=vehicles,
        day_fills=day_fills,
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
    time_limit = 10 * 60

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

    for i in range(1, len(elevation_matrix)):
        nord_fill = nord_fills[i]
        max_f = max_volumes[i]
        fill_rates[i] = (max_f / day_period) * nord_fill

    for idx in range(1, len(nord_real_days_in)):
        if len(nord_real_days_in[idx]) == 0:
            fill_rates[idx] = 0
        else:
            max_f = max_volumes[idx]
            fill_rates[idx] = (max_f / day_period) * len(nord_real_days_in[idx]) * 0.5

    stop_time = 300000
    weights = [0.0]
    empty_intervals = [0]

    for idx in range(1, len(max_volumes)):
        max_f = max_volumes[idx]
        fill_rate = fill_rates[idx]
        if fill_rate == 0:
            weights.append(0)
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

    inital_fill = copy(weights)

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
        max_iter=100000,
        max_no_improve=100,
        debug_iter=10,
        fill_rates=fill_rates,
    )

    print()

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

    print("NORD")
    for dayx_idx, routes in enumerate(best_nord_plan):
        for route_idx in range(len(routes)):
            print(f"{dayx_idx}:{route_idx}: {best_nord_plan[dayx_idx][route_idx]}")
        print()

    with open("../data/optimized_nord_energy.json", "w") as f:
        json.dump(best_nord_plan, f)
    """

    for day in range(365):
        # print(f"day: {day}")
        for weight_idx in range(1, len(weights)):
            current_day = day % day_period
            routes = best_nord_plan[current_day]
            for route in routes:
                if weight_idx in route:
                    weights[weight_idx] = 0
                    break
            weight = weights[weight_idx]
            max_f = max_fill[weight_idx]
            if weight > max_f:
                print(f"weight idx: {weight_idx}")
                # print(f"empty_interval idx: {empty_intervals[weight_idx]}")
                empty_dates = []
                for day_idx in range(len(best_nord_plan)):
                    routes = best_nord_plan[day_idx]
                    for route in routes:
                        if weight_idx in route:
                            empty_dates.append(day_idx)
                            break

                print(f"current data: {day%day_period}")
                print(f"empty dates: {empty_dates}")

                print(f"empty interval: {empty_intervals[weight_idx]}")
                raise Exception("OVERFLOW")
            weights[weight_idx] += fill_rates[weight_idx]
    weights = copy(inital_fill)

    print("NORD DID IT")

    day_plan = multi_nn(
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        vehicles=vehicles,
        inital_fill=weights,
        fill_rates=fill_rates,
        max_fills=max_fill,
        day_period=day_period,
        empty_intervals=empty_intervals,
        stop_time=stop_time,
        weight_matrix=weight_matrix,
    )

    real_days_in = [[] for _ in all_moloks]
    for i in range(len(all_moloks)):
        for day_idx, day in enumerate(day_plan):
            for route in day:
                if i in route:
                    real_days_in[i].append(day_idx)
                    break
    inital_fill = copy(weights)

    inital_cost = sum(
        [
            sum([sum_route_dist(i, distance_matrix) for i in routes])
            for routes in day_plan
        ]
    )

    day_penalty_matrix = [
        [[0 for _ in all_moloks] for _ in all_moloks] for _ in range(day_period)
    ]

    # while True:
    for day in range(365):
        # print(f"day: {day}")
        for weight_idx in range(1, len(weights)):
            current_day = day % day_period
            routes = day_plan[current_day]
            for route in routes:
                if weight_idx in route:
                    weights[weight_idx] = 0
                    break
            weight = weights[weight_idx]
            max_f = max_fill[weight_idx]
            if weight > max_f:
                print(f"weight idx: {weight_idx}")
                # print(f"empty_interval idx: {empty_intervals[weight_idx]}")
                empty_dates = []
                for day_idx in range(len(day_plan)):
                    routes = day_plan[day_idx]
                    for route in routes:
                        if weight_idx in route:
                            empty_dates.append(day_idx)
                            break

                print(f"current data: {day%day_period}")
                print(f"empty dates: {empty_dates}")
                print(f"empty interval: {empty_intervals[weight_idx]}")
                raise Exception("OVERFLOW")
            weights[weight_idx] += fill_rates[weight_idx]
    weights = copy(inital_fill)

    vehicles_used = []
    pre_cost = sum(
        [
            sum([sum_route_dist(i, distance_matrix) for i in routes])
            for routes in day_plan
        ]
    )
    # most_points = max([len(day_plan[i][j]) for i in range(len(day_plan)) for j in range(len(day_plan[i]))])
    for routes in day_plan:
        for route_idx in range(len(routes)):
            if route_idx in vehicles_used:
                continue
            route = day_plan[route_idx]
            for point in route:
                if len(point) > 2:
                    vehicles_used.append(route_idx)
                    break
    print(f"vehicles_used:{len(vehicles_used)}")

    print(f"pre_cost : {pre_cost}")

    weight_matrix = gen_weight_day_matrix(weights, fill_rates, day_period, real_days_in)

    best_day_plan = gls(
        day_plan=day_plan,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        penalty=0.2,
        day_penalty_matrix=day_penalty_matrix,
        vehicles=vehicles,
        stop_delay=stop_time,
        weight_matrix=weight_matrix,
        days_in=real_days_in,
        empty_intervals=empty_intervals,
        max_iter=100000,
        max_no_improve=100,
        debug_iter=10,
        time_limit_s=time_limit * 2,
        fill_rates=fill_rates,
    )

    with open("../data/optimized_nord_plan.json", "w") as f:
        json.dump(best_nord_plan, f)

    with open("../data/cust_plan.json", "w") as f:
        json.dump(best_day_plan, f)

    aft_cost = sum(
        [
            sum([sum_route_dist(i, distance_matrix) for i in routes])
            for routes in day_plan
        ]
    )

    print(f"aft_cost: {aft_cost}")

    print(f"diff: {aft_cost - pre_cost}")
    print()

    final_cost = sum(
        [
            sum([sum_route_dist(i, distance_matrix) for i in routes])
            for routes in day_plan
        ]
    )

    print(f"final cost: {final_cost}")

    print(f"total improvement cost: {final_cost - inital_cost}")

    print(f"diff nord: {final_cost - nord_total_dist}")

    vehicles_used = []
    for routes in best_day_plan:
        for route_idx in range(len(routes)):
            if route_idx in vehicles_used:
                continue
            route = best_day_plan[route_idx]
            for point in route:
                if len(point) > 2:
                    vehicles_used.append(route_idx)
                    break

    print(f"vehicles_used:{len(vehicles_used)}")

    print("OLD NORD")
    for dayx_idx, routes in enumerate(base_nord):
        for route_idx in range(len(routes)):
            print(f"{dayx_idx}:{route_idx}: {base_nord[dayx_idx][route_idx]}")
        print()

    print("NORD")
    for dayx_idx, routes in enumerate(best_nord_plan):
        for route_idx in range(len(routes)):
            print(f"{dayx_idx}:{route_idx}: {best_nord_plan[dayx_idx][route_idx]}")
        print()

    print("CUST")
    for dayx_idx, routes in enumerate(best_day_plan):
        for route_idx in range(len(routes)):
            if route_idx not in vehicles_used:
                continue
            print(f"{dayx_idx}:{route_idx}: {best_day_plan[dayx_idx][route_idx]}")
        print()

    for day in range(365):
        # print(f"day: {day}")
        for weight_idx in range(1, len(weights)):
            current_day = day % day_period
            routes = best_day_plan[current_day]
            for route in routes:
                if weight_idx in route:
                    weights[weight_idx] = 0
                    break
            weight = weights[weight_idx]
            max_f = max_fill[weight_idx]
            if weight > max_f:
                print(f"weight idx: {weight_idx}")
                # print(f"empty_interval idx: {empty_intervals[weight_idx]}")
                empty_dates = []
                for day_idx in range(len(day_plan)):
                    routes = best_day_plan[day_idx]
                    for route in routes:
                        if weight_idx in route:
                            empty_dates.append(day_idx)
                            break

                print(f"current data: {day%day_period}")
                print(f"empty dates: {empty_dates}")
                raise Exception("OVERFLOW")
            weights[weight_idx] += fill_rates[weight_idx]

    print("sugoi")

    """
    """

    print(f"stop time: {stop_time/60000}")
    rint(vehicles_used)
    print(f"most point:{most_points}")
    print(f"diff: {cust_total_dist - nord_total_dist}")

    #print(f"diff: {cust_total_dist - nord_total_dist}")

    print(f"time: {sum_route_time(day_plan[0][0],time_matrix,stop_time)}")
    stop_time += 30000
    """
