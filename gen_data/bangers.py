import json
from math import cos, asin, sqrt, pi
import json
from tqdm import tqdm
all_moloks = []
with open("../data/molokker.json","r") as f:
    all_moloks = json.loads(f.read()) 
pop_pop = []
with open("../data/only_aalborg_data.json","r") as f:
    pop_pop = json.loads(f.read()) 

in_molok_range = []


def distance(lat1, lon1, lat2, lon2):
    r = 6371 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))

for molok in tqdm(all_moloks):
    base_lat = molok["lat"]
    base_lon = molok["lon"]
    for pop in pop_pop: 
        lat = pop["lat"]
        lon = pop["lon"]
        populaion = pop["population"]

        diff_d = distance(base_lat,base_lon,lat,lon)
        if diff_d < 0.25:
            in_molok_range.append([lat,lon,populaion])
with open("../data/in_range.json","w") as f:
    f.write(json.dumps(in_molok_range))
