import json
distance_matrix = []
poly_matrix = []
all_molokker = []

with open("../data/molokker.json","r") as f:
    all_molokker = json.loads(f.read())

with open("../data/molok_polyline_matrix.json","r") as f:
    poly_matrix= json.loads(f.read())

with open("../data/molok_distance_matrix.json","r") as f:
    distance_matrix = json.loads(f.read())

print(len(all_molokker))
print(len(distance_matrix))
print(len(poly_matrix))

