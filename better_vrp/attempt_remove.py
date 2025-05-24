from calculate_energy import calculate_segment_energy_points
from vehicle import Vehicle
from help_heuristics import (
    get_penalty,
    is_weekend,
    sum_route_weight_volume,
    update_weight_matrix,
    volume_to_weight,
)


def attemp_remove_multi(
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
            for point_idx in range(1, len(route_i) - 1):

                pre_point = route_i[point_idx - 1]
                cur_point = route_i[point_idx]
                next_point = route_i[point_idx + 1]

                temp_days = days_in[cur_point]

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

                    if pre_diff + next_diff <= min(
                        empty_interval[cur_point], len(day_plan) - 1
                    ):
                        old_cost = get_penalty(
                            pre_point,
                            cur_point,
                            distance_matrix=distance_matrix,
                            penalty_matrix=penalty_matrix,
                            penalty=penalty,
                        ) + get_penalty(
                            cur_point,
                            next_point,
                            distance_matrix=distance_matrix,
                            penalty_matrix=penalty_matrix,
                            penalty=penalty,
                        )
                        new_cost = get_penalty(
                            pre_point,
                            next_point,
                            distance_matrix=distance_matrix,
                            penalty_matrix=penalty_matrix,
                            penalty=penalty,
                        )

                        cost_diff = new_cost - old_cost

                        if cost_diff < best_improvement:

                            best_improvement = cost_diff
                            best_i = point_idx
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


def implement_atttempt_remove(
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
    routes = day_plan[best_day_i]
    route = routes[best_route_i]
    point = route[best_i]
    days_in[point].remove(best_day_i)
    route.remove(point)


def attempt_remove_mutli_day_en(
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
        r1_penalty_matrix = day_penalty_matrix[day_idx_i]
        r1_penalty_matrix = day_penalty_matrix[day_idx_i]
        r1_weights = weight_matrix[day_idx_i]
        for route_idx_i in range(len(cur_day_i)):
            route_i = cur_day_i[route_idx_i]

            r1_vehicle = vehicles[route_idx_i]
            for point_idx in range(1, len(route_i) - 1):

                pre_point = route_i[point_idx - 1]
                cur_point = route_i[point_idx]
                next_point = route_i[point_idx + 1]

                temp_days = days_in[cur_point]

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

                    if pre_diff + next_diff <= min(
                        empty_interval[cur_point], len(day_plan) - 1
                    ):

                        extra_1_mass = sum_route_weight_volume(
                            route_i[: point_idx + 1], r1_weights
                        )
                        cur_mass_1 = r1_weights[point_idx]

                        _, old_1_pen_pre_cost, _ = calculate_segment_energy_points(
                            point1=pre_point,
                            point2=cur_point,
                            elevation_matrix=elevation_matrix,
                            time_matrix=time_matrix,
                            vehicle=r1_vehicle,
                            penalty_matrix=r1_penalty_matrix,
                            penalty=penalty,
                            extra_mass=extra_1_mass - cur_mass_1,
                        )

                        _, old_2_pen_pre_cost, _ = calculate_segment_energy_points(
                            point1=cur_point,
                            point2=next_point,
                            elevation_matrix=elevation_matrix,
                            time_matrix=time_matrix,
                            vehicle=r1_vehicle,
                            penalty_matrix=r1_penalty_matrix,
                            penalty=penalty,
                            extra_mass=extra_1_mass,
                        )

                        _, new_pen_reg_cost, _ = calculate_segment_energy_points(
                            point1=pre_point,
                            point2=next_point,
                            elevation_matrix=elevation_matrix,
                            time_matrix=time_matrix,
                            vehicle=r1_vehicle,
                            penalty_matrix=r1_penalty_matrix,
                            penalty=penalty,
                            extra_mass=extra_1_mass - cur_mass_1,
                        )
                        old_cost = old_1_pen_pre_cost + old_2_pen_pre_cost
                        new_cost = new_pen_reg_cost

                        cost_diff = new_cost - old_cost

                        if cost_diff < best_improvement:

                            best_improvement = cost_diff
                            best_i = point_idx
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


def implement_remove_day_en(
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
    routes = day_plan[best_day_i]
    route = routes[best_route_i]
    point = route[best_i]
    days_in[point].remove(best_day_i)
    route.remove(point)

    update_weight_matrix(
        day_period=len(day_plan),
        days_in=days_in,
        point=point,
        weight_matrix=volume_matrix,
        fill_rates=fill_rates,
    )
    for day_idx in range(len(volume_matrix)):
        for point_idx in range(len(volume_matrix[day_idx])):
            weight_matrix[day_idx][point_idx] = volume_to_weight(
                volume_matrix[day_idx][point_idx]
            )
