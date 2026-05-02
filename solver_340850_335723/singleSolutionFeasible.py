"""
Classe usata per gestire più comodamente le soluzioni fattibili.
Ha come parametri il container, l'item (e le dimensioni per cui è calcolata la soluzione)
e l'ep per cui è calcolata. Implementa la funzione ComputeMerit, così da avere sotto mano
tutti i dati poi per 1) scegliere la soluzione migliore e 2) per aggiornare il container
senza andare a cercare i dati in maniera difficile.
"""

class SingleSolutionFeasible:
    def __init__(self, container, item, item_width, item_depth, item_height, ep):
        self.container = container
        self.item = item
        self.item_width = item_width
        self.item_depth = item_depth
        self.item_height = item_height
        self.ep = ep
        merit = None

    def computeMerit(self):
        pass