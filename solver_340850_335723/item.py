class Item:
    def __init__(self, item_id, width, depth, height, weight, value, allowed_rotations):
        #Definizione degli attributi principali attraverso il costruttore
        self.id = item_id
        self.width = width
        self.depth = depth
        self.height = height
        self.weight = weight
        self.value = value
        self.allowed_rotations = [int(ar) for ar in str(allowed_rotations)]

        #Gestione delle rotazioni
        self.curr_width, self.curr_depth, self.curr_height = width, depth, height

    #Funzione che modifica i valori 3D in base alla rotazione effettuata
    # (lista presa dal file results_checker)
    def set_rotation(self, rotation_number):
        w, d, h = self.width, self.depth, self.height
        rotations = [
            (w, d, h),
            (d, w, h),
            (h, d, w),
            (d, h, w),
            (w, h, d),
            (h, w, d),
        ]
        self.curr_width, self.curr_depth, self.curr_height = rotations[rotation_number]

    #Definizione _toString che serve per testare il codice
    def __str__(self):
        return (f"Codice: {self.id}, Width: {self.width}, Depth: {self.depth}, Height: {self.height}, "
                f"Weight: {self.weight}, Value: {self.value}.")


