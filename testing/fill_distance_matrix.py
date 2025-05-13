import json
from tqdm import tqdm
import requests
containers = []
small_containers = []

distance_matrix = []
time_matrix = []
poly_line_matrix = []

url = "http://localhost:8002/route?json="

with open("snall_moloks.json","r") as f:
    small_containers = json.loads(f.read())

with open("molokker.json","r") as f:
    containers = json.loads(f.read())

with open("molok_distance_matrix.json","r") as f:
    distance_matrix = json.loads(f.read())

with open("molok_time_matrix.json","r") as f:
    time_matrix = json.loads(f.read())

with open("molok_polyline_matrix.json","r") as f:
    poly_line_matrix = json.loads(f.read())

for line_idx in tqdm(range(len(distance_matrix)),desc="test") :
    distance_line = distance_matrix[line_idx]
    time_line= time_matrix[line_idx]
    poly_lines = poly_line_matrix[line_idx]
    container = containers[line_idx]

    base_lon = container["lon"]
    base_lat = container["lat"]
    if line_idx == 0:
        print(f"before amount: {len(distance_line)}")
    for small_container in small_containers:
        lon = small_container["lon"]
        lat = small_container["lat"]

        req_json = json.dumps({"locations":[{"lat":base_lat,"lon":base_lon},{"lat":lat,"lon":lon}],"costing":"auto"})

        out_url = url+req_json

        resp = requests.request(url=out_url,method="GET")
        resp_json = resp.json()
        summary = resp_json["trip"]["summary"]
        time_taken = summary["time"]
        distance_taken = summary["length"]
        poly_line = resp_json["trip"]["legs"][0]["shape"]

        distance_line.append(distance_taken)
        time_line.append(time_taken)
        poly_lines.append(poly_line)

    if line_idx == 0:
        print(f"after amount: {len(distance_line)}")
    distance_matrix[line_idx] = distance_line
    time_matrix[line_idx] = time_line
    poly_line_matrix[line_idx] = poly_lines

with open("molok_distance_matrix.json","w") as f:
    f.write(json.dumps(distance_matrix))

with open("molok_time_matrix.json","w") as f:
    f.write(json.dumps(time_matrix))

with open("molok_polyline_matrix.json","w") as f:
    f.write(json.dumps(poly_line_matrix))
