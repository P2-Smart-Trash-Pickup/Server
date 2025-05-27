import json
poly_matrix = []
distance_matrix = []
all_moloks = []

with open("molok_polyline_matrix.json","r") as f:
    poly_matrix = json.loads(f.read())

with open("molok_distance_matrix.json","r") as f:
    distance_matrix = json.loads(f.read())

with open("molokker.json","r") as f:
    all_moloks = json.loads(f.read())

url = "http://localhost:8002/route?json="

current_molok = all_moloks[-1]

poly_matrix.append([])

for i in range(len(poly_matrix)-1):
    poly_matrix[-1].append(poly_matrix[i][-1])

poly_matrix[-1].append("")

with open("molok_polyline_matrix.json","w") as f:
    f.write(json.dumps(poly_matrix))

