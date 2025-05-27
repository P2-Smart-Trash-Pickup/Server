import folium
import json

molokker_json_data = {}
with open("molokker.json","r") as f:
    bangers = f.read()
    molokker_json_data = json.loads(bangers)

map = folium.Map()

min_lat = float("inf")
min_lon = float("inf")

max_lat = -float("inf")
max_lon = -float("inf")

for molok in molokker_json_data:
    adress = molok["adress"]
    lon = molok["lon"]
    lat = molok["lat"]

    if lat > max_lat:
        max_lat = lat
    elif lat < min_lat:
        min_lat = lat

    if lon > max_lon:
        max_lon = lon
    elif lon < min_lon:
        min_lon = lon

    folium.CircleMarker(location=[lat,lon],radius=1,popup=adress).add_to(map)

map.fit_bounds([[max_lat,min_lon],[min_lat,max_lon]],max_zoom=15)

map.save("map.html")
