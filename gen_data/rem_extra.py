import json
distance_matrix = []
time_matrix = []
with open("../data/molok_distance_matrix.json","r") as f:
    distance_matrix = json.loads(f.read())

with open("../data/molok_time_matrix.json","r") as f:
    time_matrix = json.loads(f.read())

for line_idx in range(len(distance_matrix)):
    line = distance_matrix[line_idx]
    line.pop(435)
    distance_matrix[line_idx] = line

distance_matrix.pop(435)

for line_idx in range(len(distance_matrix)):
    line = distance_matrix[line_idx]
    if line.index(0) != line_idx and not (line_idx == 160 or line_idx == 588):
        print(line_idx)
        raise Exception("fack")

for line_idx in range(len(time_matrix)):
    line = time_matrix[line_idx]
    line.pop(435)
    time_matrix[line_idx] = line
time_matrix.pop(435)

with open("../data/molok_distance_matrix.json","w") as f:
    f.write(json.dumps(distance_matrix))

with open("../data/molok_time_matrix.json","w") as f:
    f.write(json.dumps(time_matrix))
