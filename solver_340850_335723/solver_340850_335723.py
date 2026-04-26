from abstract_solver import AbstractSolver
from additional_script import AdditionalScript
from item import Item
from container import Container

class solver_340850_335723(AbstractSolver):

    def __init__(self, inst):
        #Inizializzazione delle variabili che andrò a usare nel solver
        super().__init__(inst)
        self.items = []
        self.containers = []
        self.additional_script = AdditionalScript()

    # Metodo solve() costituito da più parti:
    # 1) Memorizzazione degli items e dei containers del dataset in questione in liste
    # 2) Sorting degli items secondo uno specifico criterio

    def solve(self):

        # 1.0) Memorizzazione Items
        self.items = self.additional_script._load_items(self.inst.df_items)
        # 1.1) Memorizzazione Containers
        self.containers = self.additional_script._load_containers(self.inst.df_vehicles)

        # 2) Sorting degli items
        self.items_by_h_a_w = self.additional_script._sorted_items_h_a_w(self.items)
        self.items_by_volume_decreasing = self.additional_script._sort_items_by_volume_decreasing(self.items)


        
        self.write_solution_to_file()



#test per vedere se il sorting funziona
"""
if __name__ == "__main__":
    #Non cambiare
    from instances import Instance
    import os
    import sys

    os.chdir(os.path.dirname(os.getcwd()))
    sys.path.append(os.getcwd())
    #fino a qua
    dataset_name = 'Dataset0'    #qua puoi cambiare il dataset
    

    try:
        #Non cambiare
        inst = Instance(dataset_name)
        my_solver = solver_340850_335723(inst)
        #fino a qua

        print(f"--- Test Sorting {dataset_name} ---")
        my_solver.solve()
        print(f"--- Lista sortata per h,a,w decrescente ---")
        print(my_solver.sorted_items_h_a_w(my_solver.items))

        print(f"--- Lista sortata per volume decrescente ---")
        for item in my_solver.items_by_volume_decreasing:
            print(f"Item: {item.id}, Volume: {item.width * item.depth * item.height}")


    except Exception as e:
        print(f"Errore durante il test: {e}")
"""
"""
if __name__ == "__main__":
    #Non cambiare
    from instances import Instance
    import os
    import sys

    os.chdir(os.path.dirname(os.getcwd()))
    sys.path.append(os.getcwd())
    #fino a qua
    dataset_name = 'Dataset0'    #qua puoi cambiare il dataset
    

    try:
        #Non cambiare
        inst = Instance(dataset_name)
        my_solver = solver_340850_335723(inst)
        #fino a qua

        print(f"--- Test Sorting {dataset_name} ---")
        my_solver.solve()
        print(f"--- Lista sortata per h,a,w decrescente ---")
        for item in my_solver.items_by_h_a_w:
            print(f"ID: {item.id} | H: {item.curr_height}, A: {item.curr_depth*item.curr_width}, W: {item.weight}")
    except Exception as e:
        print(f"Errore durante il test: {e}")
        """

