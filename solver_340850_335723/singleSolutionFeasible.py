"""
Classe usata per gestire più comodamente le soluzioni fattibili.
Ha come parametri il container, l'item (e le dimensioni per cui è calcolata la soluzione)
e l'ep per cui è calcolata. Implementa la funzione ComputeMerit, così da avere sotto mano
tutti i dati poi per 1) scegliere la soluzione migliore e 2) per aggiornare il container
senza andare a cercare i dati in maniera difficile.
"""

class SingleSolutionFeasible:
    def __init__(self, container, item, item_width, item_depth, item_height, ep, rotation):
        self.container = container
        self.item = item
        self.item_width = item_width
        self.item_depth = item_depth
        self.item_height = item_height
        self.ep = ep
        self.item_rotation = rotation
        self.merit = None

    def computeMerit(self):
        # RS (Residual Space) = distanza dal bordo del container lungo ciascun asse
        # (asse x -> depth, asse y -> width, asse z -> height)
        rs_depth  = self.container.depth  - (self.ep[0] + self.item_depth)
        rs_width  = self.container.width  - (self.ep[1] + self.item_width)
        rs_height = self.container.height - (self.ep[2] + self.item_height)
        # Merito dell'articolo (pagg. 11-12): minimizzare la somma dei residui
        self.merit = -(rs_depth + rs_width + rs_height)  # Usiamo il meno perché poi cerchi il MAX