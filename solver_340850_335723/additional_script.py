from item import Item
from container import Container

"""
    Ordine delle funzioni nel file additional_script:
    _load_items(df_items) --> memorizza gli items in una lista non ordinata
    _load_containers(df_vehicles) --> memorizza i containers in una lista non ordinata
    _sort_items_by_width_increasing(items_list) --> ordina gli items di una lista per width crescente
    _sort_items_by_volume_decreasing(items_list) --> ordina gli items di una lista per volume decrescente
    
    
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
    def _sort_items_by_width_increasing(items_list):
        sorted_list = sorted(
            items_list,
            key=lambda item: item.width)
        return sorted_list

    @staticmethod
    def _sort_items_by_volume_decreasing(items_list):
        sorted_list = sorted(
            items_list,
            key=lambda item: (item.width * item.depth * item.height),
            reverse=True
        )
        return sorted_list

    #Funzioni per impaccamento: 1) Best Fit Decreasing e 2) Bottom Left Fill
    @staticmethod
    def _BFD_packing():
        pass

    @staticmethod
    def _BLF_packing():
        pass