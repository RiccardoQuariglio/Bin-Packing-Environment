from item import Item
from container import Container
import random

"""
    Ordine delle funzioni nel file additional_script:
    loadItems(df_items) --> memorizza gli items in una lista non ordinata
    loadContainers(df_vehicles) --> memorizza i containers in una lista non ordinata
    sortedItemsByAHW(items) --> ordina gli items di una lista per area e altezza decrescente
    stochasticSortedItems(items, randomness=0.4) --> ordina gli items di una lista con fattore di randomicità    
    
    """

class AdditionalScript():
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
            return False

        ep_feasible = []
        for ep in container.extreme_points:
            (ex, ey, ez) = ep
            #Verifica limiti container
            if (ex + item_to_pack.curr_width <= container.width and
                ey + item_to_pack.curr_depth <= container.depth and
                    ez + item_to_pack.curr_height <= container.height):

                #Verifica sovrapposizioni con altri oggetti nel container
                overlapping = False
                for obj_inserito in container.items_placed:
                    if (ex < obj_inserito.x_position + obj_inserito.curr_width and
                            ex + item.curr_width > obj_inserito.x_position and
                            ey < obj_inserito.y_position + obj_inserito.curr_depth and
                            ey + item.curr_depth > obj_inserito.y_position and
                            ez < obj_inserito.z_position + obj_inserito.curr_height and
                            ez + item.curr_height > obj_inserito.z_position):
                        sovrapposizione = True
                        break








    @staticmethod
    def computeMerit(container: Container):
        pass

    @staticmethod
    def containerBestMerit(list_containers):
        pass

    @staticmethod
    def packItemIntoContainer(item: Item, container: Container):
        pass

    @staticmethod
    def openNewContainer(set_containers: set[Container]):
        pass

    def provaSara(self):
        pass



