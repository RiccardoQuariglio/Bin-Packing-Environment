try:
    from .item import Item
    from .container import Container
    from .singleSolutionFeasible import SingleSolutionFeasible
except ImportError:
    from item import Item
    from container import Container
    from singleSolutionFeasible import SingleSolutionFeasible

"""
    Ordine delle funzioni nel file additional_script:
    1) loadItems(df_items) --> memorizza gli items in una lista non ordinata
    2) loadContainers(df_vehicles) --> memorizza i containers in una lista non ordinata
    3) sortedItemsByAHW(items) --> ordina gli items di una lista per area e altezza decrescente
    4) itemFitsContainer(item, container) --> verifica se l'item entra nel container in almeno una rotazione
    5) chooseContainer(item_to_pack, containers_lista, vol_medio, peso_medio, valore_medio) -->
       restituisce la lista dei container candidati ordinati dal migliore al peggiore
       (criterio: max items_stimati/cost, poi area di base, poi min gravityStrength)
    6) isFeasible(item_to_pack, container) --> verifica che un item possa essere impaccato in un container
    6) chooseLastContainer(item_to_pack, containers_lista) --> endgame: restituisce i candidati
       ordinati per costo minimo (usata quando il volume residuo è piccolo)
    7) isFeasible(item_to_pack, container) --> verifica che un item possa essere impaccato in un container
    8) packItemIntoContainer(best_solution) --> impacca l'item e aggiorna gli extreme points
    9) canTakeProjection(item_new, other, direction) --> verifica proiezioni per gli extreme points
    """

