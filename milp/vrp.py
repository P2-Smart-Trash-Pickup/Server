from gen_data import generate_distance_matrix
from test_vrp import make_test

point_amount = 500 
width = 1920
height = 1080
vehicle_amount = 2

points, distance_matrix = generate_distance_matrix(point_amount, width, height)
demand = [0]
for _ in range(point_amount - 1):
    demand.append(1)
make_test(vehicle_amount,50,1000)


