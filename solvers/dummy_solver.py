from solvers.abstract_solver import AbstractSolver

class DummySolver(AbstractSolver):

    def __init__(self, inst):
        super().__init__(inst)
        self.name = 'DummySolver'

    def solve(self):
        for idx, row in self.inst.df_items.iterrows():
            self.sol['type_vehicle'].append(0)
            self.sol['idx_vehicle'].append(self.idx_vehicle)
            self.sol['id_item'].append(idx)
            self.sol['x_origin'].append(0)
            self.sol['y_origin'].append(0)
            self.sol['z_origin'].append(0)
            self.sol['orient'].append(row.allowedRotations[0])
            self.idx_vehicle += 1