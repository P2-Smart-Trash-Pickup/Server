import json
from pathlib import Path

project_root = Path(__file__).parent.parent

from milp.vrp_gls import solve_cutom_gls 

molok_dates = {}
with open(str(project_root)+"/data/empty_data.json","r") as f:
    molok_dates = json.loads(f.read())

all_moloks = []
with open(str(project_root)+"/data/molokker.json","r") as f:
    all_moloks = json.loads(f.read())

distance_matrix = []
with open(str(project_root)+"/data/molok_distance_matrix2.json","r") as f:
    distance_matrix = json.loads(f.read())
full_distance = 0
full_distance_custom = 0
better = {}
printed = False
for years in molok_dates.keys():
    if not better.get(years):
        better[years] = {}
    for months in molok_dates[years].keys():
        if not better[years].get(months):
            better[years][months] = {}
        for days in molok_dates[years][months].keys():

            if not better[years][months].get(days):
                better[years][months][days] = [] 
            routes = molok_dates[years][months][days]
            routes.insert(0,all_moloks[0])
            routes.append(all_moloks[0])
            temp_distance_matrix = []
            last_index = 0

            corresponding= {}

            for molok1_idx in range(len(routes)-1):
                molok = routes[molok1_idx]
                adress = molok["adress"]

                molok2 = routes[molok1_idx+1]
                adress2 = molok2["adress"]
                pre_current_idx = 0
                for i in range(len(all_moloks)):
                    if all_moloks[i]["adress"]== adress:
                        pre_current_idx = i
                        break

                current_idx = 0
                for i in range(len(all_moloks)):
                    if all_moloks[i]["adress"]== adress2:
                        current_idx = i
                        break
                temp_distance_matrix.append([])

                full_distance += distance_matrix[pre_current_idx][current_idx]
                last_index = current_idx

                corresponding[molok1_idx] = pre_current_idx  
                for molok2_idx in range(len(routes)-1):

                    molok2 = routes[molok2_idx]
                    adress2 = molok2["adress"]

                    current_idx = 0
                    for i in range(len(all_moloks)):
                        if all_moloks[i]["adress"]== adress2:
                            current_idx = i
                            break
                    temp_distance_matrix[-1].append(distance_matrix[pre_current_idx][current_idx])

            full_distance += distance_matrix[last_index][0]

            if not printed:
                printed = True 

            demands = [0] 
            for i in range(len(temp_distance_matrix)-1):
                demands.append(1)


            new_route,cost = solve_cutom_gls(temp_distance_matrix,demands,len(routes)*2,max_time=99999)
            new_route[0] = [corresponding[i] for i in new_route[0]]

            better[years][months][days] = new_route[0][1:-1]
            if len(new_route[0]) != len(routes):
                print(len(temp_distance_matrix))
                print(len(new_route[0]))
                print(len(routes))
                raise Exception("Damn")
            full_distance_custom += cost
print(full_distance)
print(full_distance_custom)

with open(str(project_root)+"/data/better.json","w") as f:
    f.write(json.dumps(better))




