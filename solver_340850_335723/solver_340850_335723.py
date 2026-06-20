try:
    from .abstract_solver import AbstractSolver
    from .additional_script import AdditionalScript
    from .item import Item
    from .container import Container
except ImportError:
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
        

        # 2) Sorting degli items (copia ordinata, la lista originale rimane invariata se serve altrove)
        self.items_list = self.additional_script.sortedItemsByAHW(self.items_list)

        # 3) Scelta primo container e aggiunta alla lista di containers utilizzati
        first_container = self.additional_script.chooseFirstContainer(self.containers_set)
        first_container.idx = self.idx_vehicle
        self.idx_vehicle += 1
        self.containers_utilizzati.append(first_container)
        


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

                


            # 5.1) Se non c'è nessuna soluzione fattibile per nessun container, se ne apre uno nuovo e lo si
            #      impacca là
            if not bool_placed:    #"Se bool_placed == False"
                new_container = self.additional_script.openNewContainer(self.containers_set)
                
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

                    

            if not bool_placed:
                # Per evitare loop infinito, rimuoviamo comunque l'item dalla lista,
                # registrando che non è stato possibile piazzarlo (la soluzione sarà infeasible per items mancanti,
                # ma il solver termina invece di bloccarsi).
                print(f"WARNING: l'item {item_to_pack.id} non è stato posizionato neanche dopo l'apertura di un nuovo container.")
                self.items_list.pop(0)


        
        self.write_solution_to_file()

