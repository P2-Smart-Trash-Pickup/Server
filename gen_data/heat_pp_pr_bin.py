
import pandas as pd
import folium
from folium.plugins import HeatMap
from tqdm import tqdm
from math import cos, asin, sqrt, pi
import json

all_moloks = []
with open("../data/molokker.json","r") as f:
    all_moloks = json.loads(f.read()) 

pp_pr_bin= []
with open("../data/pp_pr_bin.json","r") as f:
    pp_pr_bin= json.loads(f.read())
only_aa = []
with open("../data/only_aalborg_data.json","r") as f:
    only_aa = json.loads(f.read())

map = folium.Map()
min_lat = float("inf")
min_lon = float("inf")

max_lat = -float("inf")
max_lon = -float("inf")
center = [57.045145680231414, 9.947690880035433]

def distance(lat1, lon1, lat2, lon2):
    r = 6371 # km
    p = pi / 180

    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    return 2 * r * asin(sqrt(a))
heat_data = []
for index in tqdm(range(len(all_moloks)),desc="sui"):
    molok = all_moloks[index]
    lon = molok["lon"] 
    lat = molok["lat"] 
    population = pp_pr_bin[index]
    if population == 0:

        #heat_data.append([lat,lon,population])
        folium.Marker(location=[lat,lon],popup=str(population)).add_to(map)
    min_lat = lat if lat < min_lat else min_lat 
    min_lon = lon if lon < min_lon else min_lon 

    max_lat = lat if lat > max_lat else max_lat 
    max_lon = lon if lon > max_lon else max_lon 

for index in tqdm(range(len(only_aa)),desc="sui"):
    molok = only_aa[index]
    lon = molok["lon"] 
    lat = molok["lat"] 
    heat_data.append([lat,lon])


map.fit_bounds([[min_lat,min_lon],[max_lat,max_lon]])
HeatMap(heat_data).add_to(map)

map.save("sugoi2.html")
