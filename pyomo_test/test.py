import json
import pyomo.environ as pyo



distance_matrix = []
with open("../data/molok_distance_matrix2 - Copy.json","r") as f:
    distance_matrix = json.load(f)


model = pyo.ConcreteModel() 
solver = pyo.SolverFactory("scip")
solver.options = { 'limits/time':600  } 

model.N = pyo.RangeSet(0,len(distance_matrix)-1)

def ini(model,i,j):
    return distance_matrix[i][j]

model.d = pyo.Param(model.N,model.N,initialize=ini) 

model.x = pyo.Var(model.N,model.N,within=pyo.Binary)
model.u = pyo.Var(model.N,within=pyo.NonNegativeReals)

def objective_rule(model):
    return sum(model.d[i,j] * model.x[i,j] for i in model.N for j in model.N if i != j)

model.my_objective = pyo.Objective(rule=objective_rule,sense=pyo.minimize)

def customer_visit_rule(model,j):
    if j == 0:
        return pyo.Constraint.Skip
    return sum(model.x[i,j] for i in model.N if i != j) == 1

model.customer_visit = pyo.Constraint(model.N,rule=customer_visit_rule)

def exit_depot_rule(model):
    return sum(model.x[0,j] for j in model.N if j != 0) == 1
model_depot_exit = pyo.Constraint(rule=exit_depot_rule)

def enter_depot_rule(model):
    return sum(model.x[j,0] for j in model.N if j != 0) == 1
model_depot_enter = pyo.Constraint(rule=enter_depot_rule)

def flow_rule(model,h):
    if h== 0:
        return pyo.Constraint.Skip
    return sum(model.x[i,h] for i in model.N if i != h) == sum(model.x[h,j] for j in model.N if j != h)
model.flow = pyo.Constraint(model.N,rule=flow_rule)

def subtor_rule(model,i,j):
    if j == 0 or i == 0 or j== i:
        return pyo.Constraint.Skip
    return model.u[i] +1 <= model.u[j] + len(distance_matrix)*(1-model.x[i,j])
model.subtor = pyo.Constraint(model.N,model.N,rule=subtor_rule)

print("Starting solve")
results = solver.solve(model,tee=True)

print(f"Objective value: {model.my_objective()}")
