import random
import math

def sum_route(route,demand):
    total_demand = 0
    for i in route:
        total_demand += demand[i]
    return total_demand 

def solve_vrp_clark_wright(distance_matrix,demand,vehicle_capacity):
    savings = []
    for i in range(1,len(distance_matrix)):
        for j in range(1,len(distance_matrix)):
            if i == j:
                continue
            depot_cost_i = distance_matrix[i][0]
            depot_cost_j = distance_matrix[0][j]
            customer_cost = distance_matrix[i][j]

            saving = depot_cost_i + depot_cost_j - customer_cost
            savings.append([saving,[i,j]])
    savings.sort(key=lambda arr:arr[0],reverse=True)
    routes = [[0,i,0] for i in range(1,len(distance_matrix))]
    for saving in savings:
        route_i,route_j = None,None
        i = saving[1][0]
        j = saving[1][1]
        for route in routes:
            if i in route and j not in route:
                route_i = route
            elif j in route and i not in route:
                route_j = route
        if route_i is None or route_j is None:
            continue

        total_demand = sum_route(route_i,demand) + sum_route(route_j,demand)
        if total_demand > vehicle_capacity:
            continue
        
        merged_routed = route_i[:-1] + route_j[1:]
        routes.remove(route_i)
        routes.remove(route_j)
        routes.append(merged_routed)
    total_distance = 0
    for route in routes:
        for customer in range(len(route)-1):
            total_distance += distance_matrix[route[customer]][route[customer+1]] 
        total_distance += distance_matrix[route[-2]][0]
    return routes,total_distance 

def draw_clark_wright(points,routes,draw):
    for route in routes:
        r = random.randint(0,255)
        g = random.randint(0,255)
        b = random.randint(0,255)
        for customer in range(len(route)-1):
                    current_point = points[route[customer]]
                    next_point = points[route[customer+1]]

                    draw.line([(current_point[0],current_point[1]),(next_point[0],next_point[1])],fill=(r,g,b))
                    slope = 0
                    pependicular_slope = 1
                    try:
                        slope = (next_point[1] - current_point[1])/(next_point[0] - current_point[0]) 
                        pependicular_slope = -1/slope
                    except:
                        pass

                    mid_width =current_point[0] + (next_point[0] - current_point[0])/2
                    mid_height = current_point[1] + (next_point[1] - current_point[1])/2

                    tip_width = current_point[0] + (next_point[0] - current_point[0])*0.6
                    tip_height = current_point[1] + (next_point[1] - current_point[1])*0.6

                    new_x_1 = mid_width + 5/math.sqrt(1+pependicular_slope**2)
                    new_y_1 = mid_height + (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

                    new_x_2 = mid_width - 5/math.sqrt(1+pependicular_slope**2)
                    new_y_2 = mid_height - (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

                    draw.polygon([(tip_width,tip_height),(new_x_1,new_y_1),(new_x_2,new_y_2)],fill=(r,g,b))

        current_point = points[route[-2]]
        next_point = points[route[-1]]

        draw.line([(current_point[0],current_point[1]),(next_point[0],next_point[1])],fill=(r,g,b))
        slope = 0
        pependicular_slope = 1
        try:
            slope = (next_point[1] - current_point[1])/(next_point[0] - current_point[0]) 
            pependicular_slope = -1/slope
        except:
            pass

        mid_width =current_point[0] + (next_point[0] - current_point[0])/2
        mid_height = current_point[1] + (next_point[1] - current_point[1])/2

        tip_width = current_point[0] + (next_point[0] - current_point[0])*0.6
        tip_height = current_point[1] + (next_point[1] - current_point[1])*0.6

        new_x_1 = mid_width + 5/math.sqrt(1+pependicular_slope**2)
        new_y_1 = mid_height + (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

        new_x_2 = mid_width - 5/math.sqrt(1+pependicular_slope**2)
        new_y_2 = mid_height - (pependicular_slope*5)/math.sqrt(1+pependicular_slope**2)

        draw.polygon([(tip_width,tip_height),(new_x_1,new_y_1),(new_x_2,new_y_2)],fill=(r,g,b))
