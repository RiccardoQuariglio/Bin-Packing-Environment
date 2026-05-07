"""
Funzione di merito per 3D Bin Packing con Extreme Points.

Valuta ogni extreme point candidato per il posizionamento di un item,
combinando due penalità:
  - pen_xy : spazio residuo su X e Y (superficie) → da minimizzare
  - pen_z  : differenza di altezza rispetto agli altri item → da minimizzare

Score finale: beta * pen_z + alpha * pen_xy
  (beta > alpha per dare priorità all'uniformità in altezza)
"""

from dataclasses import dataclass
from typing import Optional
import math


# ---------------------------------------------------------------------------
# Strutture dati
# ---------------------------------------------------------------------------

@dataclass
class Item:
    """Item da posizionare nel container."""
    w: float   # larghezza (asse X)
    d: float   # profondità (asse Y)
    h: float   # altezza   (asse Z)


@dataclass
class ExtremePoint:
    """Extreme point candidato per il posizionamento."""
    x: float
    y: float
    z: float


@dataclass
class Container:
    """Container 3D."""
    W: float   # larghezza massima (asse X)
    D: float   # profondità massima (asse Y)
    H: float   # altezza massima   (asse Z)


@dataclass
class PlacedItem:
    """Item già posizionato nel container."""
    x: float
    y: float
    z: float
    w: float
    d: float
    h: float

    @property
    def top_z(self) -> float:
        """Quota della faccia superiore dell'item."""
        return self.z + self.h


# ---------------------------------------------------------------------------
# Verifica fattibilità
# ---------------------------------------------------------------------------

def is_feasible(
    ep: ExtremePoint,
    item: Item,
    container: Container,
    placed_items: list[PlacedItem],
) -> bool:
    """
    Verifica che l'item posizionato in ep rientri nel container
    e non si sovrapponga ad altri item già posizionati.
    """
    # Controllo bordi container
    if (ep.x + item.w > container.W or
            ep.y + item.d > container.D or
            ep.z + item.h > container.H):
        return False

    # Controllo collisioni con item già posizionati
    for placed in placed_items:
        overlap_x = ep.x < placed.x + placed.w and ep.x + item.w > placed.x
        overlap_y = ep.y < placed.y + placed.d and ep.y + item.d > placed.y
        overlap_z = ep.z < placed.z + placed.h and ep.z + item.h > placed.z
        if overlap_x and overlap_y and overlap_z:
            return False

    return True


# ---------------------------------------------------------------------------
# Calcolo penalità
# ---------------------------------------------------------------------------

def penalty_surface(
    ep: ExtremePoint,
    item: Item,
    container: Container,
) -> float:
    """
    Penalità sulla superficie occupata (assi X e Y).

    Misura lo spazio residuo normalizzato: un valore alto indica che
    l'item lascia molto spazio libero sul piano XY, il che è penalizzato.
    """
    res_x = container.W - (ep.x + item.w)
    res_y = container.D - (ep.y + item.d)

    # Normalizzazione rispetto alle dimensioni del container
    norm_res_x = res_x / container.W
    norm_res_y = res_y / container.D

    # Media geometrica per bilanciare le due direzioni
    return math.sqrt(norm_res_x ** 2 + norm_res_y ** 2)


def penalty_height(
    ep: ExtremePoint,
    item: Item,
    placed_items: list[PlacedItem],
    container: Container,
) -> float:
    """
    Penalità sull'altezza (asse Z).

    Misura la differenza media tra la quota superiore dell'item corrente
    e quella degli item già posizionati: incentiva l'uniformità in altezza.
    """
    item_top = ep.z + item.h

    if not placed_items:
        # Nessun item presente: penalità proporzionale all'altezza assoluta
        return item_top / container.H

    tops = [p.top_z for p in placed_items]
    avg_top = sum(tops) / len(tops)

    # Differenza normalizzata rispetto all'altezza del container
    diff = abs(item_top - avg_top) / container.H
    return diff


# ---------------------------------------------------------------------------
# Funzione di merito principale
# ---------------------------------------------------------------------------

def merit_score(
    ep: ExtremePoint,
    item: Item,
    container: Container,
    placed_items: list[PlacedItem],
    alpha: float = 1.0,
    beta: float = 2.0,
) -> float:
    """
    Calcola il punteggio di merito per il posizionamento di un item in ep.

    Parametri
    ----------
    ep            : extreme point candidato
    item          : item da posizionare
    container     : container 3D
    placed_items  : item già posizionati
    alpha         : peso penalità superficie (XY)  [default 1.0]
    beta          : peso penalità altezza (Z)       [default 2.0]

    Restituisce
    -----------
    Score da minimizzare. Valori più bassi = posizionamento migliore.
    """
    pen_xy = penalty_surface(ep, item, container)
    pen_z  = penalty_height(ep, item, placed_items, container)

    # Priorità: altezza (beta > alpha) poi superficie
    return beta * pen_z + alpha * pen_xy


# ---------------------------------------------------------------------------
# Selezione dell'extreme point ottimale
# ---------------------------------------------------------------------------

def best_extreme_point(
    item: Item,
    extreme_points: list[ExtremePoint],
    container: Container,
    placed_items: list[PlacedItem],
    alpha: float = 1.0,
    beta: float = 2.0,
) -> Optional[tuple[ExtremePoint, float]]:
    """
    Seleziona l'extreme point con il miglior (minimo) score di merito.

    Restituisce una tupla (ep_migliore, score) oppure None se nessun EP
    è fattibile per l'item dato.
    """
    best_ep    = None
    best_score = float("inf")

    for ep in extreme_points:
        if not is_feasible(ep, item, container, placed_items):
            continue

        score = merit_score(ep, item, container, placed_items, alpha, beta)

        if score < best_score:
            best_score = score
            best_ep    = ep

    if best_ep is None:
        return None

    return best_ep, best_score


# ---------------------------------------------------------------------------
# Esempio d'uso
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    container = Container(W=10.0, D=10.0, H=10.0)

    item = Item(w=3.0, d=3.0, h=2.0)

    extreme_points = [
        ExtremePoint(0, 0, 0),
        ExtremePoint(3, 0, 0),
        ExtremePoint(0, 3, 0),
        ExtremePoint(3, 3, 0),
        ExtremePoint(0, 0, 2),
    ]

    # Simuliamo un item già posizionato
    placed_items = [
        PlacedItem(x=0, y=0, z=0, w=3, d=3, h=2),
    ]

    result = best_extreme_point(
        item, extreme_points, container, placed_items,
        alpha=1.0, beta=2.0,
    )

    if result:
        ep, score = result
        print(f"Extreme point ottimale: ({ep.x}, {ep.y}, {ep.z})")
        print(f"Score di merito: {score:.4f}")

        # Dettaglio penalità
        pen_xy = penalty_surface(ep, item, container)
        pen_z  = penalty_height(ep, item, placed_items, container)
        print(f"  → Penalità superficie (α·pen_xy): {1.0 * pen_xy:.4f}")
        print(f"  → Penalità altezza    (β·pen_z):  {2.0 * pen_z:.4f}")
    else:
        print("Nessun extreme point fattibile trovato.")
