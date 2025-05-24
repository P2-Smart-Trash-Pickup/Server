from file_manipulation import load_distance_matrix, load_fill_rate, load_moloks, load_time_matrix,load_elevation_matrix
from vehicle import Vehicle
def gen_test() -> tuple[list[list[list[list[float]]]],list[list[float]],list[float],list[float],list[float],Vehicle,list[list[int]]]:
    penalty_matrix = []
    time_matrix = load_time_matrix()
    fill_rates = load_fill_rate()
    elevation_matrix = load_elevation_matrix()
    for _ in elevation_matrix:
        penalty_matrix.append([])
        for _ in elevation_matrix:
            penalty_matrix[-1].append(0)
    weights = [(i*0.129)/1000 for i in fill_rates]
    max_volume = ((7.57-5)*(3-0.6)*(3))*1000
    vehicle = Vehicle(max_capacity=29*1000,battery_capacity=416,acceleration=0.68,time_constraint=21600000,initial_mass=13*1000,max_volume=max_volume)

    molokker = load_moloks()
    max_volumes = [0.0] + [i["max_fill"] for i in molokker[1:]]

    return elevation_matrix,time_matrix,max_volumes,fill_rates,weights,vehicle,penalty_matrix

def gen_test_dist() -> tuple[list[list[float]],list[list[float]],list[float],list[float],Vehicle,list[list[int]]]:
    penalty_matrix = []
    time_matrix = load_time_matrix()
    fill_rates = load_fill_rate()
    fill_rates = [i*0.129 for i in fill_rates]
    distance_matrix = load_distance_matrix()
    molokker = load_moloks()
    max_fill = [0.0] + [i["max_fill"]*0.129 for i in molokker[1:]]
    for _ in distance_matrix:
        penalty_matrix.append([])
        for _ in distance_matrix:
            penalty_matrix[-1].append(0)
    max_volume = ((7.57-5)*(3-0.6)*(3))*1000
    vehicle = Vehicle(max_capacity=29*1000,battery_capacity=416,acceleration=0.68,time_constraint=28800000,initial_mass=13*1000,max_volume=max_volume)

    return distance_matrix,time_matrix,fill_rates,max_fill,vehicle,penalty_matrix
def get_vehicle() -> Vehicle:

    max_volume = ((7.57-5)*(3-0.6)*(3))*1000
    vehicle = Vehicle(max_capacity=29*1000,battery_capacity=416,acceleration=0.68,time_constraint=28800000,initial_mass=13*1000,max_volume=max_volume)
    return vehicle


