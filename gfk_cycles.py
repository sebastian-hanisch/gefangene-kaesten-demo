"""Zyklen einer Anordnung (numpy/Standardbibliothek). Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b).

Eine Anordnung ist ein Feld `q` der Länge n: Kasten j enthält den Zettel `q[j]` (alles von 0 an gezählt; angezeigt wird ab 1). Gefangener i sucht den Zettel i.
Die Zyklus-Strategie öffnet zuerst Kasten i und danach den Kasten, dessen Nummer der gerade gefundene Zettel trägt. Sie führt genau um den Zyklus von i in q herum:
der Zettel i liegt im letzten Kasten dieses Zyklus. Gefangener i hat deshalb genau dann Erfolg, wenn der Zyklus von i höchstens m Kästen lang ist."""

from __future__ import annotations

import math

import numpy as np


def is_permutation(q) -> bool:
    """Enthält q jede Zahl von 0 bis n-1 genau einmal?"""
    return sorted(int(x) for x in q) == list(range(len(q)))


def cycles_of(q) -> list[list[int]]:
    """Die Zyklen von q als Listen von Kästen in Öffnungsreihenfolge, geordnet nach dem kleinsten Kasten jedes Zyklus."""
    n = len(q)
    seen = [False] * n
    out = []
    for start in range(n):
        if seen[start]:
            continue
        cyc, j = [], start
        while not seen[j]:
            seen[j] = True
            cyc.append(j)
            j = int(q[j])
        out.append(cyc)
    return out


def cycle_lengths(q) -> list[int]:
    return [len(c) for c in cycles_of(q)]


def follow_boxes(q, prisoner: int, m: int) -> tuple[list[tuple[int, int]], bool]:
    """Wörtliche Zyklus-Strategie für einen Gefangenen: öffnet Kasten `prisoner`, dann den Kasten mit der Nummer des gefundenen Zettels, höchstens m Kästen.
    Gibt die Folge (Kasten, gefundener Zettel) und zurück, ob der eigene Zettel gefunden wurde."""
    opened = []
    box = prisoner
    for _ in range(m):
        slip = int(q[box])
        opened.append((box, slip))
        if slip == prisoner:
            return opened, True
        box = slip
    return opened, False


def min_label_batch(perms: np.ndarray) -> np.ndarray:
    """Für jede Anordnung (Zeile) und jeden Kasten die kleinste Kastennummer seines Zyklus, durch Zeigerverdopplung in ceil(log2 n) Runden.
    Nach t Runden ist das Minimum über 2^t aufeinanderfolgende Kästen des Zyklus gebildet; 2^t >= n deckt jeden Zyklus ab."""
    runs, n = perms.shape
    label = np.tile(np.arange(n), (runs, 1))
    jump = perms.copy()
    for _ in range(max(0, math.ceil(math.log2(n)))):
        label = np.minimum(label, np.take_along_axis(label, jump, axis=1))
        jump = np.take_along_axis(jump, jump, axis=1)
    return label


def element_cycle_lengths(perms: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(Länge des Zyklus, in dem jeder Kasten liegt; Vertreter-Maske = Kasten ist der kleinste seines Zyklus). Beide mit der Form (Läufe, n)."""
    runs, n = perms.shape
    label = min_label_batch(perms)
    keys = label + n * np.arange(runs)[:, None]
    counts = np.bincount(keys.ravel(), minlength=runs * n)
    lengths = counts[keys]
    return lengths, label == np.arange(n)[None, :]


def swap_cost_of_lengths(lengths, m: int) -> int:
    """Mindestzahl von Vertauschungen (zwei Kästen tauschen ihre Zettel), bis kein Zyklus länger als m ist: Summe über die Zyklen von ceil(L/m) - 1.
    Eine Vertauschung innerhalb eines Zyklus teilt ihn in zwei beliebige Stücke; eine Vertauschung zweier Zyklen verschmilzt sie und hilft nie."""
    return sum(-(-int(length) // m) - 1 for length in lengths)


def swap_cost_batch(perms: np.ndarray, m: int) -> np.ndarray:
    """Dasselbe für viele Anordnungen: je Zyklus einmal, gezählt am Vertreter des Zyklus."""
    lengths, reps = element_cycle_lengths(perms)
    return ((-(-lengths // m) - 1) * reps).sum(axis=1)


def successes_batch(perms: np.ndarray, m: int) -> np.ndarray:
    """Zahl der Gefangenen mit Erfolg je Anordnung: Gefangene, deren Zyklus höchstens m Kästen lang ist."""
    lengths, _ = element_cycle_lengths(perms)
    return (lengths <= m).sum(axis=1)


def swap_contents(q, a: int, b: int) -> list[int]:
    """Kopie von q, in der die Kästen a und b ihre Zettel getauscht haben."""
    out = [int(x) for x in q]
    out[a], out[b] = out[b], out[a]
    return out


def plan_swaps(q, m: int) -> list[tuple[int, int]]:
    """Vertauschungen, die alle Zyklen auf höchstens m Kästen verkürzen: in jedem zu langen Zyklus c_0, c_1, ... tauscht man die Kästen c_0 und c_m,
    wodurch ein Zyklus der Länge m abgespalten wird; das wird wiederholt. Länge der Liste = swap_cost_of_lengths."""
    current = [int(x) for x in q]
    plan: list[tuple[int, int]] = []
    while True:
        long_cycle = next((c for c in cycles_of(current) if len(c) > m), None)
        if long_cycle is None:
            return plan
        a, b = long_cycle[0], long_cycle[m]
        current = swap_contents(current, a, b)
        plan.append((a, b))
