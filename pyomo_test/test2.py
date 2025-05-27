# OptFrame Python Demo TSP - Traveling Salesman Problem

from typing import List
import random

from optframe import *
from optframe.protocols import *

import json
distance_matrix = []
with open("../data/molok_distance_matrix2.json","r") as f:
    distance_matrix =json.load(f) 

class SolutionTSP(object):
    def __init__(self):
        # number of cities in solution
        self.n : int = 0
        # visited cities as a list
        self.cities : List[int] = []

    # MUST provide some printing mechanism
    def __str__(self):
        return f"SolutionTSP(n={self.n};cities={self.cities})"
    
class ProblemContextTSP(object):
    def __init__(self):
        # float engine for OptFrame
        self.engine = Engine(APILevel.API1d)
        # number of cities
        self.n = 0
        # distance matrix
        self.dist = []
        
   # Example: "3\n1 10 10\n2 20 20\n3 30 30\n"

    def load(self, distance_matrix:list[list[float]]):
        self.n = len(distance_matrix)
        self.dist = distance_matrix

    def __str__(self):
        return f"SUI"
# continuation of ProblemContextTSP class...
    @staticmethod
    def minimize(pTSP: 'ProblemContextTSP', s: SolutionTSP) -> float:
        assert (s.n == pTSP.n)
        assert (len(s.cities) == s.n)
        # remember this is an API1d method
        f = 0.0
        for i in range(pTSP.n-1):
          f += pTSP.dist[s.cities[i]][s.cities[i + 1]];
        f += pTSP.dist[s.cities[int(pTSP.n) - 1]][s.cities[0]];
        return f
# continuation of ProblemContextTSP class...
    @staticmethod
    def generateSolution(problemCtx: 'ProblemContextTSP') -> SolutionTSP:
        sol = SolutionTSP()
        customers = []
        for i in range(1,problemCtx.n):
            customers.append(i)
        random.shuffle(customers)
        customers.insert(0,0)
        customers.append(0)
        sol.cities = customers
        sol.n = problemCtx.n
        return sol

# optional tests...
assert isinstance(SolutionTSP, XSolution)            # composition tests 
assert isinstance(ProblemContextTSP,  XProblem)      # composition tests 
assert isinstance(ProblemContextTSP,  XConstructive) # composition tests    
assert isinstance(ProblemContextTSP,  XMinimize)     # composition tests

from optframe.components import Move

class MoveSwapClass(Move):
    def __init__(self, _i: int = 0, _j: int = 0):
        self.i = _i
        self.j = _j
    def __str__(self):
        return "MoveSwapClass(i="+str(self.i)+";j="+str(self.j)+")"
    def apply(self, problemCtx, sol: SolutionTSP) -> 'MoveSwapClass':
        aux = sol.cities[self.j]
        sol.cities[self.j] = sol.cities[self.i]
        sol.cities[self.i] = aux
        # must create reverse move (j,i)
        return MoveSwapClass(self.j, self.i)
    def canBeApplied(self, problemCtx, sol: SolutionTSP) -> bool:
        return True
    def eq(self, problemCtx, m2: 'MoveSwapClass') -> bool:
        return (self.i == m2.i) and (self.j == m2.j)

assert isinstance(MoveSwapClass, XMove)       # composition tests
assert MoveSwapClass in Move.__subclasses__() # classmethod style

#from optframe.components import NS

class NSSwap(object):
    @staticmethod
    def randomMove(pTSP, sol: SolutionTSP) -> MoveSwapClass:
        import random
        n = sol.n
        i = random.randint(0, n - 1)
        j = i
        while  j <= i:
            i = random.randint(0, n - 1)
            j = random.randint(0, n - 1)
        # return MoveSwap(i, j)
        return MoveSwapClass(i, j)
    
#assert NSSwap in NS.__subclasses__()   # optional test

#from optframe.components import NSSeq
from optframe.components import NSIterator

# For NSSeq, one must provide a Move Iterator
# A Move Iterator has five actions: Init, First, Next, IsDone and Current

class IteratorSwap(NSIterator):
    def __init__(self, _i: int, _j: int):
        self.i = _i
        self.j = _j
    def first(self, pTSP: ProblemContextTSP):
        self.i = 0
        self.j = 1
    def next(self, pTSP: ProblemContextTSP):
        if self.j < pTSP.n - 1:
            self.j = self.j+1
        else:
            self.i = self.i + 1
            self.j = self.i + 1
    def isDone(self, pTSP: ProblemContextTSP):
        return self.i >= pTSP.n - 1
    def current(self, pTSP: ProblemContextTSP):
        return MoveSwapClass(self.i, self.j)
    
