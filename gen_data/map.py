import pandas as pd
import folium
from folium.plugins import HeatMap
from tqdm import tqdm
from math import cos, asin, sqrt, pi
import json

file_loc = "../data/dnk_general_2020.csv"

population_data = pd.read_csv(file_loc)

print(population_data.loc[:,"longitude"].iloc[2])
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
only_aalborg = []
for index in tqdm(range(len(population_data.loc[:,"longitude"])),desc="sui"):
    lon = population_data.loc[:,"longitude"].iloc[index]
    lat = population_data.loc[:,"latitude"].iloc[index]
    population = population_data.loc[:,"dnk_general_2020"].iloc[index]
    distances = distance(center[0],center[1],lat,lon)
    if distances < 30:
        obj = {"lat":lat,"lon":lon,"population":population} 
        only_aalborg.append(obj)
        #heat_data.append([lat,lon,population])
        #min_lat = lat if lat < min_lat else min_lat 
        #min_lon = lon if lon < min_lon else min_lon 

        #max_lat = lat if lat > max_lat else max_lat 
        #max_lon = lon if lon > max_lon else max_lon 
with open("../data/only_aalborg_data.json","w") as f:
    f.write(json.dumps(only_aalborg))
"""
map.fit_bounds([[min_lat,min_lon],[max_lat,max_lon]])
HeatMap(heat_data).add_to(map)

map.save("heat_test_allborg.html")
"""






