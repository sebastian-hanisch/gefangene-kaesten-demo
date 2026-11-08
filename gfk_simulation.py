"""Simulation der drei Strategien (numpy, vektorisiert über die Läufe; Zufall nur aus SplitMix64 mit abgeleiteten Strömen, gfk_scenario.stream_seed).

Eine Anordnung ist das Feld q: Kasten j enthält den Zettel q[j] (gfk_cycles). Das Team kennt vorab eine geheime Umbenennung rho der Kästen: der Kasten, den es
„j“ nennt, ist in Wirklichkeit der Kasten rho[j]. Aus Sicht des Teams liegt dann in Kasten j der Zettel q_team[j] = q[rho[j]]. Ohne Umbenennung ist rho die Identität.
Jede Strategie wird auf q_team angewandt; der Wärter legt q (er kennt rho nicht)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import gfk_constants as C
import gfk_cycles as Y
import gfk_scenario as S
from gfk_rng import uniform_block


def random_arrangements(seed: int, runs: int, n: int) -> np.ndarray:
    """`runs` gleichverteilte Anordnungen von n Zetteln (Zeilen): Rangfolge von n·runs Gleichverteilten, 53 Bit, Gleichstände vernachlässigbar."""
    keys = uniform_block(seed, runs * n).reshape(runs, n)
    return np.argsort(keys, axis=1)


def adversary_against_cycle(n: int) -> np.ndarray:
    """Ein einziger Zyklus der Länge n: Kasten j enthält den Zettel j+1 (der letzte den Zettel 0). Jeder Gefangene muss alle n Kästen öffnen."""
    return (np.arange(n) + 1) % n


def adversary_against_fixed(n: int, m: int) -> np.ndarray:
    """Gegen die festen Fenster i, ..., i+m-1: der Zettel i liegt im Kasten i+m (zyklisch), also knapp außerhalb des Fensters (für m < n)."""
    return (np.arange(n) - m) % n


def team_view(q: np.ndarray, rho: np.ndarray | None) -> np.ndarray:
    """q_team[j] = q[rho[j]] zeilenweise; ohne Umbenennung bleibt q."""
    if rho is None:
        return q
    return np.take_along_axis(q, rho, axis=1)


def fixed_window_successes(q: np.ndarray, m: int) -> np.ndarray:
    """Gefangene mit Erfolg bei festen Fenstern: der Zettel i liegt im Kasten inv[i]; Erfolg, wenn (inv[i] - i) mod n < m."""
    n = q.shape[1]
    inv = np.argsort(q, axis=1)
    return (((inv - np.arange(n)[None, :]) % n) < m).sum(axis=1)


@dataclass(frozen=True)
class SimResult:
    n: int
    m: int
    warden: str
    swaps: int
    runs: int
    s_random: np.ndarray      # Gefangene mit Erfolg je Lauf, Strategie Zufall
    s_fixed: np.ndarray       # feste Fenster
    s_cycle: np.ndarray       # Zyklus-Strategie nach dem Eingriff des Helfers
    cost: np.ndarray          # nötige Vertauschungen der Anordnung des Zyklus-Laufs (vor dem Eingriff)
    longest: np.ndarray       # längster Zyklus der Anordnung des Zyklus-Laufs


def simulate(n: int, m: int, warden: str, swaps: int, runs: int, seed: int) -> SimResult:
    """Spielt `runs` Anordnungen durch. Der Zyklus-Lauf: Helfer greift nur ein, wenn die Vertauschungen reichen (0 < Kosten <= swaps), und dann haben alle Erfolg."""
    parts = {k: [] for k in ("s_random", "s_fixed", "s_cycle", "cost", "longest")}
    done, chunk = 0, 0
    while done < runs:
        size = min(C.CHUNK_RUNS, runs - done)
        label = f"{n}|{m}|{warden}|{chunk}"
        rho = None
        if warden == C.WARDEN_RANDOM:
            q_cycle = q_fixed = random_arrangements(S.stream_seed(seed, "perm|" + label), size, n)
        else:
            q_cycle = np.tile(adversary_against_cycle(n), (size, 1))
            q_fixed = np.tile(adversary_against_fixed(n, m), (size, 1))
            if warden == C.WARDEN_SECRET:
                rho = random_arrangements(S.stream_seed(seed, "rho|" + label), size, n)
        q_cycle, q_fixed = team_view(q_cycle, rho), team_view(q_fixed, rho)
        lengths, reps = Y.element_cycle_lengths(q_cycle)
        cost = ((-(-lengths // m) - 1) * reps).sum(axis=1)
        short = (lengths <= m).sum(axis=1)
        helped = (cost > 0) & (cost <= swaps)
        parts["s_cycle"].append(np.where(helped, n, short))
        parts["cost"].append(cost)
        parts["longest"].append(lengths.max(axis=1))
        parts["s_fixed"].append(fixed_window_successes(q_fixed, m))
        draws = uniform_block(S.stream_seed(seed, "rand|" + label), size * n).reshape(size, n)
        parts["s_random"].append((draws < m / n).sum(axis=1))
        done += size
        chunk += 1
    return SimResult(n, m, warden, swaps, runs, **{k: np.concatenate(v) for k, v in parts.items()})


def all_succeed_count(s: np.ndarray, n: int) -> int:
    return int((s == n).sum())
