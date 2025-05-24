from math import cos, sin, atan2, pi, asin, sqrt
from copy import copy
from file_manipulation import load_moloks
import random
from PIL import Image, ImageDraw
import math
from typing import List, Tuple


def calc_angle(
    lat_start: float, lon_start: float, lat_end: float, lon_end: float
) -> float:
    lat_start = to_radi(lat_start)
    lat_end = to_radi(lat_end)
    lon_start = to_radi(lon_start)
    lon_end = to_radi(lon_end)
    dif_lon = lon_end - lon_start
    const_y = sin(dif_lon) * cos(lat_end)
    const_x = cos(lat_start) * sin(lat_end) - sin(lat_start) * cos(lat_end) * cos(
        dif_lon
    )
    deg = atan2(const_y, const_x)

    # deg = deg * 180/pi

    # deg = (deg + 360) %360

    # deg = (deg+180) % 360

    return deg


def circular_line_sweep_clustering(
    points: List[Tuple[float, float]],
    center: Tuple[float, float] = (0, 0),
    max_angular_gap: float = 30.0,  # in degrees
    min_cluster_size: int = 1,
) -> List[List[Tuple[float, float]]]:
    """
    Perform circular line sweep clustering around a central point.

    Args:
        points: List of (x, y) coordinate tuples
        center: (x, y) coordinates of the central point
        max_angular_gap: Maximum angular gap (degrees) between points in a cluster
        min_cluster_size: Minimum number of points in a cluster

    Returns:
        List of clusters (each cluster is a list of points)
    """
    if not points:
        return []

    # Convert max angular gap to radians for calculations
    max_gap_rad = math.radians(max_angular_gap)

    # Convert points to polar coordinates (relative to center)
    polar_points = []
    # cx, cy = center
    for x, y in points:
        # Calculate angle relative to center
        # dx, dy = x - cx, y - cy
        # angle = math.atan2(dy, dx)  # returns [-π, π]
        angle = calc_angle(center[0], center[1], x, y)
        polar_points.append((angle, x, y))

    # Sort points by angle
    polar_points.sort()

    clusters = []
    current_cluster = []

    # Handle circular nature by duplicating points with +2π
    extended_points = polar_points + [
        (angle + 2 * math.pi, x, y) for angle, x, y in polar_points
    ]

    for i in range(1, len(extended_points)):
        prev_angle, prev_x, prev_y = extended_points[i - 1]
        curr_angle, curr_x, curr_y = extended_points[i]

        angular_gap = curr_angle - prev_angle

        if angular_gap <= max_gap_rad:
            if not current_cluster:
                current_cluster.append((prev_x, prev_y))
            current_cluster.append((curr_x, curr_y))
        else:
            if current_cluster and len(current_cluster) >= min_cluster_size:
                clusters.append(current_cluster)
            current_cluster = []

    # Handle the last cluster
    if current_cluster and len(current_cluster) >= min_cluster_size:
        clusters.append(current_cluster)

    # Remove duplicate clusters from the circular extension
    # We only keep clusters that start in the original [-π, π] range
    unique_clusters = []
    seen = set()
    for cluster in clusters:
        # Use the first point as the cluster identifier
        first_point = cluster[0]
        if first_point not in seen:
            seen.add(first_point)
            # Only add if the first point was in the original set
            if (first_point[0], first_point[1]) in points:
                unique_clusters.append(cluster)

    return unique_clusters


def to_radi(deg: float):
    return deg * pi / 180


def distance_lat_long(lat1, lon1, lat2, lon2):
    r = 6371  # km
    p = pi / 180

    a = (
        0.5
        - cos((lat2 - lat1) * p) / 2
        + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    )
    return 2 * r * asin(sqrt(a))


def merge_clusters(clusters):
    """
    Merge clusters that share common points.
    """
    # Implement union-find or other merging approach here
    # This is a simplified version
    merged = []
    used_points = set()

    for cluster in clusters:
        # Check if any point in this cluster is already in a merged cluster
        found = False
        for i, m_cluster in enumerate(merged):
            if any(point in m_cluster for point in cluster):
                # Merge with existing cluster
                merged[i] = list(set(m_cluster + cluster))
                found = True
                break

        if not found:
            merged.append(cluster)

    return merged


class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))  # Each point is its own parent initially
        self.cluster_count = size  # Tracks total clusters (initially `n`)

    def find(self, x):
        """Find the root cluster of `x` with path compression."""
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # Path compression
            x = self.parent[x]
        return x

    def union(self, x, y):
        """Merge clusters containing `x` and `y`."""
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root != y_root:
            self.parent[y_root] = x_root  # Attach y's tree to x's root
            self.cluster_count -= 1  # One fewer cluster now


def plot_lat_lon(
    lat, lon, min_lat, max_lat, min_lon, max_lon, width, height
) -> tuple[float, float]:

    # Project coordinates
    x = (lon - min_lon) / (max_lon - min_lon) * width

    y = height - (lat - min_lat) / (max_lat - min_lat) * height
    return x, y


