import json
import requests

empty_data = {} 
molokker = {} 
distance_matrix = []
snall_molok = []
poly_matrix = {}
ele_matrix = []

with open("empty_data.json","r") as f:
    empty_data = json.loads(f.read())

with open("molokker.json","r") as f:
    molokker = json.loads(f.read())

with open("molok_distance_matrix.json","r") as f:
    distance_matrix = json.loads(f.read())

with open("molok_polyline_matrix2.json","r") as f:
    poly_matrix = json.loads(f.read())

with open("molok_elevation_matrix.json","r") as f:
    ele_matrix= json.loads(f.read())

with open("snall_moloks.json","r") as f:
    snall_molok= json.loads(f.read())
for line_idx in range(len(poly_matrix)):
    line = poly_matrix[line_idx]
    for val_idx in range(len(line)):
        val = line[val_idx]
        if val == "":
            if val_idx != line_idx and not (line_idx==159 or line_idx==160 or line_idx==589 or line_idx==588): 
                print(f"val idx: {val_idx}")
                print(f"line idx: {line_idx}")
                print(len(line))
                print(len(poly_matrix))

                all_occ_pre = [i for i,val in enumerate(poly_matrix[line_idx-1]) if val == ""]
                all_occ = [i for i,val in enumerate(line) if val == ""]
                all_occ_next = [i for i,val in enumerate(poly_matrix[line_idx+1]) if val == ""]
                if all_occ_pre == all_occ:
                    print("sus")
                print(f"pre: {all_occ_pre}")
                print(f"current: {all_occ}")
                print(f"next: {all_occ_next}")
                    
                raise Exception("aint no sunshine when shes gone")

"""
print(f"antal molokker: {len(molokker)}")
print(f"antal matrix: {len(distance_matrix)}")
print(f"antal i matrix række: {len(distance_matrix[0])}")
"""

"""
first_container = molokker[0]
lon = first_container["lon"]
lat = first_container["lat"]
for a in range(1,len(molokker)):

    second_container = molokker[a]

    lon_2 = second_container["lon"]
    lat_2 = second_container["lat"]

    url = "http://localhost:8002/route?json="

    req_json = json.dumps({"locations":[{"lat":lat,"lon":lon},{"lat":lat_2,"lon":lon_2}],"costing":"auto"})

    out_url = url+req_json

    resp = requests.request(url=out_url,method="GET")
    resp_json = resp.json()
    summary = resp_json["trip"]["summary"]
    time_taken = summary["time"]
    distance_taken = summary["length"]
    poly_line = resp_json["trip"]["legs"][0]["shape"]

    if distance_taken != distance_matrix[1][a+1]:
        print(a)
        print(second_container["adress"])
        raise Exception("err")

"""
"""
for month in empty_data.values():
    for day in month.values():
        for val in day.values():
            for nice in val:
                adress = nice["adress"]
                adress_exists = False
                for molok in molokker:
                    if molok["adress"] == adress:
                        adress_exists = True
                if not adress_exists:
                    print(adress)
"""
                    
