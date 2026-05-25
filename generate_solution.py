
from instances import Instance
from solver_340850_335723.solver_340850_335723 import solver_340850_335723

DATASET_NAME = 'Dataset0'

inst = Instance(DATASET_NAME)
solver = solver_340850_335723(inst)
solver.solve()