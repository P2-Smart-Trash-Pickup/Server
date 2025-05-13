import json
distance_matrix = []
time_matrix = []
polyline_matrix = []
with open("molok_distance_matrix.json","r") as f:
    distance_matrix = json.loads(f.read())

with open("molok_time_matrix.json","r") as f:
    time_matrix = json.loads(f.read())

with open("molok_polyline_matrix.json","r") as f:
    polyline_matrix = json.loads(f.read())

for line_idx in range(len(distance_matrix)):
    distance_line = distance_matrix[line_idx]
    time_line = time_matrix[line_idx]
    poly_line = polyline_matrix[line_idx]

    zero_index = distance_line.index(0)

    for idx in range(zero_index):
        old_distance_line = distance_matrix[idx]
        old_time_line = time_matrix[idx]
        old_poly_line = polyline_matrix[idx]

        distance_line[idx] = old_distance_line[line_idx]
        time_line[idx] = old_time_line[line_idx]
        poly_line[idx] = old_poly_line[line_idx]

    distance_matrix[line_idx] = distance_line
    time_matrix[line_idx] = time_line
    polyline_matrix[line_idx] = poly_line

with open("molok_distance_matrix2.json","w") as f:
    f.write(json.dumps(distance_matrix))

with open("molok_time_matrix.json2","w") as f:
    f.write(json.dumps(time_matrix))

with open("molok_polyline_matrix2.json","w") as f:
    f.write(json.dumps(polyline_matrix))
