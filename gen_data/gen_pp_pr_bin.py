import json
from math import cos, asin, sqrt, pi
from tqdm import tqdm

all_moloks = []
with open("../data/molokker.json","r") as f:
    all_moloks = json.loads(f.read())

file_loc = "../data/dnk_general_2020.csv"

population_data = {} 

with open("../data/in_range.json","r") as f:
    population_data= json.loads(f.read())

pp_pr_bin = [0 for _ in all_moloks]
last_idx = 0
try:
    with open("../data/pp_pr_bin.json","x") as f:
        f.write(json.dumps({"idx":0,"pp_pr_bin":[0 for _ in all_moloks]}))
except:
    with open("../data/pp_pr_bin.json","r") as f:
        pp_pr_bin = json.loads(f.read())

def distance(lat1, lon1, lat2, lon2):
    r = 6371 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))
longest_distance = 0.25 

for index in tqdm(range(len(population_data)),desc="going_goog"):
    data_point = population_data[index]
    base_lon = data_point[1] 
    base_lat = data_point[0] 
    population = data_point[2] 
    shortest_distance = float("inf")
    best_moloks = []
    for molok_idx in range(1,len(all_moloks)):
        molok = all_moloks[molok_idx]
        lat = molok["lat"]
        lon = molok["lon"]
        diff_distance = distance(base_lat,base_lon,lat,lon)
        if diff_distance == shortest_distance:
            best_moloks.append(molok_idx)
        elif diff_distance < shortest_distance:
            best_moloks = []
            shortest_distance = diff_distance
            best_moloks.append(molok_idx)
    for idx in best_moloks:
        pp_pr_bin[idx] += population

with open("../data/pp_pr_bin.json","w") as f:
    f.write(json.dumps(pp_pr_bin))
