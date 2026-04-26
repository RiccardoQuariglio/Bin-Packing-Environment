from item import Item
from container import Container
import random

"""
    Ordine delle funzioni nel file additional_script:
    _load_items(df_items) --> memorizza gli items in una lista non ordinata
    _load_containers(df_vehicles) --> memorizza i containers in una lista non ordinata
    _sorted_items_by_a_h_w(items) --> ordina gli items di una lista per area e altezza decrescente
    _stochastic_sorted_items(items, randomness=0.4) --> ordina gli items di una lista con fattore di randomicità    
    
    """

class AdditionalScript():
    def doNothing(self):
        pass

    @staticmethod
    def _load_items(df_items):
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
    def _load_containers(df_vehicles):
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
    def _sorted_items_by_a_h_w(items):
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
    def _stochastic_sorted_items(items, randomness=0.4):
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
    
    
    def donothing(self):
        pass