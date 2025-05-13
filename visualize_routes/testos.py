import json
mollokker = {}
with open("molokker_class.json","r") as f:
    mollokker = json.loads(f.read()) 
"Willy Brandts Vej 31, 9220 Aalborg Øst"
"Willy Brandts Vej 31, 9220 Aalborg Øst"
for val in mollokker.keys():
    print(val)
print(mollokker["Willy Brandts Vej 31, 9220 Aalborg Øst"])
