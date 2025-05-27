import json
import math


height_matrix = []
with open("../data/molok_height_matrix.json", "r") as f:
    height_matrix = json.load(f)
idx_points = [i for i in range(len(height_matrix))]

el_matrix = []

for point_1 in range(len(height_matrix)):
    el_matrix.append([])
    for point_2 in range(len(height_matrix)):

        route_heights = height_matrix[point_1][point_2]
        if not route_heights:
            el_matrix[-1].append([])
            continue
        dist_list = [i[0] for i in route_heights]
        height_list = [i[1] for i in route_heights]

        extreme_points = [route_heights[0].copy()]

        for val in range(1, len(route_heights) - 1):
            pre_point = route_heights[val - 1][1]
            point = route_heights[val][1]
            next_point = route_heights[val + 1][1]

            if (pre_point < point and next_point < point) or (
                pre_point > point and next_point > point
            ):
                extreme_points.append(route_heights[val].copy())
        extreme_points.append(route_heights[-1].copy())

        extreme_dist_list = [i[0] for i in extreme_points]

        extreme_height_list = [i[1] for i in extreme_points]

        extreme_angles = []

        for val in range(len(extreme_points) - 1):
            point = extreme_points[val].copy()
            next_point = extreme_points[val + 1].copy()

            diff_x = next_point[0] - point[0]
            diff_y = next_point[1] - point[1]
            radi = math.atan2(diff_y, diff_x)

            point[0] = next_point[0]
            point[1] = radi

            extreme_angles.append(point)
        el_matrix[-1].append(extreme_angles)

with open("../data/molok_elcom_matrix.json", "w") as f:
    json.dump(el_matrix, f)
