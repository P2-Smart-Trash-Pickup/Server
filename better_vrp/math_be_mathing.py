import math
def combine_rads(dist_1:float,dist_2:float,rad_1:float,rad_2:float):
    return math.atan2(dist_1*math.tan(rad_1)+dist_2*math.tan(rad_2),dist_1+dist_2)

def lttp(points: list[list[float]], max_outputs: int) -> list[list[float]]:
    if len(points) <= max_outputs:
        return points

    n_buckets = max_outputs - 2  
    bucket_size = (len(points) - 2) / n_buckets

    downsampled = [0]

    for i in range(1, max_outputs - 1):
        start_idx = int(1 + (i - 1) * bucket_size)
        end_idx = int(1 + i * bucket_size)
        end_idx = min(end_idx, len(points) - 1)  

        bucket = points[start_idx:end_idx]

        if len(bucket) == 0:
            bucket = [points[start_idx]] if start_idx < len(points) else [points[-1]]

        next_anchor_idx = min(end_idx, len(points) - 1)
        next_anchor = points[next_anchor_idx]

        # Find point in bucket forming the largest triangle with prev & next anchors
        prev_anchor = points[downsampled[-1]]
        max_area = -1
        best_point_idx = start_idx

        for idx,point in enumerate(bucket):
            area = 0.5 * abs(
                (
                    prev_anchor[0] * (point[1] - next_anchor[1])
                    + point[0] * (next_anchor[1] - prev_anchor[1])
                    + next_anchor[0] * (prev_anchor[1] - point[1])
                )
            )
            if area > max_area:
                max_area = area
                best_point_idx = idx+start_idx

        downsampled.append(best_point_idx)

    downsampled.append(len(points)-1)

    best_points = []

    for idx in range(len(downsampled)-1):
        current_point = points[downsampled[idx]]
        for idx2 in range(idx+1,downsampled[idx+1]):
            next_point = points[idx2]
            new_radi = combine_rads(current_point[0],next_point[0],current_point[1],next_point[1]) 
            current_point[0] = next_point[0]
            current_point[1] = new_radi
        best_points.append(current_point)

    return best_points 

def merge_slopes(points:list[list[float]]) -> list[list[float]]:
    new_points = [0] 
    new_a_points = []
    for idx in range(1,len(points)-1):
        pre_radi = points[idx-1][1]
        cur_radi = points[idx][1]
        next_radi = points[idx+1][1]
        if (pre_radi < cur_radi and next_radi < cur_radi) or (pre_radi > cur_radi and next_radi > cur_radi):
            new_points.append(idx)
    new_points.append(len(points)-1)
    pre_dist = 0
    for idx in range(len(new_points)-1):
        current_point = points[new_points[idx]]
        next_point_idx = new_points[idx+1]
        for idx2 in range(new_points[idx]+1,next_point_idx):
            next_point = points[idx2]
            new_radi = combine_rads(current_point[0]-pre_dist,next_point[0]-current_point[0],current_point[1],next_point[1])
            pre_dist = current_point[0]
            current_point[0] = next_point[0]
            current_point[1] = new_radi
        new_a_points.append(current_point)

    #new_a_points = [points[idx] for idx in new_points]

    return new_a_points 
