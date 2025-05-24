import json

time_matrix = []
with open("../data/molok_time_matrix2 - Copy.json","r") as f:
    time_matrix = json.load(f)

all_moller = []
with open("../data/molokker.json","r") as f:
    all_moller = json.load(f)
empty_data = []

with open("../data/empty_data.json","r") as f:
    empty_data= json.load(f)
def utc_to_sec(s):
    time_str = s.split(" ")[0]
    time_split = time_str.split(":")
    hour = int(time_split[0])
    minue = int(time_split[1])
    seconds = int(time_split[2])

    total_seconds = hour*3600 + minue*60 + seconds
    return total_seconds 
iteration = 0
sum_diff = 0
for years in empty_data.keys():
    for months in empty_data[years].keys():
        for days in empty_data[years][months].keys():
            for idx,point in enumerate(empty_data[years][months][days][:-1]):
                next_point = empty_data[years][months][days][idx+1]
                next_adress = next_point["adress"]
                next_time= next_point["time"]
                adress = point["adress"]
                time = point["time"]

                pre_time = utc_to_sec(time) 
                next_time_time= utc_to_sec(next_time) 

                molok_pre_idx = None 
                molok_next_idx = None 

                for i, val in enumerate(all_moller):
                    if val["adress"] == adress:
                        molok_pre_idx = i
                        if molok_pre_idx != None and molok_next_idx != None:
                            break
                    if val["adress"] == next_adress:
                        molok_next_idx = i
                        if molok_pre_idx != None and molok_next_idx != None:
                            break
                our_time = time_matrix[molok_pre_idx][molok_next_idx]

                diff = 0
                if our_time != 0:
                    diff = (next_time_time - pre_time) / (our_time/1000)

                sum_diff += diff
                iteration += 1
average_diff = sum_diff/iteration
print(average_diff)

for i,_ in enumerate(time_matrix):
    for y,_ in enumerate(time_matrix[i]):
        index_time = time_matrix[i][y]
        changed = index_time*average_diff 
        time_matrix[i][y] = changed


iteration = 0
sum_diff = 0
for years in empty_data.keys():
    for months in empty_data[years].keys():
        for days in empty_data[years][months].keys():
            for idx,point in enumerate(empty_data[years][months][days][:-1]):
                next_point = empty_data[years][months][days][idx+1]
                next_adress = next_point["adress"]
                next_time= next_point["time"]
                adress = point["adress"]
                time = point["time"]

                pre_time = utc_to_sec(time) 
                next_time_time= utc_to_sec(next_time) 

                molok_pre_idx = None 
                molok_next_idx = None 

                for i, val in enumerate(all_moller):
                    if val["adress"] == adress:
                        molok_pre_idx = i
                        if molok_pre_idx != None and molok_next_idx != None:
                            break
                    if val["adress"] == next_adress:
                        molok_next_idx = i
                        if molok_pre_idx != None and molok_next_idx != None:
                            break
                our_time = time_matrix[molok_pre_idx][molok_next_idx]
                diff = 0
                if our_time != 0:
                    diff = (next_time_time - pre_time) / (our_time/1000)

                sum_diff += diff
                iteration += 1

average_diff = sum_diff/iteration
print(average_diff)

with open("../data/molok_time_matrix3.json","w") as f:
    json.dump(time_matrix,f)



