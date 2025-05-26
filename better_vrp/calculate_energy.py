import math
from vehicle import Vehicle
from file_manipulation import load_time_matrix, load_elevation_matrix
from help_heuristics import sum_route_weight_volume
import json


def calculate_energy_expendeture(
    duration_t: float,
    mass: float,
    road_angle: float,
    vehicle_speed: float,
    vehicle_acceleration: float,
    vehicle_front_area: float = 8,
    air_density: float = 1.225,
    rolling_resistance: float = 0.03,
    drag_resistance: float = 0.8,
    drive_train_efficiency: float = 0.85,
    discharge_efficiency: float = 0.9,
) -> float:

    gravity_acceleration = 9.82
    duration_h = duration_t / 3600
    F_a = (
        1 / 2 * air_density * vehicle_front_area * drag_resistance * (vehicle_speed**2)
    )
    F_r = mass * rolling_resistance * gravity_acceleration * math.cos(road_angle)
    F_g = mass * gravity_acceleration * math.sin(road_angle)
    F_la = mass * vehicle_acceleration
    F_t = F_la + F_a + F_r + F_g

    P_v = vehicle_speed * F_t
    P_t = P_v / drive_train_efficiency
    E_c = (P_t / (1000 * discharge_efficiency)) * duration_h

    return E_c


def calcualte_segment_energy(
    elevations: list[list[float]],
    trip_time: float,
    mass: float,
    vehicle_acceleration: float,
    penalty_amount: int | None = None,
    penalty: float | None = None,
) -> tuple[float, float]:
    total_energy = 0
    penalized_total = 0
    if len(elevations) == 0:
        return 0, 0
    avg_speed = elevations[-1][0] / trip_time

    acceleration_time = avg_speed / vehicle_acceleration
    # de_acceleration_time = (0-avg_speed)/(-vehicle_acceleration*2)
    de_acceleration_time = acceleration_time

    pre_distance = 0
    start_point = 0

    for elevation_point_idx in range(len(elevations)):
        elevation_point = elevations[elevation_point_idx]

        current_distance = elevation_point[0]
        if current_distance == 0:
            start_point += 1
            continue
        current_road_grade = elevation_point[1]
        current_duration = (current_distance - pre_distance) / avg_speed
        pre_distance = current_distance

        if elevation_point_idx == start_point:
            total_energy += calculate_energy_expendeture(
                duration_t=acceleration_time,
                mass=mass,
                road_angle=current_road_grade,
                vehicle_speed=avg_speed,
                vehicle_acceleration=vehicle_acceleration,
            )
            total_energy += calculate_energy_expendeture(
                duration_t=current_duration - acceleration_time,
                mass=mass,
                road_angle=current_road_grade,
                vehicle_speed=avg_speed,
                vehicle_acceleration=0,
            )
        elif elevation_point_idx == len(elevations) - 1:
            total_energy += calculate_energy_expendeture(
                duration_t=current_duration - de_acceleration_time,
                mass=mass,
                road_angle=current_road_grade,
                vehicle_speed=avg_speed,
                vehicle_acceleration=0,
            )
            total_energy += calculate_energy_expendeture(
                duration_t=de_acceleration_time,
                mass=mass,
                road_angle=current_road_grade,
                vehicle_speed=avg_speed,
                vehicle_acceleration=-vehicle_acceleration,
            )
        else:
            total_energy += calculate_energy_expendeture(
                duration_t=current_duration,
                mass=mass,
                road_angle=current_road_grade,
                vehicle_speed=avg_speed,
                vehicle_acceleration=0,
            )
    if penalty_amount != None and penalty != None:
        penalized_total = total_energy + penalty * total_energy * penalty_amount
    return total_energy, penalized_total


def calculate_segment_energy_points(
    point1: int,
    point2: int,
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    penalty_matrix: list[list[int]],
    penalty: float | None,
    vehicle: Vehicle,
    extra_mass: float,
) -> tuple[float, float, float]:
    arc = elevation_matrix[point1][point2]
    time = time_matrix[point1][point2]

    penalty_amount = 0
    if penalty_matrix and penalty != None:
        penalty_amount = penalty_matrix[point1][point2]

    reg_cost, pen_cost = calcualte_segment_energy(
        arc,
        trip_time=time,
        mass=vehicle.initial_mass + extra_mass,
        vehicle_acceleration=vehicle.acceleration,
        penalty_amount=penalty_amount,
        penalty=penalty,
    )

    return reg_cost, pen_cost, time


def calculate_route_energy(
    route: list[int],
    elevation_matrix: list[list[list[list[float]]]],
    time_matrix: list[list[float]],
    weights: list[float],
    vehicle: Vehicle,
    penalty_matrix: list[list[int]] | None = None,
    penalty: float | None = None,
) -> tuple[float, float]:
    total_energy = 0
    penalized_total = 0
    vehicle_inital_mass = vehicle.initial_mass
    vehicle_acceleration = vehicle.acceleration
    for i in range(len(route) - 1):
        vehicle_mass = vehicle_inital_mass + sum_route_weight_volume(
            route[: i + 1], weights
        )
        # vehicle_mass = vehicle_inital_mass

        current_point = route[i]
        next_point = route[i + 1]

        depot_elevation = elevation_matrix[current_point][next_point]
        if not depot_elevation:
            continue

        depot_time = time_matrix[current_point][next_point]

        energy_required = 0
        penalty_energy = 0
        if penalty_matrix and penalty != None:
            penalty_amount = penalty_matrix[current_point][next_point]
            energy_required, penalty_energy = calcualte_segment_energy(
                depot_elevation,
                depot_time,
                vehicle_mass,
                vehicle_acceleration,
                penalty_amount=penalty_amount,
                penalty=penalty,
            )
        else:
            energy_required, penalty_energy = calcualte_segment_energy(
                depot_elevation, depot_time, vehicle_mass, vehicle_acceleration
            )

        total_energy += energy_required
        penalized_total += penalty_energy

    return total_energy, penalized_total


if __name__ == "__main__":
    better_routes = []
    with open("../data/better.json", "r") as f:
        better_routes = json.load(f)

    time_matrix = load_time_matrix()
    elevation_matrix = load_elevation_matrix()

    route = better_routes["2025"]["1"]["5"]
    depot_elevation = elevation_matrix[0][route[1]]
    depot_time = time_matrix[0][route[1]]
    mass = 29 * 1000

    total_distance = depot_elevation[-1][0]

    total_energy = calcualte_segment_energy(depot_elevation, depot_time, mass, 0.68)

    last_index = 0

    for i in range(1, len(route) - 1):

        print(total_energy)
        current_point = route[i]
        next_point = route[i + 1]

        depot_elevation = elevation_matrix[current_point][next_point]
        if not depot_elevation:
            continue

        total_distance += depot_elevation[-1][0]
        depot_time = time_matrix[current_point][next_point]

        total_energy += calcualte_segment_energy(
            depot_elevation, depot_time, mass, 0.68
        )
        last_index = next_point

    print(total_energy)
    depot_elevation = elevation_matrix[last_index][0]

    total_distance += depot_elevation[-1][0]
    depot_time = time_matrix[last_index][0]

    total_energy += calcualte_segment_energy(depot_elevation, depot_time, mass, 0.68)

    print(total_energy)
    print(total_distance)
