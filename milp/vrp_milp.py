from pulp import LpProblem, LpVariable, LpMinimize,  LpBinary, lpSum,value,PULP_CBC_CMD

import random
import math

def solve_vrp_milp(distance_matrix,demand,vehicle_amount,vehicle_capacity):
    prob = LpProblem("Warehouse", LpMinimize)

    x = LpVariable.dicts("x",((i,j,k) 
        for i in range(len(distance_matrix)) 
        for j in range(len(distance_matrix)) 
        for k in range(vehicle_amount)),
                     cat=LpBinary)
    prob += lpSum(distance_matrix[i][j] * x[i,j,k]
        for i in range(len(distance_matrix)) 
        for j in range(len(distance_matrix)) 
        for k in range(vehicle_amount))

    for j in range(len(distance_matrix)):
        for k in range(vehicle_amount):
            prob += lpSum(x[i,j,k] for i in range(len(distance_matrix))) == lpSum(x[j,l,k] for l in range(len(distance_matrix))) 

    for j in range(1,len(distance_matrix)):
        prob += lpSum(x[i,j,k]
                  for k in range(vehicle_amount) 
                  for i in range(len(distance_matrix))) == 1

    for k in range(vehicle_amount):
        prob += lpSum(x[0,j,k] for j in range(1,len(distance_matrix))) <= 1  
        prob += lpSum(x[i,0,k] for i in range(1,len(distance_matrix))) <= 1 

    for i in range(len(distance_matrix)):
        for k in range(vehicle_amount):
            prob += x[i,i,k] == 0

    """
    for k in range(vehicle_amount):
        prob += lpSum(demand[j]*x[i,j,k]
                  for i in range(len(distance_matrix))
                  for j in range(1,len(distance_matrix))
                  ) <= vehicle_capacity 
    """
    u = LpVariable.dicts("u", 
                    ((i, k) for i in range(1,len(distance_matrix)) 
                            for k in range(vehicle_amount)),
                    lowBound=0, upBound=len(distance_matrix)-1)

    """
    for i in range(1,len(distance_matrix)):
        for j in range(1,len(distance_matrix)):
            if i != j:
                for k in range(vehicle_amount):
                    prob += u[i,k] - u[j,k] + (len(distance_matrix)-1) * x[i,j,k] <= len(distance_matrix) - 2
    """

    for i in range(1,len(distance_matrix)):
        for j in range(1,len(distance_matrix)):
            if i != j:
                for k in range(vehicle_amount):
                        prob += u[j,k] - u[i,k] >= demand[j] - vehicle_capacity*(1-x[i,j,k]) 

    for i in range(1,len(distance_matrix)):
        for k in range(vehicle_amount):
            prob += demand[i] <= u[i,k] <= vehicle_capacity

    y = LpVariable.dicts("y", (k for k in range(vehicle_amount)), cat=LpBinary)

    for k in range(vehicle_amount):
        for i in range(len(distance_matrix)):
            for j in range(len(distance_matrix)):
                prob += x[i,j,k] <= y[k]  # If y[k]=0, x[i,j,k]=0

    # If y[k] = 1, vehicle must leave and return to depot exactly once
        prob += lpSum(x[0,j,k] for j in range(1, len(distance_matrix))) == y[k]  # Departure
        prob += lpSum(x[i,0,k] for i in range(1, len(distance_matrix))) == y[k]  # Return

    prob.solve(PULP_CBC_CMD(msg=False))

    #prob.solve()
    """
    for v in prob.variables():
        print(v.name, "=", v.varValue)
    """

    return prob,value(prob.objective),x,y

def draw_milp(distance_matrix,points,x,vehicles,vehicle_amount,draw):
    for k in range(vehicle_amount):
        #print(f"\nVehicle {k+1} Route:")
        if value(vehicles[k]) != 1:
            continue
        current_location = 0 
        route = [0]
        route_complete = False
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        
        while not route_complete:
            for j in range(len(distance_matrix)):
                if value(x[current_location,j,k]) == 1:
                    draw.line([(points[current_location][0],points[current_location][1]),(points[j][0],points[j][1])],fill=(r,g,b))
                    slope = 0
                    pependicular_slope = 1
                    try:
                        slope = (points[j][1] - points[current_location][1])/(points[j][0] - points[current_location][0]) 
                        pependicular_slope = -1/slope
                    except:
                        pass

                    mid_width =points[current_location][0] + (points[j][0] - points[current_location][0])/2
                    mid_height = points[current_location][1] + (points[j][1] - points[current_location][1])/2

                    tip_width = points[current_location][0] + (points[j][0] - points[current_location][0])*0.6
                    tip_height = points[current_location][1] + (points[j][1] - points[current_location][1])*0.6

                    new_x_1 = mid_width + 5/math.sqrt(1+pependicular_slope**2)
                    new_y_1 = mid_height + (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

                    new_x_2 = mid_width - 5/math.sqrt(1+pependicular_slope**2)
                    new_y_2 = mid_height - (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

                    draw.polygon([(tip_width,tip_height),(new_x_1,new_y_1),(new_x_2,new_y_2)],fill=(r,g,b))

                    route.append(j)
                    current_location = j
                    if j == 0:
                        route_complete = True
                    break

        
        #print(" -> ".join(map(str, route)))
