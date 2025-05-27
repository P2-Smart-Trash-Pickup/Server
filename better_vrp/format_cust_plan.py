import json
import csv
cust_plan = []
with open("../data/optimized_nord_plan.json","r") as f:
    cust_plan = json.load(f)

all_moloks = []
with open("../data/molokker.json","r") as f:
    all_moloks = json.load(f)

data = []

for day_idx,routes in enumerate(cust_plan): 
    for route in routes:
        for point in route[:-1]:
            mol = all_moloks[point]
            lat = mol["lat"]
            lon = mol["lon"]
            adress = mol["adress"]
            desc = "" 
            if point == 0:

                desc = "DEPOT"
            else:
                desc = "CONTAINER"
            out_data = {"Name":adress,"Latitude":lat,"Longitude":lon,"Description":desc,"Day":day_idx}
            data.append(out_data)


with open("optimized_nord_plan.csv","w",newline="") as f:
    writer = csv.DictWriter(f,fieldnames=["Name","Latitude","Longitude","Description","Day"])
    writer.writeheader()
    writer.writerows(data)

