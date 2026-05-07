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

    """
    # Metodo solve() costituito da più parti:
    # 1) Memorizzazione degli items e dei containers del dataset in questione in liste
    # 2) Sorting degli items secondo uno specifico criterio
    # 3) Scelta del primo container: da qui in avanti c'è il vero impaccamento
    # 4) Calcolo soluzioni fattibili per ogni container, ciclando sui containers
    # 5.0 - 5.1) Si sceglie la soluzione migliore (se non ce n'erano, si apre un nuovo container e si piazza là)
    #            e si impacca finalmente l'item, andando ad aggiornare lista_items, container coinvolto.
    """


    def solve(self):

        # 1.0) Memorizzazione Items
        self.items_list = self.additional_script.loadItems(self.inst.df_items)
        # 1.1) Memorizzazione Containers
        self.containers_set = self.additional_script.loadContainers(self.inst.df_vehicles)
        print(f"Items memorizzati correttamente ({len(self.items_list)} items in totale);\n"
              f"containers memorizzati correttamente ({len(self.containers_set)} containers in totale);\n"
              f"Primo item della lista:\n"
              f"width, depth, height: {self.items_list[0].width}, {self.items_list[0].depth}, {self.items_list[0].height}\n"
              f"curr_width, curr_depth, curr_heigth: {self.items_list[0].curr_width}, {self.items_list[0].curr_depth}, {self.items_list[0].curr_height}\n"
              f"============================================================\n")

        # 2) Sorting degli items
        #self.items_by_a_h_w = self.additional_script.sortedItemsByAHW(self.items_list)

        # 3) Scelta primo container e aggiunta alla lista di containers utilizzati
        first_container = self.additional_script.chooseFirstContainer(self.containers_set)
        first_container.idx = self.idx_vehicle
        self.idx_vehicle += 1
        self.containers_utilizzati.append(first_container)
        print(f"Primo containers scelto correttamente (idx: {first_container.idx})\n"
              f"===================================================\n")


        #4) Per ogni container, vedere se ci sono soluzioni fattibili, e aggiungerli alla lista totale (delle soluz fattibili)
        while self.items_list:
            item_to_pack = self.items_list[0]
            bool_placed = False
            all_feasible_solutions = []
            for container in self.containers_utilizzati:   #Sicuramente non è vuoto
                container_feasible_solutions = self.additional_script.isFeasible(item_to_pack, container)
                if container_feasible_solutions:
                    all_feasible_solutions.extend(container_feasible_solutions)

            # 5.0) Se ci sono soluzioni fattibili, trovare la migliore con la funzione di merito
            #      e impaccare l'item nel container
            if all_feasible_solutions:    #"Se lista" <==> "Se la lista non è vuota"
                bool_placed = True
                best_solution = max(all_feasible_solutions,  key=lambda x: x.merit)
                best_solution.item.x_position = best_solution.ep[0]
                best_solution.item.y_position = best_solution.ep[1]
                best_solution.item.z_position = best_solution.ep[2]
                self.additional_script.packItemIntoContainer(best_solution)
                item_placed = self.items_list.pop(0)

                #Aggiornamento self.sol (per far funzionare il checker)
                self.sol['type_vehicle'].append(best_solution.container.type)
                self.sol['idx_vehicle'].append(best_solution.container.idx)
                self.sol['id_item'].append(best_solution.item.id)
                self.sol['x_origin'].append(best_solution.ep[0])
                self.sol['y_origin'].append(best_solution.ep[1])
                self.sol['z_origin'].append(best_solution.ep[2])
                # Per ora mettiamo 0 come orientamento di default se non lo hai salvato
                self.sol['orient'].append(best_solution.item_rotation)

                print(f"L'item {best_solution.item.id} è stato posizionato nel container "
                      f"{best_solution.container.idx} in posizione {best_solution.ep}.\n")


            # 5.1) Se non c'è nessuna soluzione fattibile per nessun container, se ne apre uno nuovo e lo si
            #      impacca là
            if not bool_placed:    #"Se bool_placed == False"
                new_container = self.additional_script.openNewContainer(self.containers_set)
                print(f"E' stato aperto un nuovo container con idx: {new_container.idx}")
                new_container.idx = self.idx_vehicle
                self.idx_vehicle += 1
                self.containers_utilizzati.append(new_container)
                feasible_solutions = self.additional_script.isFeasible(item_to_pack, new_container)
                if feasible_solutions is not None:
                    best_solution = max(feasible_solutions, key=lambda x: x.merit)
                    best_solution.item.x_position = best_solution.ep[0]
                    best_solution.item.y_position = best_solution.ep[1]
                    best_solution.item.z_position = best_solution.ep[2]
                    self.additional_script.packItemIntoContainer(best_solution)
                    bool_placed = True
                    item_placed = self.items_list.pop(0)
                    # Aggiornamento self.sol (per far funzionare il checker)
                    self.sol['type_vehicle'].append(best_solution.container.type)
                    self.sol['idx_vehicle'].append(best_solution.container.idx)
                    self.sol['id_item'].append(best_solution.item.id)
                    self.sol['x_origin'].append(best_solution.ep[0])
                    self.sol['y_origin'].append(best_solution.ep[1])
                    self.sol['z_origin'].append(best_solution.ep[2])
                    # Per ora mettiamo 0 come orientamento di default se non lo hai salvato
                    self.sol['orient'].append(best_solution.item_rotation)

                    print(f"L'item {best_solution.item.id} è stato posizionato nel container "
                          f"{best_solution.container.idx} in posizione {best_solution.ep}.\n")

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

    except Exception as e:
        print(f"Errore durante il test: {e}")