assert IteratorSwap in NSIterator.__subclasses__()   # optional test
    
class NSSeqSwap(object):
    @staticmethod
    def randomMove(pTSP: ProblemContextTSP, sol: SolutionTSP) -> MoveSwapClass:
        return NSSwap.randomMove(pTSP, sol)  # composition
    
    @staticmethod
    def getIterator(pTSP: ProblemContextTSP, sol: SolutionTSP) -> IteratorSwap:
        return IteratorSwap(-1, -1)

#assert NSSeqSwap in NSSeq.__subclasses__()   # optional test
# ===========================================
# begins main() python script for TSP ILS/VNS
# ===========================================

# import ILSLevels and BestImprovement
from optframe.heuristics import *

# set random seed for system
random.seed(0) # bad generator, just an example..

# loads problem from filesystem
pTSP = ProblemContextTSP()
pTSP.load(distance_matrix)
print(pTSP)

# Register Basic Components
comp_list = pTSP.engine.setup(pTSP)
print(comp_list)

# get index of new NS
ns_idx = pTSP.engine.add_ns_class(pTSP, NSSwap)
print("ns_idx=", ns_idx)

# get index of new NSSeq
nsseq_idx = pTSP.engine.add_nsseq_class(pTSP, NSSeqSwap)
print("nsseq_idx=", nsseq_idx)

# ========= play a little bit =========

gev_idx = comp_list[0] # GeneralEvaluator
ev_idx  = comp_list[1] # Evaluator
print("evaluator id:", ev_idx)

c_idx = comp_list[2]
print("c_idx=", c_idx)

is_idx = IdInitialSearch(0)
print("is_idx=", is_idx)

# test each component

fev = pTSP.engine.get_evaluator(ev_idx)
pTSP.engine.print_component(fev)

fc = pTSP.engine.get_constructive(c_idx)
pTSP.engine.print_component(fc)

solxx = pTSP.engine.fconstructive_gensolution(fc)
print("test solution:", solxx)

z1 = pTSP.engine.fevaluator_evaluate(fev, True, solxx)
print("test evaluation:", z1)

# some basic tests with moves and iterator
move = MoveSwapClass(0,1) # swap 0 with 1
print("move=",move)
m1 = NSSwap.randomMove(pTSP, solxx)
print(m1)

print("begin test with iterator")
it = NSSeqSwap.getIterator(pTSP, solxx)
it.first(pTSP)
while not it.isDone(pTSP):
    m = it.current(pTSP)
    print(m)
    it.next(pTSP)
print("end test with iterator")

# ======== end playing ========

# pack NS into a NS list
list_idx = pTSP.engine.create_component_list(
    "[ OptFrame:NS 0 ]", "OptFrame:NS[]")
print("list_idx=", list_idx)

# print("Listing registered components:")
# pTSP.engine.list_components("OptFrame:")

# list the required parameters for OptFrame ComponentBuilder
# print("engine will list builders for OptFrame: ")
# print(pTSP.engine.list_builders("OptFrame:"))
# print()

# make next local search component silent (loglevel 0)
pTSP.engine.experimental_set_parameter("COMPONENT_LOG_LEVEL", "0")

print("building 'BI' neighborhood exploration as local search", flush=True)
bi = BestImprovement(pTSP.engine, 0, 0)
ls_idx = bi.get_id()
print("ls_idx=", ls_idx, flush=True)

print("creating local search list", flush=True)
list_vnd_idx = pTSP.engine.create_component_list(
    "[ OptFrame:LocalSearch 0 ]", "OptFrame:LocalSearch[]")
print("list_vnd_idx=", list_vnd_idx)


print("building 'VND' local search")
vnd = VariableNeighborhoodDescent(pTSP.engine, 0, 0)
vnd_idx = vnd.get_id()
print("vnd_idx=", vnd_idx)


#####
#pTSP.engine.list_components("OptFrame:")

ilsl_pert = ILSLevelPertLPlus2(pTSP.engine, 0, 0)
pert_idx = ilsl_pert.get_id()
print("pert_idx=", pert_idx)

# pTSP.engine.list_components("OptFrame:")

# make next global search component info (loglevel 3)
pTSP.engine.experimental_set_parameter("COMPONENT_LOG_LEVEL", "3")

# build Iterated Local Search (ILS) Levels with iterMax=10 maxPert=5
ilsl = ILSLevels(pTSP.engine, 0, 0, 1, 0, 10, 5)
print("will start ILS for 3 seconds")
lout = ilsl.search(3.0)
print("Best solution: ",   lout.best_s)
print("Best evaluation: ", lout.best_e)

print("FINISHED")
