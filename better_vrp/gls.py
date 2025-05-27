from copy import deepcopy
from calculate_energy import calculate_route_energy, calculate_segment_energy_points
from cross import (
    cross_days_cap,
    implement_cross_day,
    cross_multi_day_en,
    implement_cross_day_en,
)
from relocate import (
    relocate_days_cap,
    implement_relocate_day,
    relocate_mutli_day_en,
    implement_relocate_day_en,
)
from exchange import (
    exchange_days_cap,
    implement_exchange_day,
    exchange_multi_day_en,
    implement_exchange_day_en,
)
from two_op import (
    two_op_days_cap,
    implement_two_op_days,
    implement_two_op_days_en,
    two_op_en_multi_day,
)
from attempt_remove import (
    attemp_remove_multi,
    implement_atttempt_remove,
    attempt_remove_mutli_day_en,
    implement_remove_day_en,
)

from vehicle import Vehicle
from help_heuristics import (
    Heuristic,
    get_max_empty,
    sum_route_dist,
    EnergyHeuristic,
)
from tqdm import tqdm
import time


def local_search(
    day_plan: list[list[list[int]]],
    days_in: list[list[int]],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    vehicles: list[Vehicle],
    weight_matrix: list[list[float]],
    day_penalty_matrix: list[list[list[int]]],
    penalty: float,
    stop_delay: float,
    empty_intervals: list[int],
    fill_rates: list[float],
) -> float:

    results: list[Heuristic] = []
    heuristics: list[Heuristic] = [
        Heuristic(two_op_days_cap, implement_two_op_days),
        Heuristic(cross_days_cap, implement_cross_day),
        Heuristic(relocate_days_cap, implement_relocate_day),
        Heuristic(exchange_days_cap, implement_exchange_day),
        Heuristic(attemp_remove_multi, implement_atttempt_remove),
    ]

    for heuristic_s in heuristics:
        heuristic_s.solve(
            day_plan=day_plan,
            days_in=days_in,
            distance_matrix=distance_matrix,
            time_matrix=time_matrix,
            vehicles=vehicles,
            weight_matrix=weight_matrix,
            day_penalty_matrix=day_penalty_matrix,
            penalty=penalty,
            stop_delay=stop_delay,
            empty_intervals=empty_intervals,
        )
        results.append(heuristic_s)

    results.sort(key=lambda x: x.best_cost)

    best_heurestic = results[0]

    best_cost = best_heurestic.best_cost

    if best_cost < 0.1:
        best_heurestic.implement(
            day_plan=day_plan,
            days_in=days_in,
            weight_matrix=weight_matrix,
            fill_rates=fill_rates,
        )

    return best_cost


def find_feature_pen(
    day_plan: list[list[list[int]]],
    distance_matrix: list[list[float]],
    day_penalty_matrix: list[list[list[int]]],
) -> list[tuple[int, int, int]]:
    worst_features = []
    worst_utility = 0
    for day_idx_i in range(len(day_plan)):
        routes_i = day_plan[day_idx_i]
        for route_i_idx in range(len(routes_i)):
            route = routes_i[route_i_idx]

            for point_idx in range(len(route) - 1):
                point_i = route[point_idx]
                point_j = route[point_idx + 1]

                utility = distance_matrix[point_i][point_j] / (
                    1 + day_penalty_matrix[day_idx_i][point_i][point_j]
                )

                if utility == worst_utility:
                    worst_features.append((day_idx_i, point_idx, point_idx + 1))
                elif utility > worst_utility:
                    worst_features = [(day_idx_i, point_idx, point_idx + 1)]
                    worst_utility = utility

    return worst_features


