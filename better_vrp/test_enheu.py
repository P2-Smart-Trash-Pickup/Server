import json
import math
import random
from copy import copy

from calculate_energy import calculate_route_energy
from cross import (
    cross_en,
    cross_en_paralel,
    cross_multi_day_en,
    implement_cross,
    implement_cross_day_en,
)
from exchange import exchange_en, implement_exchange
from file_manipulation import load_date_molok, load_moloks
from help_heuristics import gen_weight_day_matrix, volume_to_weight
from relocate import implement_relocate, relocate_en
from test_vrp import gen_test
from two_op import implement_two_op_days, two_op_en_multi_day

if __name__ == "__main__":
    (
        elevation_matrix,
        time_matrix,
        max_volumes,
        fill_rates,
        org_weights,
        vehicle,
        penalty_matrix,
    ) = gen_test()
    day_period = 14

    stop_time = 300000

    date_molok = load_date_molok()
    all_moloks = load_moloks()

    nord_fills = []
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

    weights = [0.0]
    volumes = [0.0]
    empty_intervals = [0]
    for idx in range(1, len(max_volumes)):
        max_f = max_volumes[idx]
        fill_rate = fill_rates[idx]
        if fill_rate == 0:
            weights.append(0.0)
            volumes.append(0.0)
            empty_intervals.append(0)
            continue
        procent_diff = max_f / fill_rate
        empty_intervals.append(math.floor(procent_diff))
        fill_proc = random.uniform(0, procent_diff)
        # weights.append(fill_proc*fill_rate)
        weights.append(0.0)
        volumes.append(0.0)

    nord_real_days_in = [[] for _ in all_moloks]
    for i in range(len(all_moloks)):
        for day_idx, day in enumerate(nord_days):
            for route in day:
                if i in route:
                    nord_real_days_in[i].append(day_idx)

    for idx in range(1, len(nord_real_days_in)):
        if len(nord_real_days_in[idx]) == 0:
            fill_rates[idx] = 0
        else:
            max_f = max_volumes[idx]
            fill_rates[idx] = (max_f / day_period) * len(nord_real_days_in[idx]) * 0.5

    volume_matrix = gen_weight_day_matrix(
        volumes,
        fill_rates,
        day_period,
        nord_real_days_in,
    )
    weight_matrix = [
        [volume_to_weight(vol) for vol in route] for route in volume_matrix
    ]

    vehicle_amount = 1
    vehicles = [copy(vehicle) for _ in range(vehicle_amount)]

    nord_total_dist = sum(
        [
            sum(
                [
                    calculate_route_energy(
                        route=nord_days[day_idx][route_idx],
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        weights=weight_matrix[day_idx],
                        vehicle=vehicles[route_idx],
                    )[0]
                    for route_idx in range(len(nord_days[day_idx]))
                ]
            )
            for day_idx in range(len(nord_days))
        ]
    )
    print(f"Pre cost:{nord_total_dist}")

    day_penalty_matrix = [
        [[0 for _ in all_moloks] for _ in all_moloks] for _ in range(day_period)
    ]
    (
        best_improvement,
        best_i,
        best_j,
        best_route_i,
        best_route_j,
        best_day_i,
        best_day_j,
    ) = cross_multi_day_en(
        day_plan=nord_days,
        elevation_matrix=elevation_matrix,
        time_matrix=time_matrix,
        day_penalty_matrix=day_penalty_matrix,
        penalty=0.0,
        vehicles=vehicles,
        stop_delay=stop_time,
        weight_matrix=weight_matrix,
        day_volume_matrix=volume_matrix,
        days_in=nord_real_days_in,
        empty_interval=empty_intervals,
    )

    implement_cross_day_en(
        day_plan=nord_days,
        best_i=best_i,
        best_j=best_j,
        best_route_i=best_route_i,
        best_route_j=best_route_j,
        best_day_i=best_day_i,
        best_day_j=best_day_j,
        days_in=nord_real_days_in,
        weight_matrix=weight_matrix,
        fill_rates=fill_rates,
        volume_matrix=volume_matrix,
    )
    print(f"Cost theory: {best_improvement}")

    nord_total_aft_dist = sum(
        [
            sum(
                [
                    calculate_route_energy(
                        route=nord_days[day_idx][route_idx],
                        elevation_matrix=elevation_matrix,
                        time_matrix=time_matrix,
                        weights=weight_matrix[day_idx],
                        vehicle=vehicles[route_idx],
                    )[0]
                    for route_idx in range(len(nord_days[day_idx]))
                ]
            )
            for day_idx in range(len(nord_days))
        ]
    )
    print(f"Aft cost:{nord_total_dist}")
    print(f"Real diff: {nord_total_aft_dist - nord_total_dist}")
