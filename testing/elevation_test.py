import json
import requests
from tqdm import tqdm
import math


url = "http://localhost:8002/height?json="

poly_url = "http://localhost:8002/route?json="

all_moloks = []

with open("molokker.json","r") as f:
    all_moloks = json.loads(f.read())
try:

    with open("molok_polyline_matrix2.json","x") as f:
        f.write(json.dumps([]))
    with open("molok_elevation_matrix.json","x") as f:
        f.write(json.dumps([]))
except:
    pass
optimal_point = 0
for molok_line_index in tqdm(range(len(all_moloks)),desc="getting elevation"):
    base_molok = all_moloks[molok_line_index]
    base_lat = base_molok["lat"]

    base_lon = base_molok["lon"]
    line_ele = []
    line_poly = []

    if optimal_point > molok_line_index:
        continue

    polyline_matrix = []
    elevaton_matrix = []

    with open("molok_polyline_matrix2.json","r") as f:
        polyline_matrix= json.loads(f.read())
    with open("molok_elevation_matrix.json","r") as f:
        elevaton_matrix= json.loads(f.read())

    if len(elevaton_matrix)-1 >  molok_line_index:
        optimal_point = len(elevaton_matrix)-1
        continue

    for molok_index in range(len(all_moloks)):
        if len(line_ele) != molok_index:
            print(all_moloks[molok_index-1])
            print(base_molok)
            raise Exception("Weird point 1")
        if molok_index== molok_line_index:
            line_ele.append([])
            line_poly.append("")
            continue
        if molok_line_index == 159 and molok_index == 160:
            line_ele.append([])
            line_poly.append("")
            continue

        if molok_line_index == 160 and molok_index == 159:
            line_ele.append([])
            line_poly.append("")
            continue

        if molok_line_index == 588 and molok_index == 589:
            line_ele.append([])
            line_poly.append("")
            continue

        if molok_line_index == 589 and molok_index == 588:
            line_ele.append([])
            line_poly.append("")
            continue

        molok = all_moloks[molok_index]
        lat = molok["lat"]
        lon = molok["lon"]

        out_poly_obj = {"locations":[{"lat":base_lat,"lon":base_lon},{"lat":lat,"lon":lon}],"costing":"auto"}
        out_poly_url = poly_url + json.dumps(out_poly_obj)
        resp= requests.request(url=out_poly_url,method="GET")
        poly_line = resp.json()["trip"]["legs"][0]["shape"]

        out_obj = {"range":True,"encoded_polyline":poly_line}
        out_json = json.dumps(out_obj)
        out_url = url + out_json

        resp= requests.request(url=out_url,method="GET")

        elevation_data = resp.json()["range_height"]

        elevation_data = [elevation_data[0]] + [elevation_data[data] for data in range(1,len(elevation_data)) if elevation_data[data][0] != elevation_data[data-1][0]] 
        sum_angle = 0

        for data_idx2 in range(len(elevation_data)-1):
            data = elevation_data[data_idx2]
            data_next = elevation_data[data_idx2+1]

            angle = math.atan(((data_next[1]-data[1])/(data_next[0]-data[0]))*(180/math.pi))
            sum_angle+=abs(angle)

        test = []

        if len(elevation_data) -1 == 0:
            print()
            print(out_poly_url)
            print(base_molok)
            print(molok)
            print(elevation_data)
            print(poly_line)
            print(molok_line_index)
            print(molok_index)
            raise Exception("Weird point amount")

        min_angle = sum_angle/(len(elevation_data)-1) 
        has_point = True 
        point_index = len(elevation_data)-1 

        while has_point: 
            has_point = False

            for data_idx2 in range(point_index)[::-1]:
                data = elevation_data[data_idx2]
                data_next = elevation_data[point_index]

                angle = math.atan(((data_next[1]-data[1])/(data_next[0]-data[0]))*(180/math.pi))

                if abs(angle) > min_angle:
                    test.append(data_next)
                    point_index = data_idx2
                    has_point = True
                    break

        test.append(elevation_data[0])
        test = test[::-1]
        pre_angle = 0

        for data_idx in range(len(test)-1):
            data = test[data_idx]
            data_next = test[data_idx+1]

            angle = math.atan(((data_next[1]-data[1])/(data_next[0]-data[0]))*(180/math.pi))
            test[data_idx][1] =pre_angle 
            pre_angle = angle
        test[-1][1] = pre_angle
        line_poly.append(poly_line)
        line_ele.append(test)

    if len(line_ele) != len(all_moloks):
        raise Exception("Error")
    if line_ele.index([]) != molok_line_index and not (molok_line_index == 160 or molok_line_index == 589):
        raise Exception("Error 2")

    elevaton_matrix.append(line_ele)
    polyline_matrix.append(line_poly)

    with open("molok_elevation_matrix.json","w") as f:
        f.write(json.dumps(elevaton_matrix))

    with open("molok_polyline_matrix2.json","w") as f:
        f.write(json.dumps(polyline_matrix))
