import json
pp_pr_bin = []
with open("../data/pp_pr_bin.json","r") as f:
    pp_pr_bin = json.load(f)

molokker = []
with open("../data/molokker.json","r") as f:
    molokker = json.load(f)

fill_rates = []
ratio = (354/(365*4*7))/0.129
for val in zip(pp_pr_bin,molokker):
    people = val[0]
    molok = val[1]
    fill_rate = people*ratio 
    max_fill = molok["max_fill"]
    fill_rates.append(fill_rate)

with open("../data/fill_rates.json","w") as f:
    json.dump(fill_rates,f)

