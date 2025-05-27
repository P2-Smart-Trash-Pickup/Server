import math
import random
def get_distance(point_a:list[float]|list[int],point_b:list[float]|list[int]) -> float:
    diff_width = point_a[0] - point_b[0]

    diff_height = point_a[1] - point_b[1]

    distance = math.sqrt(diff_width**2+diff_height**2)

    return distance

def generate_distance_matrix(point_amount:int,width:int,height:int) -> tuple[list[list[int]],list[list[int]]]:
    points = []

    for i in range(point_amount):

        point = [random.randint(0,width),random.randint(0,height)]
        while point in points: 
            point = [random.randint(0,width),random.randint(0,height)]
        points.append(point)

    distance_matrix = []

    for i in points:
        distance_row = []
        for j in points:
            distance = get_distance(i,j)
            distance_row.append(int(distance))
        distance_matrix.append(distance_row)

    #distance_matrix = np.array(distance_matrix)

    return points,distance_matrix

def gen_data_or(distance_matrix,point_amount,vehicle_amount,demand):
    data = {}
    data["distance_matrix"] = distance_matrix 
    data["demands"] = demand 
    data["vehicle_capacities"] = [round(point_amount/vehicle_amount)+1 for _ in range(vehicle_amount)] 
    data["num_vehicles"] =vehicle_amount 
    data["depot"] = 0
    return data
