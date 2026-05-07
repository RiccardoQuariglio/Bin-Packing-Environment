#Ciao Riki

class Container:
    def __init__(self, type_name, width, depth, height, max_weight, cost, max_value, gravity):
        self.type = type_name
        self.idx = None
        self.width = width
        self.depth = depth
        self.height = height
        self.volume = width * depth * height
        self.max_weight = max_weight
        self.cost = cost
        self.max_value = max_value
        self.gravity_strength = gravity

        #Parametri utilizzati per gestire l'impaccamento
        self.remaining_value = max_value
        self.remaining_weight = max_weight
        self.items_placed = []  # Lista di oggetti Item già posizionati
        self.extreme_points = [(0, 0, 0)]  # Inizializzazione EP

    # Definizione _toString che serve per testare il codice
    def __str__(self):
        return (f"Type: {self.type}, Width: {self.width}, Depth: {self.depth}, Height: {self.height}, "
                f"Max Weight: {self.max_weight}, Cost: {self.cost}, Max Value: {self.max_value}, Gravity Strength: {self.gravity_strength}")