def gls(
    day_plan: list[list[list[int]]],
    days_in: list[list[int]],
    distance_matrix: list[list[float]],
    time_matrix: list[list[float]],
    vehicles: list[Vehicle],
    weight_matrix: list[list[float]],
    day_penalty_matrix: list[list[list[int]]],
    penalty: float,
    stop_delay: float,
    empty_intervals: list[int],
    fill_rates: list[float],
    max_iter: int,
    max_no_improve: int,
    debug_iter: int = 0,
    time_limit_s=0,
) -> list[list[list[int]]]:
    no_pen = deepcopy(day_penalty_matrix)

    local_search(
        day_plan=day_plan,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        penalty=penalty,
        day_penalty_matrix=day_penalty_matrix,
        vehicles=vehicles,
        stop_delay=stop_delay,
        weight_matrix=weight_matrix,
        days_in=days_in,
        empty_intervals=empty_intervals,
        fill_rates=fill_rates,
    )
    best_day_plan = deepcopy(day_plan)

    best_cost = sum(
        [
            sum([sum_route_dist(i, distance_matrix) for i in routes])
            for routes in best_day_plan
        ]
    )
    current_cost = best_cost

    since_no_improve = 0
    start_time = time.time()

    for i in tqdm(range(max_iter), desc="Optimizing"):
        if since_no_improve > max_no_improve / 10:
            penalty *= 1.2
        else:
            penalty *= 0.95

        if debug_iter:
            if i % debug_iter == 0:
                print()
                print(f"Current iter: {i}")
                print(f"Current cost: {current_cost}")
                print()
        if time_limit_s:
            if time.time() - start_time > time_limit_s:
                break
        if since_no_improve > max_no_improve:
            break
        worst_features = find_feature_pen(day_plan, distance_matrix, day_penalty_matrix)
        for day, point_i, point_j in worst_features:
            day_penalty_matrix[day][point_i][point_j] += 1

        cost = local_search(
            day_plan=day_plan,
            distance_matrix=distance_matrix,
            time_matrix=time_matrix,
            penalty=penalty,
            day_penalty_matrix=day_penalty_matrix,
            vehicles=vehicles,
            stop_delay=stop_delay,
            weight_matrix=weight_matrix,
            days_in=days_in,
            empty_intervals=empty_intervals,
            fill_rates=fill_rates,
        )
        current_cost += cost
        if current_cost < best_cost:
            best_day_plan = deepcopy(day_plan)
            best_cost = current_cost
            print()
            print(f"NEW BEST COST!!!: {current_cost}")
            print()
            since_no_improve = 0
        else:
            since_no_improve += 1

    local_search(
        day_plan=best_day_plan,
        distance_matrix=distance_matrix,
        time_matrix=time_matrix,
        penalty=penalty,
        day_penalty_matrix=no_pen,
        vehicles=vehicles,
        stop_delay=stop_delay,
        weight_matrix=weight_matrix,
        days_in=days_in,
        empty_intervals=empty_intervals,
        fill_rates=fill_rates,
    )

    return best_day_plan


def local_search_en(
    day_plan: list[list[list[int]]],
    days_in: list[list[int]],
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    vehicles: list[Vehicle],
    weight_matrix: list[list[float]],
    volume_matrix: list[list[float]],
    day_penalty_matrix: list[list[list[int]]],
    penalty: float,
    stop_delay: float,
    empty_intervals: list[int],
    fill_rates: list[float],
) -> float:

    results: list[EnergyHeuristic] = []
    heuristics: list[EnergyHeuristic] = [
        EnergyHeuristic(two_op_en_multi_day, implement_two_op_days_en, "Two op"),
        EnergyHeuristic(relocate_mutli_day_en, implement_relocate_day_en, "Relocate"),
        EnergyHeuristic(exchange_multi_day_en, implement_exchange_day_en, "Exchange"),
        # EnergyHeuristic(cross_multi_day_en, implement_cross_day_en),
        EnergyHeuristic(attempt_remove_mutli_day_en, implement_remove_day_en, "Remove"),
    ]

    iter = 0
    for heuristic_s in heuristics:
        heuristic_s.solve(
            day_plan=day_plan,
            elevation_matrix=elevation_matrix,
            volume_matrix=volume_matrix,
            days_in=days_in,
            time_matrix=time_matrix,
            vehicles=vehicles,
            weight_matrix=weight_matrix,
            day_penalty_matrix=day_penalty_matrix,
            penalty=penalty,
            stop_delay=stop_delay,
            empty_intervals=empty_intervals,
        )
        results.append(heuristic_s)
        iter += 1

    results.sort(key=lambda x: x.best_cost)

    best_heurestic = results[0]

    best_cost = best_heurestic.best_cost

    if best_cost < 0.1:
        best_heurestic.implement(
            volume_matrix=volume_matrix,
            day_plan=day_plan,
            days_in=days_in,
            weight_matrix=weight_matrix,
            fill_rates=fill_rates,
        )

    return best_cost


def find_feature_pen_en(
    day_plan: list[list[list[int]]],
    elevation_matrix: list[list[list[list[float]]]],
    day_penalty_matrix: list[list[list[int]]],
    time_matrix: list[list[float]],
    vehicles: list[Vehicle],
    weight_matrix: list[list[float]],
) -> list[tuple[int, int, int]]:
    worst_features = []
    worst_utility = 0
    for day_idx_i in range(len(day_plan)):
        routes_i = day_plan[day_idx_i]
        pen_mat = day_penalty_matrix[day_idx_i]
        r1_weights = weight_matrix[day_idx_i]
        for route_i_idx in range(len(routes_i)):
            route = routes_i[route_i_idx]
            r1_vehicle = vehicles[route_i_idx]

            for point_idx in range(len(route) - 1):
                point_i = route[point_idx]
                point_j = route[point_idx + 1]
                cost, _, _ = calculate_segment_energy_points(
                    point1=point_i,
                    point2=point_j,
                    elevation_matrix=elevation_matrix,
                    time_matrix=time_matrix,
                    penalty_matrix=pen_mat,
                    penalty=0.0,
                    vehicle=r1_vehicle,
                    extra_mass=r1_weights[point_i],
                )
                utility = cost / (1 + day_penalty_matrix[day_idx_i][point_i][point_j])

                if utility == worst_utility:
                    worst_features.append((day_idx_i, point_idx, point_idx + 1))
                elif utility > worst_utility:
                    worst_features = [(day_idx_i, point_idx, point_idx + 1)]
                    worst_utility = utility

    return worst_features