class AdditionalScript:

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
        # Lista (non un set) per garantire un ordine di iterazione deterministico:
        # i max() in chooseFirstContainer/openNewContainer risolvono così i pareggi
        # sempre allo stesso modo, rendendo le soluzioni ripetibili.
        containers_list = []
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
            containers_list.append(new_container)
        return containers_list

    #Esempi di sorting

    @staticmethod
    def sortedItemsByAHW(items):
    #Ordina gli oggetti basandosi sulle loro dimensioni massime potenziali
        sorted_list=[]
        def getBestMetrics(item):
            max_h = 0
            max_area = 0
            
            for rot_idx in item.allowed_rotations:
                item.setRotation(rot_idx)
                max_area = max(max_area, item.curr_width * item.curr_depth)
                max_h = max(max_h, item.curr_height)
                
            return max_area, max_h, item.weight

        sorted_list = sorted(
            items,
            key= getBestMetrics,
            reverse=True)
        return sorted_list

    @staticmethod
    def itemFitsContainer(item: Item, container: Container):
        # Verifica se l'item entra nel container in almeno una delle rotazioni ammesse
        saved_rotation = item.curr_rotation_number
        fits = False
        for rot_idx in item.allowed_rotations:
            item.setRotation(rot_idx)
            if (item.curr_depth <= container.depth and
                    item.curr_width <= container.width and
                    item.curr_height <= container.height):
                fits = True
                break
        item.setRotation(saved_rotation)
        return fits

    @staticmethod
    def chooseContainer(item_to_pack: Item, containers_lista: list[Container],
                        vol_medio: float, peso_medio: float, valore_medio: float):
        # Sceglie il container migliore stimando quanti item ci entreranno effettivamente.
        #
        # Il criterio volume/cost ignorava i vincoli di maxWeight e maxValue: un container
        # piccolo e economico ma con maxWeight basso si satura subito e ne servono tanti,
        # vanificando il risparmio unitario.
        #
        # Invece, per ogni container candidato si stima il numero di item che può contenere
        # come il MINIMO tra tre limiti:
        #   - volume_container / volume_medio_item   (limite spaziale)
        #   - maxWeight / peso_medio_item             (limite di peso)
        #   - maxValue / valore_medio_item            (limite di valore)
        # Il vincolo più stringente determina quanti item ci stanno realmente.
        # Si massimizza items_stimati / cost: il container che contiene più item per euro.
        #
        # Tie-break: area di base (più superficie), poi min gravityStrength (meno vincolante).
        #
        # Restituisce la lista dei candidati ordinati dal migliore al peggiore;
        # il solver li prova in ordine finché trova uno in cui l'item entra (isFeasible).

        candidates = [c for c in containers_lista if AdditionalScript.itemFitsContainer(item_to_pack, c)]
        if not candidates:
            return []

        def containerScore(c):
            items_by_vol = c.volume / vol_medio if vol_medio > 0 else float('inf')
            items_by_weight = c.max_weight / peso_medio if peso_medio > 0 else float('inf')
            items_by_value = c.max_value / valore_medio if valore_medio > 0 else float('inf')
            items_stimati = min(items_by_vol, items_by_weight, items_by_value)
            return (items_stimati / c.cost, c.width * c.depth, -c.gravity_strength)

        candidates.sort(key=containerScore, reverse=True)
        result = []
        for template in candidates:
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
            result.append(new_instance)
        return result

    @staticmethod
    def chooseLastContainer(item_to_pack: Item, containers_lista: list[Container]):
        # Endgame: quando il volume residuo è piccolo, predilige container più economici
        # per evitare di aprire un container grande e costoso per pochi item.
        # Criterio lessicografico:
        # 1) min costo (container più economico)
        # 2) min volume (più piccolo che basta)
        # 3) min gravityStrength (meno vincolante)
        candidates = [c for c in containers_lista if AdditionalScript.itemFitsContainer(item_to_pack, c)]
        if not candidates:
            return []
        candidates.sort(key=lambda c: (c.cost, c.volume, c.gravity_strength))
        result = []
        for template in candidates:
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
            result.append(new_instance)
        return result

    @staticmethod
    def isFeasible(item_to_pack: Item, container: Container):
        #Verifica peso e valore item (basta uno dei due a sforare per essere infeasible)
        if item_to_pack.weight > container.remaining_weight:
            return None
        if item_to_pack.value > container.remaining_value:
            return None

        feasible_solutions = []

        # Salvo lo stato corrente per ripristinarlo a fine funzione (l'item non è ancora piazzato)
        saved_rotation = item_to_pack.curr_rotation_number

        # Itero su tutte le rotazioni ammesse per questo item
        for rot_idx in item_to_pack.allowed_rotations:
            item_to_pack.setRotation(rot_idx)

            for ep in container.extreme_points:
                (ex, ey, ez) = ep
                (item_to_pack.x_position, item_to_pack.y_position, item_to_pack.z_position) = (ex, ey, ez)

                #Verifica limiti container (x->depth, y->width, z->height)
                if not (ex + item_to_pack.curr_depth <= container.depth and
                        ey + item_to_pack.curr_width <= container.width and
                        ez + item_to_pack.curr_height <= container.height):
                    continue

                #Verifica sovrapposizioni con altri oggetti nel container
                overlapping = False
                for box_placed in container.items_placed:
                    if item_to_pack.boxesOverlap(box_placed):
                        overlapping = True
                        break
                if overlapping:
                    continue

                #Verifica Gravity Strength
                if ez == 0:
                    pass  # tocca il pavimento, sempre supportato
                else:
                    current_support_area = 0.0
                    min_support_area = (item_to_pack.curr_width * item_to_pack.curr_depth *
                                        (container.gravity_strength / 100.0))
                    for box_placed in container.items_placed:
                        current_support_area += item_to_pack.getSupportArea(box_placed)
                    if current_support_area + 1e-9 < min_support_area:
                        continue

                feasible_solution = SingleSolutionFeasible(
                    container,
                    item_to_pack,
                    item_width=item_to_pack.curr_width,
                    item_depth=item_to_pack.curr_depth,
                    item_height=item_to_pack.curr_height,
                    ep=ep,
                    rotation=item_to_pack.curr_rotation_number)
                feasible_solution.computeMerit()
                feasible_solutions.append(feasible_solution)

        # Ripristino lo stato dell'item (non è ancora piazzato qui)
        item_to_pack.setRotation(saved_rotation)
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


        """??? ALGORITMO 1
        E giusto togliere l'ep della soluzione ottenuta dalla lista di ep del container"""
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
                potential_y = other.y_position + other.curr_width
                if potential_y > max_bounds["YX"]:
                    max_bounds["YX"] = potential_y
                    new_ex_points["YX"] = (item.x_position + item.curr_depth, potential_y, item.z_position)

            # 1. YZ: Proiettiamo lo spigolo z (zk+hk) verso Y, cerchiamo supporto su faccia Z
            if AdditionalScript.canTakeProjection(item, other, "YZ"):
                potential_y = other.y_position + other.curr_width
                if potential_y > max_bounds["YZ"]:
                    max_bounds["YZ"] = potential_y
                    new_ex_points["YZ"] = (item.x_position, potential_y, item.z_position + item.curr_height)

            # Esempio Direzione XY: proiettiamo y_spigolo verso X
            if AdditionalScript.canTakeProjection(item, other, "XY"):
                potential_x = other.x_position + other.curr_depth
                if potential_x > max_bounds["XY"]:
                    max_bounds["XY"] = potential_x
                    new_ex_points["XY"] = (potential_x, item.y_position + item.curr_width, item.z_position)

            # 3. XZ: Proiettiamo lo spigolo z (zk+hk) verso X, cerchiamo supporto su faccia Z
            if AdditionalScript.canTakeProjection(item, other, "XZ"):
                potential_x = other.x_position + other.curr_depth
                if potential_x > max_bounds["XZ"]:
                    max_bounds["XZ"] = potential_x
                    new_ex_points["XZ"] = (potential_x, item.y_position, item.z_position + item.curr_height)

            # --- DIREZIONI ASSE Z ---
            # 4. ZX: Proiettiamo lo spigolo x (xk+wk) verso Z, cerchiamo supporto su faccia X
            if AdditionalScript.canTakeProjection(item, other, "ZX"):
                potential_z = other.z_position + other.curr_height
                if potential_z > max_bounds["ZX"]:
                    max_bounds["ZX"] = potential_z
                    new_ex_points["ZX"] = (item.x_position + item.curr_depth, item.y_position, potential_z)

            # 5. ZY: Proiettiamo lo spigolo y (yk+dk) verso Z, cerchiamo supporto su faccia Y
            if AdditionalScript.canTakeProjection(item, other, "ZY"):
                potential_z = other.z_position + other.curr_height
                if potential_z > max_bounds["ZY"]:
                    max_bounds["ZY"] = potential_z
                    new_ex_points["ZY"] = (item.x_position, item.y_position + item.curr_width, potential_z)

            # Aggiungiamo i 3 vertici diretti (sempre generati come base)[cite: 2]
        base_pts = [
            (item.x_position + item.curr_depth, item.y_position, item.z_position),
            (item.x_position, item.y_position + item.curr_width, item.z_position),
            (item.x_position, item.y_position, item.z_position + item.curr_height)
        ]

        # Inserimento finale nella lista degli EP del container
        for p in (list(new_ex_points.values()) + base_pts):
            if p not in container.extreme_points and p != (None, None, None):
                # Verifichiamo i limiti fisici del bin
                if p[0] <= container.depth and p[1] <= container.width and p[2] <= container.height:
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
            return (x_other <= x_new + d_new < x_other + d_other) and (z_other <= z_new < z_other + h_other) and (y_other + w_other <= y_new)

        elif direction == "YZ":
            # Punto (x_new, y_new+d_new, z_new) proiettato in Y, cerchiamo supporto su Z
            return (x_other <= x_new < x_other + d_other) and (y_other + w_other <= y_new) and (z_other <= z_new < z_other + h_other)  # Semplificazione pratica

        elif direction == "XY":
            # Punto (x_new, y_new+d_new, z_new) proiettato in X, cerchiamo supporto su Y
            return (y_other <= y_new + w_new < y_other + w_other) and (z_other <= z_new < z_other + h_other) and (x_other + d_other <= x_new)

        elif direction == "XZ":
            # Punto (x_new, y_new, z_new+h_new) proiettato in X, cerchiamo supporto su Z
            return (y_other <= y_new < y_other + w_other) and (z_other <= z_new + h_new < z_other + h_other) and (x_other + d_other <= x_new)

        elif direction == "ZX":
            # Punto (x_new+w_new, y_new, z_new) proiettato in Z, cerchiamo supporto su X
            return (x_other <= x_new + d_new < x_other + d_other) and (y_other <= y_new < y_other + w_other) and (z_other + h_other <= z_new)

        elif direction == "ZY":
            # Punto (x_new, y_new+d_new, z_new) proiettato in Z, cerchiamo supporto su Y
            return (y_other <= y_new + w_new < y_other + w_other) and (x_other <= x_new < x_other + d_other) and (z_other + h_other <= z_new)

        return False








