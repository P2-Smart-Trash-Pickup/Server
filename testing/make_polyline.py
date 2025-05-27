import json
import requests
from tqdm import tqdm
import math
from math import cos, asin, sqrt, pi
test = json.dumps([])

distance_fn= "../data/molok_distance_matrix2.json"
time_fn= "../data/molok_time_matrix2.json"
poly_fn= "../data/molok_polyline_matrix2.json"
ele_fn= "../data/molok_height_matrix.json"
index_keeper = "../data/index_keeper2.json"

try:
    with open(distance_fn,"x") as f:
        f.write(test)

    with open(time_fn,"x") as f:
        f.write(test)

    with open(poly_fn,"x") as f:
        f.write(test)

    with open(ele_fn,"x") as f:
        f.write(test)

    with open(index_keeper,"x") as f:
        f.write(json.dumps({"index":0}))
except:
    pass
url = "http://localhost:8989/route?profile=truck&elevation=true&instructions=false&points_encoded=false"


all_mollooker = [] 
with open("../data/molokker.json","r") as f:
    all_mollooker= json.loads(f.read())


def distance_lat_long(lat1, lon1, lat2, lon2):
    r = 6371 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))

distance_matrix = []
time_matrix = []
polyline_matrix = []
ele_matrix = []
last_index = 0

with open(distance_fn,"r") as f:
    distance_matrix = json.loads(f.read())

with open(time_fn,"r") as f:
    time_matrix = json.loads(f.read())

with open(poly_fn,"r") as f:
    polyline_matrix= json.loads(f.read())

with open(ele_fn,"r") as f:
    ele_matrix = json.loads(f.read())

with open(index_keeper,"r") as f:
    last_index = json.loads(f.read())["index"]
session = requests.session()

for molok1_index in tqdm(range(len(all_mollooker)),desc="Generating matrixes"):
    if molok1_index < last_index:
        continue
    if molok1_index == last_index:
        with open(distance_fn,"r") as f:
            distance_matrix = json.loads(f.read())

        with open(time_fn,"r") as f:
            time_matrix = json.loads(f.read())

        with open(poly_fn,"r") as f:
            polyline_matrix= json.loads(f.read())

        with open(ele_fn,"r") as f:
            ele_matrix = json.loads(f.read())

    distance_matrix.append([])
    time_matrix.append([])
    polyline_matrix.append([])
    ele_matrix.append([])

    base_lat = all_mollooker[molok1_index]["lat"]
    base_lon = all_mollooker[molok1_index]["lon"]

    for molok2_index in range(len(all_mollooker)):

        lat = all_mollooker[molok2_index]["lat"] 
        lon = all_mollooker[molok2_index]["lon"] 

        out_url = url + f"&point={base_lat},{base_lon}&point={lat},{lon}" 

        resp = session.get(url=out_url)
        resp_json = resp.json()

        summary = resp_json["paths"][0]

        time_taken = summary["time"]

        distance_taken = summary["distance"]

        if distance_taken == 0 or molok1_index == molok2_index:
            distance_matrix[-1].append(0)
            time_matrix[-1].append(0)
            polyline_matrix[-1].append("")
            ele_matrix[-1].append([])
            continue
        points = summary["points"]["coordinates"]
        
        elevation_data = [] 
        poly_line = []
        total_distance = 0
        for val_idx in range(len(points)-1):
            val = points[val_idx]
            next_val = points[val_idx+1]
            poly_line.append([val[1],val[0]])
            height = val[2]
            distance = distance_lat_long(val[1],val[0],next_val[1],next_val[0])*1000

            elevation_data.append([total_distance,height])

            total_distance += distance

        poly_line.append([points[-1][1],points[-1][0]])

        elevation_data.append([total_distance,points[-1][2]])

        elevation_data = [elevation_data[0]] + [elevation_data[data_idx] for data_idx in range(1,len(elevation_data)) if elevation_data[data_idx][0] != elevation_data[data_idx-1][0]]



        distance_matrix[-1].append(distance_taken)
        time_matrix[-1].append(time_taken)
        polyline_matrix[-1].append(poly_line)


        ele_matrix[-1].append(elevation_data)

    if molok1_index % 50 == 0:

        json_distance_matrix = json.dumps(distance_matrix)
        json_time_matrx= json.dumps(time_matrix)
        json_polyline_matrix= json.dumps(polyline_matrix)
        json_ele_matrix = json.dumps(ele_matrix)

        with open(distance_fn,"w") as f:
            f.write(json_distance_matrix)

        with open(time_fn,"w") as f:
            f.write(json_time_matrx)

        with open(poly_fn,"w") as f:
            f.write(json_polyline_matrix)

        with open(ele_fn,"w") as f:
            f.write(json_ele_matrix)

        with open(index_keeper,"w") as f:
            f.write(json.dumps({"index":molok1_index+1}))

json_distance_matrix = json.dumps(distance_matrix)
json_time_matrx= json.dumps(time_matrix)
json_polyline_matrix= json.dumps(polyline_matrix)
json_ele_matrix = json.dumps(ele_matrix)

with open(distance_fn,"w") as f:
    f.write(json_distance_matrix)

with open(time_fn,"w") as f:
    f.write(json_time_matrx)

with open(poly_fn,"w") as f:
    f.write(json_polyline_matrix)

with open(ele_fn,"w") as f:
    f.write(json_ele_matrix)


