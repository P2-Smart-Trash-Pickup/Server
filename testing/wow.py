import json

containers = []

with open("molokker.json","r") as f:
    containers = json.loads(f.read())

new_obj = {}

for con in containers:

    address = con["adress"]
    lon = con["lon"]
    lat = con["lat"]
    max_fill = con["max_fill"]

    new_obj[address] = {"lon":lon,"lat":lat,"max_fill":max_fill}
with open("molokker_class.json","w") as f:
    f.write(json.dumps(new_obj))
