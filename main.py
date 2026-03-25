from instances import Instance
from solvers import DummySolver

if __name__ == '__main__':
    dataset_name = 'DatasetA'
    inst = Instance(dataset_name)
    #inst.transform()
    solver = DummySolver(inst)

    t = solver.solve()
    solver.write_solution_to_file()