import time
from gen_data import generate_distance_matrix,gen_data_or
from vrp_milp import solve_vrp_milp 
from vrp_clark_wright import solve_vrp_clark_wright
from vrp_or import solve_vrp_google
from vrp_tabu import solve_vrp_tabu
from vrp_gls import solve_cutom_gls
import csv
class VRPMethod:
    def __init__(self,name:str,method) -> None:
        self.name = name
        self.method = method
        pass
def make_test(vehicle_amount,step,times):

    with open("test_result.csv","w",newline="") as csvfile:
        csv_writer= csv.writer(csvfile)
        csv_writer.writerow(["Points","OR_dist","CW_dist","GLS_dist","OR_time","CW_time","GLS_time"])

    for i in range(1,times,step):
        #milp_total_duration = 0
        #milp_distance_total = 0

        c_w_total_duration = 0
        c_w_distance_total = 0

        or_total_duration = 0
        or_distance_total = 0

        #tabu_total_duration = 0
        #tabu_distance_total = 0

        gls_total_duration = 0
        gls_distance_total = 0

        difference_procent = 0
        print(f"{i+3} points")
        for _ in range(10):
            _,distance_matrix = generate_distance_matrix(i+3,500,500)
            vehicle_capacity = (i+3)*2 

            demand = [0]

            for _ in range(1,i+3):
                demand.append(1)

            data = gen_data_or(distance_matrix,len(distance_matrix),vehicle_amount,demand)
            gls_start = time.time()
            _,gls_distance = solve_cutom_gls(distance_matrix,demand,vehicle_capacity)
            gls_duration = time.time() - gls_start

            or_time = 1
            if gls_duration > or_time:
                or_time = gls_duration
            or_start = time.time()
            or_distance = solve_vrp_google(data,i,1,int(or_time))
            or_duration = time.time() - or_start
                
            c_w_start = time.time()
            _,c_w_distance = solve_vrp_clark_wright(distance_matrix,demand,vehicle_capacity)
            c_w_duration = time.time() - c_w_start
            """
            milp_start = time.time()
            _,milp_distance,_,_ = solve_vrp_milp(distance_matrix,demand,vehicle_amount,vehicle_capacity)
            milp_duration = time.time() - milp_start
            """

            """
            tabu_start = time.time()
            _,tabu_distance = solve_vrp_tabu(distance_matrix,demand,vehicle_capacity,1000,100)
            tabu_duration = time.time() - tabu_start
            """


            #difference_procent += (c_w_distance - milp_distance) / milp_distance

            #milp_total_duration += milp_duration 
            c_w_total_duration += c_w_duration 
            or_total_duration += or_duration

            #milp_distance_total += milp_distance
            c_w_distance_total += c_w_distance
            or_distance_total += or_distance

            #tabu_total_duration += tabu_duration
            #tabu_distance_total += tabu_distance

            gls_total_duration += gls_duration
            gls_distance_total += gls_distance

        #milp_total_duration= milp_total_duration/ 10
        c_w_total_duration= c_w_total_duration/ 10
        difference_procent = difference_procent / 10

        #milp_distance_total = milp_distance_total / 10
        c_w_distance_total = c_w_distance_total / 10

        or_total_duration = or_total_duration / 10
        or_distance_total = or_distance_total / 10

        """
        tabu_total_duration = tabu_total_duration/ 10
        tabu_distance_total = tabu_distance_total/ 10
        """

        gls_distance_total = gls_distance_total /10
        gls_total_duration = gls_total_duration /10

        #print(f"Milp distance: {milp_distance_total}")
        print(f"CW distance: {c_w_distance_total}")
        print(f"OR distance: {or_distance_total}")
        #print(f"TABU distance: {tabu_distance_total}")
        print(f"GLS distance: {gls_distance_total}")
        #print(f"Procentwise difference: {difference_procent}%")
        print("")
        #print(f"MILP took {"%.2f" % milp_total_duration}s")
        print(f"CW took {"%.2f" % c_w_total_duration}s")
        print(f"OR took {"%.2f" % or_total_duration}s")
        #print(f"TABU took {"%.2f" % tabu_total_duration}s")
        print(f"GLS took {"%.2f" % gls_total_duration}s")
        print("")

        with open("test_result.csv","a",newline="") as csvfile:
            csv_writer= csv.writer(csvfile)
            csv_writer.writerow([i,or_distance_total,c_w_distance_total,gls_distance_total,or_total_duration,c_w_total_duration,gls_total_duration])

