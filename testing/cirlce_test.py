import numpy as np
import pulp

def optimize_circle_radii(points):
    n = len(points)
    distances = np.zeros((n, n))
    
    # Compute pairwise distances
    for i in range(n):
        for j in range(n):
            if i != j:
                distances[i, j] = np.linalg.norm(np.array(points[i]) - np.array(points[j]))
    
    # --- STEP 1: Maximize the minimum radius (t) ---
    prob_t = pulp.LpProblem("Maximize_Min_Radius", pulp.LpMaximize)
    r = [pulp.LpVariable(f"r_{i}", lowBound=0) for i in range(n)]
    t = pulp.LpVariable("t", lowBound=0)
    prob_t += t  # Objective: Maximize t
    
    # Constraints
    for i in range(n):
        prob_t += r[i] >= t  # All radii >= t
    for i in range(n):
        for j in range(i + 1, n):
            prob_t += r[i] + r[j] <= distances[i, j]  # No overlap
    
    prob_t.solve()
    if prob_t.status != pulp.LpStatusOptimal:
        raise ValueError("Step 1 failed.")
    
    t_opt = pulp.value(t)
    print(f"Maximized minimum radius (t): {t_opt}")

    # --- STEP 2: Fix t and maximize sum(r_i) for larger radii ---
    prob_sum = pulp.LpProblem("Maximize_Sum_Radii", pulp.LpMaximize)
    r = [pulp.LpVariable(f"r_{i}", lowBound=t_opt) for i in range(n)]  # Enforce r_i >= t_opt
    prob_sum += pulp.lpSum(r)  # Objective: Maximize sum(r_i)
    
    # Constraints (no overlap)
    for i in range(n):
        for j in range(i + 1, n):
            prob_sum += r[i] + r[j] <= distances[i, j]
    
    prob_sum.solve()
    if prob_sum.status != pulp.LpStatusOptimal:
        raise ValueError("Step 2 failed.")
    
    radii = [pulp.value(var) for var in r]
    return radii

points = [
    [0, 1],    # Point A
    [3, 3],    # Point A
    [-4, 1],    # Point A
    [2, -1]    # Point A
]

radii = optimize_circle_radii(points)
for i, (point, radius) in enumerate(zip(points, radii)):
    print(f"Point {i+1} at {point}: radius = {radius:.2f}")