if __name__ == "__main__":
    moloks = load_moloks()
    lons = [i["lon"] for i in moloks]

    min_lon = min(lons)
    max_lon = max(lons)

    lats = [i["lat"] for i in moloks]

    min_lat = min(lats)
    max_lat = max(lats)

    all_points = []
    width = 1920
    height = 1080
    img = Image.new("RGB", (width + 20, height + 20))
    draw = ImageDraw.Draw(img)
    """
    for i in range(width):
        for y in range(height):
            #all_points.append({"lat":i,"lon":y})

            all_points.append((i,y))
    moloks = random.sample(all_points,100)
    """

    cluster_amount = float("inf")
    clusters = []
    ang_gap = 0.01

    moloks = list(zip(lats, lons))
    while cluster_amount > 11:
        clusters = circular_line_sweep_clustering(
            moloks, max_angular_gap=ang_gap, center=moloks[0]
        )
        cluster_amount = len(clusters)
        print(f"cluster amount: {cluster_amount}")

        for clust in clusters:
            # print(clust)
            col_r = random.randint(0, 255)
            col_g = random.randint(0, 255)
            col_b = random.randint(0, 255)
            min_x = float("inf")
            max_x = -float("inf")

            min_y = float("inf")
            max_y = -float("inf")
            for point in clust:
                """
                lat = moloks[point]["lat"]
                lon = moloks[point]["lon"]
                """
                x, y = plot_lat_lon(
                    point[0],
                    point[1],
                    min_lat,
                    max_lat,
                    min_lon,
                    max_lon,
                    width,
                    height,
                )
                # x = point[0]
                # y = point[1]
                min_x = x if x < min_x else min_x
                max_x = x if x > max_x else max_x

                min_y = y if y < min_y else min_y
                max_y = y if y > max_y else max_y
                draw.circle((x, y), 10, fill=(col_r, col_g, col_b))
            draw.rectangle(
                [(min_x, min_y), (max_x, max_y)], outline=(col_r, col_g, col_b)
            )

        ang_gap += 0.01
    x, y = plot_lat_lon(
        moloks[0][0], moloks[0][1], min_lat, max_lat, min_lon, max_lon, width, height
    )
    draw.circle((x, y), 20, fill=(255, 255, 255))
    img.save("test.png")

    """

    depot =moloks[0]
    depot_lat = depot["lat"] 
    depot_lon = depot["lon"] 

    points = []

    for idx,mol in enumerate(moloks):
        lat = mol["lat"]
        lon = mol["lon"]

        """
    # deg = calc_angle(depot_lat,depot_lon,lat,lon)
    # dist = distance_lat_long(depot_lat,depot_lon,lat,lon)
    """
        deg = atan2(abs(lon - depot_lon),abs( lat - depot_lat))
        deg = deg * 180/pi
        deg = (deg + 360) %360 
        dist = ((lon - depot_lon)**2 +(lat - depot_lat) ** 2)**0.5

        points.append((idx,dist,deg))

    points.sort(key=lambda x:x[1])

    d = 1 
    advancing_font = []

    clusters_id = [i for i in range(len(moloks))]
    uf = UnionFind(len(moloks))

    for (point,dist,deg) in points[1:]:
        s_1 = dist
        s_2 = dist - d

    """
    """
        new_front = []
        for (p1,d1,a1) in advancing_font:
            if d1 >= s_2:
                new_front.append((p1,d1,a1))
        advancing_font = new_front
    """
    """
        if not advancing_font:
            advancing_font.append((point,dist,deg))
            continue
        advancing_font.sort(key=lambda x:x[2])

        angles = [a1 for (_,_,a1) in advancing_font]
        left_i = bisect.bisect_left(angles, deg) - 1
        if left_i < 0:
            left_i = len(advancing_font) - 1  # Wrap around circularly
        right_i = left_i + 1 if left_i + 1 < len(advancing_font) else 0

        x_i = moloks[point]["lat"]
        y_i = moloks[point]["lon"]

        left_point =advancing_font[left_i][0] 

        right_point =advancing_font[right_i][0] 

        l_x_i = moloks[left_point]["lat"]
        l_y_i = moloks[left_point]["lon"]

        r_x_i = moloks[right_point]["lat"]
        r_y_i = moloks[right_point]["lon"]

        #dist_r = ((x_i- r_x_i)**2 + (r_y_i- y_i) ** 2)**0.5
        #dist_l = ((x_i- l_x_i)**2 + (l_y_i- y_i) ** 2)**0.5
        dist_l = distance_lat_long(x_i,y_i,l_x_i,l_y_i)
        dist_r = distance_lat_long(x_i,y_i,r_x_i,r_y_i)

        if dist_r > d and dist_l > d:
            pass
        elif dist_l <= d and dist_r > d:
            uf.union(point,left_point)

        elif dist_l > d and dist_r <= d:
            uf.union(point,right_point)

        elif dist_l <= d and dist_r <= d:
            uf.union(left_point,right_point)
            uf.union(point,left_point)

        advancing_font.append((point,dist,deg))

    for i in range(1,len(moloks)):
        clusters_id[i] = uf.find(i)

    new_clusters = []

    only_one = list(set(clusters_id))
    print(f"clusters: {len(only_one)-1}")

    for i in only_one:
        new_clusters.append([l for l in range(len(clusters_id)) if clusters_id[l] == i])

    for clust in new_clusters:
        print(clust)
        col_r = random.randint(0,255)
        col_g = random.randint(0,255)
        col_b = random.randint(0,255)
        min_x = float("inf")
        max_x= -float("inf")

        min_y = float("inf")
        max_y= -float("inf")
        for point in clust:
            lat = moloks[point]["lat"]
            lon = moloks[point]["lon"]
            x,y = plot_lat_lon(lat,lon,min_lat,max_lat,min_lon,max_lon,width,height)
            min_x = x if x < min_x else min_x
            max_x= x if x > max_x else max_x 

            min_y = y if y < min_y else min_y
            max_y = y if y > max_y else max_y 
            draw.circle((x,y),10,fill=(col_r,col_g,col_b))
        draw.rectangle([(min_x,min_y),(max_x,max_y)],outline=(col_r,col_g,col_b))

    x,y = plot_lat_lon(moloks[0]["lat"],moloks[0]["lon"],min_lat,max_lat,min_lon,max_lon,width,height)
    draw.circle((x,y),20,fill=(255,255,255))
    img.save("test.png")
    """
