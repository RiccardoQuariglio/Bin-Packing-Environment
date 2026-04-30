from abstract_solver import AbstractSolver
from additional_script import AdditionalScript
from item import Item
from container import Container

class solver_340850_335723(AbstractSolver):

    def __init__(self, inst):
        #Inizializzazione delle variabili che andrò a usare nel solver
        super().__init__(inst)
        self.items_list = []
        self.containers_set = set()
        self.additional_script = AdditionalScript()
        self.containers_utilizzati = []
        self.extreme_points = []

    # Metodo solve() costituito da più parti:
    # 1) Memorizzazione degli items e dei containers del dataset in questione in liste
    # 2) Sorting degli items secondo uno specifico criterio

    def solve(self):

        # 1.0) Memorizzazione Items
        self.items_list = self.additional_script.loadItems(self.inst.df_items)
        # 1.1) Memorizzazione Containers
        self.containers_set = self.additional_script.loadContainers(self.inst.df_vehicles)

        # 2) Sorting degli items
        self.items_by_a_h_w = self.additional_script.sortedItemsByAHW(self.items_list)

        # 3) Impaccamento
        #Scelta primo container e aggiunta alla lista di containers utilizzati
        first_container = self.additional_script.chooseFirstContainer(self.containers_set)
        self.containers_utilizzati.append(first_container)

        for item in self.items_list:
            item_to_pack = self.items_list[0]
            bool_placed = False
            containers_feasible = []
            for container in self.containers_utilizzati:
                if self.additional_script.isFeasible(item_to_pack, container):
                    self.additional_script.computeMerit(container)
                    containers_feasible.append(container)

            if containers_feasible:    #"Se lista" <==> "Se la lista non è vuota"
                best_container = self.additional_script.containerBestMerit(containers_feasible)
                self.additional_script.packItemIntoContainer(item_to_pack, best_container)
                bool_placed = True
                item_placed = self.items_list.pop(0)

            if not bool_placed:    #"Se bool_placed == False"
                new_container = self.additional_script.openNewContainer(self.containers_set)
                self.containers_utilizzati.append(new_container)
                if self.additional_script.isFeasible(item_to_pack, new_container):
                    self.additional_script.packItemIntoContainer(item_to_pack, new_container)
                    bool_placed = True
                    item_placed = self.items_list.pop(0)

            if not bool_placed:
                print(f"Il container {item_to_pack.id} non è stato posizionato neanche dopo l'apertura di un nuovo container.")
















        
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

