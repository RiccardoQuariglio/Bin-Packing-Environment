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
        template = max(set_containers, key=lambda x: x.volume/x.cost)
        new_instance = Container(
            type_name=template.type,
            width=template.width,
            depth=template.depth,
            height=template.height,
            max_weight=template.max_weight,
            cost=template.cost,
            max_value=template.max_value,
            gravity=template.gravity_strength
        )
        return new_instance




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
                        rotation = item_to_pack.curr_rotation_number
                        feasible_solution = SingleSolutionFeasible(
                            container,
                            item_to_pack,
                            item_to_pack.curr_width,
                            item_to_pack.curr_depth,
                            item_to_pack.curr_height,
                            ep,
                            rotation)
                        feasible_solution.computeMerit()
                        feasible_solutions.append(feasible_solution)
                    else:
                        current_support_area = 0
                        min_support_area = item_to_pack.curr_width * item_to_pack.curr_depth * (container.gravity_strength/100)
                        for box_placed in container.items_placed:
                            current_support_area += item_to_pack.get_support_area(box_placed)

                        if current_support_area >= min_support_area:
                            rotation = item_to_pack.curr_rotation_number
                            feasible_solution = SingleSolutionFeasible(
                                container,
                                item_to_pack,
                                item_width=item_to_pack.curr_width,
                                item_depth=item_to_pack.curr_depth,
                                item_height=item_to_pack.curr_height,
                                ep=ep,
                                rotation=rotation)
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
        item.curr_height = solution.item_height

        #Aggiornamento Container
        container.remaining_weight -= item.weight
        container.remaining_value -= item.value
        container.items_placed.append(item)

        if solution.ep in container.extreme_points:
            container.extreme_points.remove(solution.ep)

        max_bounds = {"YX": -1,
                      "YZ": -1,
                      "XY": -1,
                      "XZ": -1,
                      "ZX": -1,
                      "ZY": -1 }
        new_ex_points = {"YX": (None, None, None),
                      "YZ": (None, None, None),
                      "XY": (None, None, None),
                      "XZ": (None, None, None),
                      "ZX": (None, None, None),
                      "ZY": (None, None, None) }

        for other in container.items_placed:
            if other == item: continue

            # Esempio Direzione YX: proiettiamo x_spigolo verso Y
            if AdditionalScript.canTakeProjection(item, other, "YX"):
                potential_y = other.y_position + other.curr_depth
                if potential_y > max_bounds["YX"]:
                    max_bounds["YX"] = potential_y
                    new_ex_points["YX"] = (item.x_position + item.curr_width, potential_y, item.z_position)

            # 1. YZ: Proiettiamo lo spigolo z (zk+hk) verso Y, cerchiamo supporto su faccia Z
            if AdditionalScript.canTakeProjection(item, other, "YZ"):
                potential_y = other.y_position + other.curr_depth
                if potential_y > max_bounds["YZ"]:
                    max_bounds["YZ"] = potential_y
                    new_ex_points["YZ"] = (item.x_position, potential_y, item.z_position + item.curr_height)

            # Esempio Direzione XY: proiettiamo y_spigolo verso X
            if AdditionalScript.canTakeProjection(item, other, "XY"):
                potential_x = other.x_position + other.curr_width
                if potential_x > max_bounds["XY"]:
                    max_bounds["XY"] = potential_x
                    new_ex_points["XY"] = (potential_x, item.y_position + item.curr_depth, item.z_position)

            # 3. XZ: Proiettiamo lo spigolo z (zk+hk) verso X, cerchiamo supporto su faccia Z
            if AdditionalScript.canTakeProjection(item, other, "XZ"):
                potential_x = other.x_position + other.curr_width
                if potential_x > max_bounds["XZ"]:
                    max_bounds["XZ"] = potential_x
                    new_ex_points["XZ"] = (potential_x, item.y_position, item.z_position + item.curr_height)

            # --- DIREZIONI ASSE Z ---
            # 4. ZX: Proiettiamo lo spigolo x (xk+wk) verso Z, cerchiamo supporto su faccia X
            if AdditionalScript.canTakeProjection(item, other, "ZX"):
                potential_z = other.z_position + other.curr_height
                if potential_z > max_bounds["ZX"]:
                    max_bounds["ZX"] = potential_z
                    new_ex_points["ZX"] = (item.x_position + item.curr_width, item.y_position, potential_z)

            # 5. ZY: Proiettiamo lo spigolo y (yk+dk) verso Z, cerchiamo supporto su faccia Y
            if AdditionalScript.canTakeProjection(item, other, "ZY"):
                potential_z = other.z_position + other.curr_height
                if potential_z > max_bounds["ZY"]:
                    max_bounds["ZY"] = potential_z
                    new_ex_points["ZY"] = (item.x_position, item.y_position + item.curr_depth, potential_z)

            # Aggiungiamo i 3 vertici diretti (sempre generati come base)[cite: 2]
        base_pts = [
            (item.x_position + item.curr_width, item.y_position, item.z_position),
            (item.x_position, item.y_position + item.curr_depth, item.z_position),
            (item.x_position, item.y_position, item.z_position + item.curr_height)
        ]

        # Inserimento finale nella lista degli EP del container
        for p in (list(new_ex_points.values()) + base_pts):
            if p not in container.extreme_points and p != (None, None, None):
                # Verifichiamo i limiti fisici del bin
                if p[0] <= container.width and p[1] <= container.depth and p[2] <= container.height:
                    container.extreme_points.append(p)

        # 4. Ordinamento EP (z, y, x non decrescente)
        container.extreme_points.sort(key=lambda p: (p[2], p[1], p[0]))


    @staticmethod
    def canTakeProjection(item_new, other, direction):
        """
        Verifica se il punto spigolo dell'item_new può essere proiettato
        sulla faccia dell'other nella direzione specificata.
        """
        # Coordinate e dimensioni item_new (nuovo)
        x_new, y_new, z_new = item_new.x_position, item_new.y_position, item_new.z_position
        w_new, d_new, h_new = item_new.curr_width, item_new.curr_depth, item_new.curr_height

        # Coordinate e dimensioni other (già presente)
        x_other, y_other, z_other = other.x_position, other.y_position, other.z_position
        w_other, d_other, h_other = other.curr_width, other.curr_depth, other.curr_height


        if direction == "YX":
            # Punto (x_new+w_new, y_new, z_new) proiettato in Y, cerchiamo supporto su X
            # Requisito: Il punto deve essere nel range X e Z dell'other
            # e trovarsi 'davanti' (y maggiore) rispetto a other
            return (x_other <= x_new + w_new < x_other + w_other) and (z_other <= z_new < z_other + h_other) and (y_other + d_other <= y_new)

        elif direction == "YZ":
            # Punto (x_new, y_new+d_new, z_new) proiettato in Y, cerchiamo supporto su Z
            return (x_other <= x_new < x_other + w_other) and (y_other + d_other <= y_new) and (z_other <= z_new < z_other + h_other)  # Semplificaz_otherone pratica

        elif direction == "XY":
            # Punto (x_new, y_new+d_new, z_new) proiettato in X, cerchiamo supporto su Y
            return (y_other <= y_new + d_new < y_other + d_other) and (z_other <= z_new < z_other + h_other) and (x_other + w_other <= x_new)

        elif direction == "XZ":
            # Punto (x_new, y_new, z_new+h_new) proiettato in X, cerchiamo supporto su Z
            return (y_other <= y_new < y_other + d_other) and (z_other <= z_new + h_new < z_other + h_other) and (x_other + w_other <= x_new)

        elif direction == "ZX":
            # Punto (x_new+w_new, y_new, z_new) proiettato in Z, cerchiamo supporto su X
            return (x_other <= x_new + w_new < x_other + w_other) and (y_other <= y_new < y_other + d_other) and (z_other + h_other <= z_new)

        elif direction == "ZY":
            # Punto (x_new, y_new+d_new, z_new) proiettato in Z, cerchiamo supporto su Y
            return (y_other <= y_new + d_new < y_other + d_other) and (x_other <= x_new < x_other + w_other) and (z_other + h_other <= z_new)

        return False



    @staticmethod
    def openNewContainer(set_containers: set[Container]):
        # Scegliamo il modello (template) migliore dal set
        template = max(set_containers, key=lambda x: x.width * x.depth)

        # CREIAMO UN NUOVO OGGETTO basato sui dati del template
        new_instance = Container(
            type_name=template.type,
            width=template.width,
            depth=template.depth,
            height=template.height,
            max_weight=template.max_weight,
            cost=template.cost,
            max_value=template.max_value,
            gravity=template.gravity_strength
        )
        return new_instance





