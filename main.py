from instances import Instance
from solver_XXXXXX_YYYYYY import solver_XXXXXX_YYYYYY

if __name__ == '__main__':

    dataset_name = 'DatasetA'

    inst = Instance(dataset_name)

    solver = solver_XXXXXX_YYYYYY(inst)

    solver.solve()