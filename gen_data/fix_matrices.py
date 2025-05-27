import json
import pandas as pd
all_moloks = []
class_moloks = []

with open("../data/pp_pr_bin.json","r") as f:
    class_moloks = json.loads(f.read()) 

class_moloks[213] = 100
class_moloks[214] = 100
class_moloks[281] = 100

with open("../data/pp_pr_bin.json","w") as f:
    f.write(json.dumps(class_moloks))

"""
for molok in list(class_moloks.items()):
    adress = molok[0]
    val = molok[1]
    lat = val["lat"]
    lon = val["lon"]
    max_fill = val["max_fill"]
    new_obj = {"adress":adress,"lat":lat,"lon":lon,"max_fill":max_fill}
    all_moloks.append(new_obj)


with open("../data/molokker.json","w") as f:
    f.write(json.dumps(all_moloks))
"""


