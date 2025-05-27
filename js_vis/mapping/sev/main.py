import json

test_file = []
with open("../../../data/molok_polyline_matrix2.json", "r") as f:
    test_file = json.load(f)

print(test_file[0])
