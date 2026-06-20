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
        self.containers_lista = []
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
        self.containers_lista = self.additional_script.loadContainers(self.inst.df_vehicles)

        # 2) Sorting degli items (copia ordinata, la lista originale rimane invariata se serve altrove)
        self.items_list = self.additional_script.sortedItemsByAHW(self.items_list)

        # Statistiche medie degli item: servono a chooseContainer per stimare
        # quanti item entreranno in ciascun container (vincoli volume/peso/valore)
        n_items = len(self.items_list)
        volume_residuo = sum(item.volume for item in self.items_list)
        peso_residuo = sum(item.weight for item in self.items_list)
        valore_residuo = sum(item.value for item in self.items_list)
        # Soglia endgame (L3): volume del container più piccolo disponibile
        volume_soglia = min(c.volume for c in self.containers_lista)

        # 3) Scelta primo container (in base al primo item da piazzare) e aggiunta alla lista di containers utilizzati
        if self.items_list:
            vol_medio = volume_residuo / n_items
            peso_medio = peso_residuo / n_items
            valore_medio = valore_residuo / n_items
            candidates = self.additional_script.chooseContainer(
                self.items_list[0], self.containers_lista, vol_medio, peso_medio, valore_medio)
            if candidates:
                first_container = candidates[0]
                first_container.idx = self.idx_vehicle
                self.idx_vehicle += 1
                self.containers_utilizzati.append(first_container)

        #4) Per ogni container, vedere se ci sono soluzioni fattibili, e aggiungerli alla lista totale (delle soluz fattibili)
        while self.items_list:
            item_to_pack = self.items_list[0]
            bool_placed = False
            all_feasible_solutions = []
            for container in self.containers_utilizzati:
                container_feasible_solutions = self.additional_script.isFeasible(item_to_pack, container)
                if container_feasible_solutions:
                    all_feasible_solutions.extend(container_feasible_solutions)

            # 5.0) Se ci sono soluzioni fattibili, trovare la migliore con la funzione di merito
            #      e impaccare l'item nel container
            if all_feasible_solutions:
                bool_placed = True
                best_solution = max(all_feasible_solutions,  key=lambda x: x.merit)
                self.additional_script.packItemIntoContainer(best_solution)
                self.items_list.pop(0)
                volume_residuo -= best_solution.item.volume
                peso_residuo -= best_solution.item.weight
                valore_residuo -= best_solution.item.value

                self.sol['type_vehicle'].append(best_solution.container.type)
                self.sol['idx_vehicle'].append(best_solution.container.idx)
                self.sol['id_item'].append(best_solution.item.id)
                self.sol['x_origin'].append(best_solution.ep[0])
                self.sol['y_origin'].append(best_solution.ep[1])
                self.sol['z_origin'].append(best_solution.ep[2])
                self.sol['orient'].append(best_solution.item_rotation)

            # 5.1) Se non c'è nessuna soluzione fattibile per nessun container, se ne apre uno nuovo.
            #      Si provano tutti i tipi di container candidati (dal migliore al peggiore)
            #      finché si trova uno in cui l'item entra effettivamente.
            #      Endgame (L3): se il volume residuo è piccolo, si usa chooseLastContainer
            #      che predilige container economici.
            if not bool_placed:
                if volume_residuo <= volume_soglia:
                    candidates = self.additional_script.chooseLastContainer(item_to_pack, self.containers_lista)
                else:
                    n_rimanenti = len(self.items_list)
                    vol_medio = volume_residuo / n_rimanenti
                    peso_medio = peso_residuo / n_rimanenti
                    valore_medio = valore_residuo / n_rimanenti
                    candidates = self.additional_script.chooseContainer(
                        item_to_pack, self.containers_lista, vol_medio, peso_medio, valore_medio)
                for new_container in candidates:
                    new_container.idx = self.idx_vehicle
                    self.idx_vehicle += 1
                    self.containers_utilizzati.append(new_container)
                    feasible_solutions = self.additional_script.isFeasible(item_to_pack, new_container)
                    if feasible_solutions is not None:
                        best_solution = max(feasible_solutions, key=lambda x: x.merit)
                        self.additional_script.packItemIntoContainer(best_solution)
                        bool_placed = True
                        self.items_list.pop(0)
                        volume_residuo -= best_solution.item.volume
                        peso_residuo -= best_solution.item.weight
                        valore_residuo -= best_solution.item.value
                        self.sol['type_vehicle'].append(best_solution.container.type)
                        self.sol['idx_vehicle'].append(best_solution.container.idx)
                        self.sol['id_item'].append(best_solution.item.id)
                        self.sol['x_origin'].append(best_solution.ep[0])
                        self.sol['y_origin'].append(best_solution.ep[1])
                        self.sol['z_origin'].append(best_solution.ep[2])
                        self.sol['orient'].append(best_solution.item_rotation)
                        break
                    else:
                        self.containers_utilizzati.pop()
                        self.idx_vehicle -= 1

            if not bool_placed:
                # Per evitare loop infinito, rimuoviamo comunque l'item dalla lista,
                # registrando che non è stato possibile piazzarlo (la soluzione sarà infeasible per items mancanti,
                # ma il solver termina invece di bloccarsi).
                print(f"WARNING: l'item {item_to_pack.id} non è stato posizionato neanche dopo l'apertura di un nuovo container.")
                self.items_list.pop(0)

        self.write_solution_to_file()
