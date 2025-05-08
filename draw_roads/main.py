import math
import matplotlib.pyplot as plt
import polyline

import requests

import json

out_obj = {"locations":[],"costing":"auto"}

points = [[57.16688695403482, 10.14570493104723],[57.048621525369114, 9.920426837329428]]

for point in points:
    new_obj = {"lat":point[0],"lon":point[1]}
    out_obj["locations"].append(new_obj)

out_str = json.dumps(out_obj)

url_directions = f"http://localhost:8002/route?json={out_str}"

resp = requests.get(url_directions)
obj = resp.json()
chosen_polyline = obj["trip"]["legs"][0]["shape"]

points = polyline.decode(chosen_polyline,5)

radius = 6.378

out_obj = {"range":True,"encoded_polyline":chosen_polyline,"resampling_distance":1000}
out_str = json.dumps(out_obj) 

url_elevation = f"http://localhost:8002/height?json={out_str}"

resp = requests.get(url_elevation)
obj = resp.json()
range_height = obj["range_height"]
collective = [i for i in range(len(points)-1) if range_height[i][1] != range_height[i+1][1] ]
points = [points[i] for i in collective]
range_height = [range_height[i] for i in collective]


def convert_lon_lat(lon,lat,r):
    x = r * math.cos(lat) * math.cos(lon)
    y = r* math.cos(lat) * math.sin(lon)
    z = r * math.sin(lat)

    return x,y,z


fig = plt.figure()
ax = fig.add_subplot(111,projection="3d")
"""
u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
x = np.cos(u)*np.sin(v)*radius
y = np.sin(u)*np.sin(v)*radius
z = np.cos(v)*radius

ax.plot(x, y, z, color="r")
"""

all_x = []
all_y = []
all_z = []
for point_index in range(len(points)):
    X,Y,Z = convert_lon_lat(points[point_index][1],points[point_index][0],radius)
    x = X/Z
    y = Y/Z
    z = range_height[point_index][1]

    all_x.append(x)
    all_y.append(y)
    all_z.append(z)
    if point_index == 0 :
        ax.scatter(x,y,z,c="g")
    if point_index == len(points) -1:
        ax.scatter(x,y,z,c="r")
    if point_index != 0 and point_index != len(points)-1 and not (range_height[point_index-1][1] < z < range_height[point_index+1][1] or range_height[point_index-1][1] > z > range_height[point_index+1][1]):
        ax.scatter(x,y,z,c="y")



ax.plot(all_x,all_y,all_z)

    

plt.show()
