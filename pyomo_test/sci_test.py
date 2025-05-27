from pyscipopt import Model,quicksum,Conshdlr,SCIP_RESULT,SCIP_EVENTTYPE
import json
import networkx as nx

distance_matrix = []
with open("../data/molok_distance_matrix2.json","r") as f:
    distance_matrix = json.load(f)

scip = Model()

scip.hideOutput(False)

#scip.setRealParam('limits/time', 60)  # Set a target gap
scip.setRealParam('limits/gap', 0.01)  # Set a target gap
scip.setIntParam('separating/maxrounds', 10)  # More separation rounds

n = len(distance_matrix)

bin_list = {} 
print("damn")

for i in range(n):
    for j in range(n):
        bin_list[i,j] = scip.addVar(vtype="B",name=f"x_{i}_{j}")

print("damn 1")

scip.setObjective(quicksum(distance_matrix[i][j] * bin_list[i,j] for i in range(n) for j in range(n)),sense="minimize")

print("damn 2")

flow_cons = {}
for j in range(n):
    flow_cons[j] = scip.addCons(quicksum(bin_list[i,j] for i in range(n) if i!= j) == quicksum(bin_list[j,h] for h in range(n) if h != j),name=f"flow: {j}")

print("damn 3")

route_cons= {} 
for i in range(n):
    route_cons[i] = scip.addCons(quicksum(bin_list[i,j] for j in range(n) if i!= j) == 1,name=f"route const:{i}")

print("damn 4")

l_dep_cons= {}

l_dep_cons[0] = scip.addCons(quicksum(bin_list[0,j] for j in range(n) if j!=0) == 1,name=f"l dep con")

print("damn 5")

e_dep_cons= {}

e_dep_cons[0] = scip.addCons(quicksum(bin_list[j,0] for j in range(n) if j!=0) == 1,name=f"e dep con")

print("damn 6")


class SEC(Conshdlr):
    def createCons(self, name, variables):
        model = self.model
        cons = model.createCons(self, name)

        # data relevant for the constraint; in this case we only need to know which
        # variables cannot form a subtour
        cons.data = {}
        cons.data['vars'] = variables
        return cons

    def find_subtours(self, cons, solution = None):
        edges = []
        x = cons.data['vars']

        for [i,j] in list(x.keys()):
                if self.model.getSolVal(solution, x[i,j]) > 0.5:
                    edges.append((i, j))
                    edges.append((j, i))

        G = nx.Graph()
        G.add_edges_from(edges)
        components = list(nx.connected_components(G))

        if len(components) == 1:
            return []
        else:
            return components

    def consenfolp(self, constraints, n_useful_conss, sol_infeasible):
        consadded = False

        for cons in constraints:
            #sol = self.model.getBestSol()
            subtours = self.find_subtours(cons)

            # if there are subtours
            if subtours:
                x = cons.data['vars']

                # add subtour elimination constraint for each subtour
                for S in subtours:
                    self.model.addCons(quicksum(x[i,j] for i in S for j in S if j!=i) <= len(S)-1)
                    consadded = True

        if consadded:
            return {"result": SCIP_RESULT.CONSADDED}
        else:
            return {"result": SCIP_RESULT.FEASIBLE}

    # checks whether solution is feasible
    def conscheck(self, constraints, solution, check_integrality,
                  check_lp_rows, print_reason, completely, **results):

        # check if there is a violated subtour elimination constraint
        for cons in constraints:
            if self.find_subtours(cons, solution):
                return {"result": SCIP_RESULT.INFEASIBLE}

        # no violated constriant found -> feasible
        return {"result": SCIP_RESULT.FEASIBLE}

    def conslock(self, constraint, locktype, nlockspos, nlocksneg):
        pass
# create the constraint handler
conshdlr = SEC()

# Add the constraint handler to SCIP. We set check priority < 0 so that only integer feasible solutions
# are passed to the conscheck callback
scip.includeConshdlr(conshdlr, "TSP", "TSP subtour eliminator", chckpriority = -10, enfopriority = -10)

# create a subtour elimination constraint
cons = conshdlr.createCons("no_subtour_cons", bin_list)

# add constraint to SCIP
scip.addPyCons(cons)
def print_obj_value(model, event):
    print("New best solution found with objective value: {}".format(model.getObjVal()))
scip.attachEventHandlerCallback(print_obj_value, [SCIP_EVENTTYPE.BESTSOLFOUND])
scip.optimize()
solve_time = scip.getSolvingTime()
num_nodes = scip.getNTotalNodes() # Note that getNNodes() is only the number of nodes for the current run (resets at restart)
obj_val = scip.getObjVal()
print(obj_val)

current_idx = 0
routes = [current_idx]
do_once = False
while current_idx != 0 or not do_once:
    do_once = True
    for i in range(n):
        if i == current_idx:
            continue
        val = bin_list[current_idx,i]
        if scip.getVal(val) == 1:
            current_idx = i
            routes.append(current_idx)
            break
print(routes)



