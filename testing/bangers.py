import json
import requests
distance_matrix= []
time_matrix = []
poly_line_matrix = []

all_molokker = []

url = "http://localhost:8002/route?json="

with open("molok_distance_matrix.json","r") as f:
    distance_matrix = json.loads(f.read())

with open("molok_time_matrix.json","r") as f:
    time_matrix= json.loads(f.read())

with open("molok_polyline_matrix.json","r") as f:
    poly_line_matrix= json.loads(f.read())

with open("molokker.json","r") as f:
    all_molokker = json.loads(f.read())

print(len(distance_matrix))
print(len(poly_line_matrix))
for line_idx in range(len(distance_matrix)):
    zero_index = distance_matrix[line_idx].index(0)
    zero_index2 = len(distance_matrix[line_idx]) - 1 - distance_matrix[line_idx][::-1].index(0)
    if zero_index != line_idx or zero_index2 != line_idx:
        temp_distances = []
        temp_times = []
        temp_polylines = []

        base_lat = all_molokker[line_idx]["lat"]
        base_lon = all_molokker[line_idx]["lon"]

        for molok2_index in range(line_idx):
            temp_distances.append(distance_matrix[molok2_index][line_idx])
            temp_times.append(time_matrix[molok2_index][line_idx])
            temp_polylines.append(poly_line_matrix[molok2_index][line_idx])

        temp_distances.append(0)
        temp_times.append(0)
        temp_polylines.append("")
        for molok2_index in range(line_idx+1,len(all_molokker)):

            lat = all_molokker[molok2_index]["lat"] 
            lon = all_molokker[molok2_index]["lon"] 

            req_json = json.dumps({"locations":[{"lat":base_lat,"lon":base_lon},{"lat":lat,"lon":lon}],"costing":"auto"})

            out_url = url+req_json

            resp = requests.request(url=out_url,method="GET")
            resp_json = resp.json()
            summary = resp_json["trip"]["summary"]
            time_taken = summary["time"]
            distance_taken = summary["length"]
            poly_line = resp_json["trip"]["legs"][0]["shape"]

            temp_distances.append(distance_taken)
            temp_times.append(time_taken)
            temp_polylines.append(poly_line)
        distance_matrix[line_idx] = temp_distances
        time_matrix[line_idx] =temp_times 
        poly_line_matrix[line_idx] = temp_polylines 

for line_idx in range(len(distance_matrix)):
    zero_index = distance_matrix[line_idx].index(0)
    if zero_index != line_idx:
        print(f"zero index: {zero_index}")
        print(f"line index: {line_idx}")
        print(distance_matrix[line_idx])
        raise Exception("err")

with open("molok_distance_matrix.json","w") as f:
    f.write(json.dumps(distance_matrix))

with open("molok_time_matrix.json","w") as f:
    f.write(json.dumps(time_matrix))

with open("molok_polyline_matrix.json","w") as f:
    f.write(json.dumps(poly_line_matrix))





    
