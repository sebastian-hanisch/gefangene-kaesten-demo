"""Exakte Wahrscheinlichkeiten für zufällige Anordnungen (numpy/Standardbibliothek; mit `exact=True` in Brüchen, für die Tests).

Tragende Tatsache (Rekursion über den Zyklus des ersten Elements): In einer gleichverteilten Anordnung von N Kästen hat der Zyklus des ersten Kastens jede Länge
k = 1, ..., N mit Wahrscheinlichkeit 1/N, und die übrigen N - k Kästen sind wieder gleichverteilt angeordnet. Jede Größe, die sich über die Zyklen addiert
(Zahl der Gefangenen in kurzen Zyklen, Kosten der Vertauschungen), folgt daraus durch eine Rekursion über N."""

from __future__ import annotations

import math
from fractions import Fraction

import numpy as np

import gfk_constants as C


def cycle_formula(n: int, m: int, exact: bool = False):
    """1 - Summe_{k=m+1}^{n} 1/k: Wahrscheinlichkeit, dass alle Gefangenen Erfolg haben. Gilt nur, wenn höchstens ein Zyklus länger als m sein kann (2(m+1) > n)."""
    if 2 * (m + 1) <= n:
        raise ValueError(f"die Formel gilt nur für 2(m+1) > n, hier n = {n}, m = {m}")
    one = Fraction(1) if exact else 1.0
    return one - sum(one / k for k in range(m + 1, n + 1))


def max_cycle_cdf(n: int, exact: bool = False) -> list:
    """Liste F mit F[L] = P(kein Zyklus länger als L) für L = 0, ..., n, für eine gleichverteilte Anordnung von n Kästen (Rekursion mit laufender Summe)."""
    zero, one = (Fraction(0), Fraction(1)) if exact else (0.0, 1.0)
    cdf = [zero]
    for length in range(1, n + 1):
        q = [one] + [zero] * n
        for size in range(1, n + 1):
            q[size] = sum(q[max(0, size - length): size], zero) / size    # nur positive Summanden: keine Auslöschung bei winzigen Wahrscheinlichkeiten
        cdf.append(q[n])
    return cdf


def longest_cycle_pmf(n: int, exact: bool = False) -> list:
    """pmf[L] = P(der längste Zyklus hat genau die Länge L), L = 0, ..., n (pmf[0] = 0)."""
    cdf = max_cycle_cdf(n, exact)
    return [cdf[0]] + [cdf[L] - cdf[L - 1] for L in range(1, n + 1)]


def joint_distribution(n: int, m: int, cap: int, exact: bool = False) -> np.ndarray:
    """J[s, c] = P(genau s Gefangene liegen in Zyklen von höchstens m Kästen, und die Vertauschungskosten sind c); c = cap steht für „cap oder mehr“.
    Kosten eines Zyklus der Länge k: ceil(k/m) - 1. Rekursion über den Zyklus des ersten Kastens."""
    zero, one = (Fraction(0), Fraction(1)) if exact else (0.0, 1.0)
    p = []
    first = np.full((n + 1, cap + 1), zero, dtype=object if exact else float)
    first[0, 0] = one
    p.append(first)
    for size in range(1, n + 1):
        acc = np.full((n + 1, cap + 1), zero, dtype=object if exact else float)
        for k in range(1, size + 1):
            prev = p[size - k]
            gain = k if k <= m else 0
            cost = -(-k // m) - 1
            for c in range(cap + 1):
                target = min(cap, c + cost)
                acc[gain:, target] = acc[gain:, target] + prev[: n + 1 - gain, c]
        p.append(acc / size)
    return p[n]


def prob_all_with_swaps(n: int, m: int, swaps: int) -> float:
    """P(alle haben Erfolg), wenn ein Helfer bis zu `swaps` Vertauschungen machen darf und sie einsetzt, wenn sie reichen = P(Kosten <= swaps)."""
    joint = joint_distribution(n, m, swaps + 1)
    return min(1.0, float(joint[:, : swaps + 1].sum()))        # Rundung der Summe darf 1 nicht überschreiten


def successes_pmf_cycle(n: int, m: int, swaps: int = 0) -> np.ndarray:
    """P(genau s Gefangene haben Erfolg), s = 0, ..., n, bei der Zyklus-Strategie. Reichen die Vertauschungen nicht, greift der Helfer nicht ein."""
    joint = joint_distribution(n, m, swaps + 1)
    pmf = joint[:, swaps + 1].copy()                   # Kosten > swaps: Anordnung bleibt
    pmf[n] += joint[:, : swaps + 1].sum()              # Kosten <= swaps: alle haben Erfolg
    return pmf


def successes_pmf_random(n: int, m: int) -> np.ndarray:
    """Binomialverteilung mit Erfolgswahrscheinlichkeit m/n je Gefangenem (unabhängige Zufallswahl der Kästen)."""
    p = m / n
    return np.array([math.comb(n, s) * p ** s * (1 - p) ** (n - s) for s in range(n + 1)])


def prob_all_random(n: int, m: int) -> float:
    return (m / n) ** n


def worst_case_cost(n: int, m: int) -> int:
    """Größte Zahl nötiger Vertauschungen über alle Anordnungen: ceil(n/m) - 1, erreicht von einem einzigen Zyklus der Länge n."""
    return -(-n // m) - 1


def fixed_window_matrix(n: int, m: int) -> np.ndarray:
    """a[i, j] = 1, wenn Gefangener i den Kasten j öffnet: die Kästen i, i+1, ..., i+m-1 (zyklisch)."""
    return (((np.arange(n)[None, :] - np.arange(n)[:, None]) % n) < m).astype(np.int64)


def fixed_window_count(n: int, m: int) -> int:
    """Zahl der Anordnungen, in denen jeder Gefangene mit festen Fenstern seinen Zettel findet = Permanent der Fenster-Matrix.
    Teilmengen-DP: f[S] = Zahl der Zuordnungen der ersten |S| Gefangenen auf die Kästen in S, schichtweise nach |S|."""
    if n > C.EXACT_FIXED_MAX_N:
        raise ValueError(f"exakt nur bis n = {C.EXACT_FIXED_MAX_N}")
    a = fixed_window_matrix(n, m)
    masks = np.arange(1 << n, dtype=np.int64)
    popcount = np.zeros(1 << n, dtype=np.int64)
    for b in range(n):
        popcount += (masks >> b) & 1
    f = np.zeros(1 << n, dtype=np.int64)
    f[0] = 1
    for row in range(n):
        layer = masks[popcount == row + 1]
        for b in range(n):
            if a[row, b]:
                sel = layer[(layer >> b) & 1 == 1]
                f[sel] += f[sel ^ (1 << b)]
    return int(f[(1 << n) - 1])


def fixed_window_probability(n: int, m: int) -> float:
    return fixed_window_count(n, m) / math.factorial(n)
