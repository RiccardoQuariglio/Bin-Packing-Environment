from item import Item
from container import Container
import random
from singleSolutionFeasible import SingleSolutionFeasible

"""
    1) Ordine delle funzioni nel file additional_script:
    2) loadItems(df_items) --> memorizza gli items in una lista non ordinata
    3) loadContainers(df_vehicles) --> memorizza i containers in una lista non ordinata
    4) sortedItemsByAHW(items) --> ordina gli items di una lista per area e altezza decrescente
    5) stochasticSortedItems(items, randomness=0.4) --> ordina gli items di una lista con fattore di randomicità    
    6) chooseFirstContainer(set_containers: set[Container]) --> Sceglie il miglior container da cui iniziare, dato un insieme iniziale
    7) isFeasible(item_to_pack: Item, container: Container) -->
    verifica che un item possa essere impaccato in un container. Verifica, in ordine, 
    - che peso e valore dell'oggetto non superino il limite massimo del container
    Per ogni Extreme Point del container poi verifica che:
     - non superi il volume del container stesso
     - non si sovrapponga a nessun oggetto già presente all'interno del container
     - rispetti i vincoli di superficie
    Se tutti questi requisiti vengono soddisfatti, memorizza un oggetto SingleSolutionFeasible in una lista,
    che restituisce poi alla fine. (Nota: gli oggetti restituiti hanno come attributi l'item, il container, l'ep,
    le dimensioni dell'oggetto e IL VALORE DEL MERITO associato a questa soluzione).
    8) packItemIntoContainer(best_solution) -->
    9) openNewContainer(set_containers) --> si occupa di aprire un nuovo container (scegliendone uno da un insieme) 
       qualora un oggetto non possa essere impaccato in nessuno dei containers precedenti
     
    
    """

class AdditionalScript:
    def doNothing(self):
        pass

    @staticmethod
    def loadItems(df_items):
        items_list = []
        for idx, row in df_items.iterrows():
            new_item = Item(
                item_id=idx,
                width=row['width'],
                depth=row['depth'],
                height=row['height'],
                weight=row['weight'],
                value=row['value'],
                allowed_rotations=row['allowedRotations']
            )
            items_list.append(new_item)
        return items_list

    @staticmethod
    def loadContainers(df_vehicles):
        containers_set = set()
        for idx, row in df_vehicles.iterrows():
            # Creiamo dei "template" di veicoli
            new_container = Container(
                type_name=idx,
                width=row['width'],
                depth=row['depth'],
                height=row['height'],
                max_weight=row['maxWeight'],
                cost=row['cost'],
                max_value=row['maxValue'],
                gravity=row['gravityStrength']
            )
            containers_set.add(new_container)
        return containers_set

    #Esempi di sorting

    @staticmethod
    def sortedItemsByAHW(items):
    #Ordina gli oggetti basandosi sulle loro dimensioni massime potenziali
        sorted_list=[]
        def get_best_metrics(item):
            max_h = 0
            max_area = 0
            
            for rot_idx in item.allowed_rotations:
                item.set_rotation(rot_idx)
                max_area = max(max_area, item.curr_width * item.curr_depth)
                max_h = max(max_h, item.curr_height)
                
            return max_area, max_h, item.weight

        sorted_list = sorted(
            items,
            key= get_best_metrics,
            reverse=True)
        return sorted_list

    @staticmethod
    def stochasticSortedItems(items, randomness=0.4):
        #Ordina gli item per altezza decrescente con un fattore di disturbo casuale.
        heights = [item.height for item in items]
        max_h = max(heights)
        min_h = min(heights)
        h_range = max_h - min_h

        scored_items = []
        for item in items:
            noise = random.uniform(-randomness, randomness) * h_range
            score = item.height + noise
            scored_items.append((item, score))

        scored_items.sort(key=lambda x: x[1], reverse=True)
        return scored_items

    @staticmethod
    def chooseFirstContainer(set_containers: set[Container]):
        best_container = max(set_containers, key=lambda x: x.volume/x.cost)
        return best_container



    @staticmethod
    def isFeasible(item_to_pack: Item, container: Container):
        #Verifica peso e valore item
        if item_to_pack.weight > container.remaining_weight and item_to_pack.value > container.remaining_value:
            return None

        feasible_solutions = []
        for ep in container.extreme_points:
            (ex, ey, ez) = ep
            (item_to_pack.x_position, item_to_pack.y_position, item_to_pack.z_position) = (ex, ey, ez)

            #Verifica limiti container
            if (ex + item_to_pack.curr_width <= container.width and
                ey + item_to_pack.curr_depth <= container.depth and
                    ez + item_to_pack.curr_height <= container.height):

                #Verifica sovrapposizioni con altri oggetti nel container
                overlapping = False
                for box_placed in container.items_placed:
                    if item_to_pack.boxes_overlap(box_placed):
                        overlapping = True
                        break

                #Se non c'è sovrapposizione per quell'ep, verifica il Gravity Strength e, se superato anch'esso,
                #generea l'oggetto Feasible Solution
                if not overlapping:
                    if ez == 0:
                        # Se tocca il pavimento, è sempre fattibile
                        feasible_solution = SingleSolutionFeasible(
                            container,
                            item_to_pack,
                            item_to_pack.curr_width,
                            item_to_pack.curr_depth,
                            item_to_pack.curr_height,
                            ep)
                        feasible_solution.computeMerit()
                        feasible_solutions.append(feasible_solution)
                    else:
                        current_support_area = 0
                        min_support_area = item_to_pack.curr_width * item_to_pack.curr_depth * (container.gravity_strength/100)
                        for box_placed in container.items_placed:
                            current_support_area += item_to_pack.get_support_area(box_placed)

                        if current_support_area >= min_support_area:
                            feasible_solution = SingleSolutionFeasible(
                                container,
                                item_to_pack,
                                item_width=item_to_pack.curr_width,
                                item_depth=item_to_pack.curr_depth,
                                item_height=item_to_pack.curr_height,
                                ep=ep)
                            feasible_solution.computeMerit()
                            feasible_solutions.append(feasible_solution)

        #Alla fine vede: se non c'è nessun ep fattibile, ritorna False, altrimenti ritorna True e la lista di ep fattibili
        (item_to_pack.x_position, item_to_pack.y_position, item_to_pack.z_position) = (None, None, None)
        if not feasible_solutions:
            return None
        return feasible_solutions


    @staticmethod
    def packItemIntoContainer(solution: SingleSolutionFeasible):
        #Variabili prese dalla soluzione
        container = solution.container
        item = solution.item

        #Aggiornamento Item
        (ex, ey, ez) = solution.ep
        (item.x_position, item.y_position, item.z_position) = (ex, ey, ez)
        item.curr_width = solution.item_width
        item.curr_depth = solution.item_depth
        item.height = solution.item_height

        #Aggiornamento Container
        container.remaining_weight -= item.weight
        container.value -= item.value
        container.items_placed.append(item)
        pass

    @staticmethod
    def openNewContainer(set_containers: set[Container]):
        pass

    def provaSara(self):
        pass