def gls_en(
    day_plan: list[list[list[int]]],
    days_in: list[list[int]],
    elevation_matrix: list[list[list[list[float]]]],
    volume_matrix: list[list[float]],
    time_matrix: list[list[float]],
    vehicles: list[Vehicle],
    weight_matrix: list[list[float]],
    day_penalty_matrix: list[list[list[int]]],
    penalty: float,
    stop_delay: float,
    empty_intervals: list[int],
    fill_rates: list[float],
    max_iter: int,
    max_no_improve: int,
    debug_iter: int = 0,
    time_limit_s=0,
) -> list[list[list[int]]]:
    no_pen = deepcopy(day_penalty_matrix)
    print("Local seraching")

    local_search_en(
        elevation_matrix=elevation_matrix,
        volume_matrix=volume_matrix,
        day_plan=day_plan,
        time_matrix=time_matrix,
        penalty=penalty,
        day_penalty_matrix=day_penalty_matrix,
        vehicles=vehicles,
        stop_delay=stop_delay,
        weight_matrix=weight_matrix,
        days_in=days_in,
        empty_intervals=empty_intervals,
        fill_rates=fill_rates,
    )
    best_day_plan = deepcopy(day_plan)

    best_cost = sum(
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
            for day_idx, routes in enumerate(best_day_plan)
        ]
    )
    current_cost = best_cost

    since_no_improve = 0
    start_time = time.time()

    for i in tqdm(range(max_iter), desc="Optimizing"):
        print(i)
        if since_no_improve > max_no_improve / 10:
            penalty *= 1.2
        else:
            penalty *= 0.95

        if debug_iter:
            if i % debug_iter == 0:
                print()
                print(f"Current iter: {i}")
                print(f"Current cost: {current_cost}")
                print()
        if time_limit_s:
            if time.time() - start_time > time_limit_s:
                break
        if since_no_improve > max_no_improve:
            break
        worst_features = find_feature_pen_en(
            day_plan=day_plan,
            elevation_matrix=elevation_matrix,
            day_penalty_matrix=day_penalty_matrix,
            time_matrix=time_matrix,
            vehicles=vehicles,
            weight_matrix=weight_matrix,
        )
        for day, point_i, point_j in worst_features:
            day_penalty_matrix[day][point_i][point_j] += 1

        cost = local_search_en(
            elevation_matrix=elevation_matrix,
            volume_matrix=volume_matrix,
            day_plan=day_plan,
            time_matrix=time_matrix,
            penalty=penalty,
            day_penalty_matrix=day_penalty_matrix,
            vehicles=vehicles,
            stop_delay=stop_delay,
            weight_matrix=weight_matrix,
            days_in=days_in,
            empty_intervals=empty_intervals,
            fill_rates=fill_rates,
        )
        current_cost += cost
        if current_cost < best_cost:
            best_day_plan = deepcopy(day_plan)
            best_cost = current_cost
            print()
            print(f"NEW BEST COST!!!: {current_cost}")

            # print(f"Act cost: {act_cost}")
            print()
            since_no_improve = 0
        else:
            since_no_improve += 1

        for day_idx in range(1, len(elevation_matrix)):
            if empty_intervals[day_idx] == 0:
                continue
            temp_days_in = days_in[day_idx]
            temp_empty = empty_intervals[day_idx]
            temp_max_empty = get_max_empty(temp_days_in, len(day_plan))
            if temp_max_empty > temp_empty:
                print(f"day: {day_idx}")
                print(f"empt interval: {temp_empty}")
                print(f"max empty: {temp_max_empty}")
                print(f"days in: {temp_days_in}")
                raise Exception("GLS IS SUSSY")

    local_search_en(
        elevation_matrix=elevation_matrix,
        volume_matrix=volume_matrix,
        day_plan=day_plan,
        time_matrix=time_matrix,
        penalty=penalty,
        day_penalty_matrix=no_pen,
        vehicles=vehicles,
        stop_delay=stop_delay,
        weight_matrix=weight_matrix,
        days_in=days_in,
        empty_intervals=empty_intervals,
        fill_rates=fill_rates,
    )

    return best_day_plan
