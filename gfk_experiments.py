"""Experimente E1 bis E4: exakte Reihen (Rekursion und Formel) und Nachspielen mit der Simulation. Verdikte als reine Funktionen (Art, Text)."""

from __future__ import annotations

import math

import numpy as np

import gfk_constants as C
import gfk_exact as X
import gfk_scenario as S
import gfk_simulation as M
from gfk_evaluation import de, pct, prob


# --- E1: wie viele Kästen? ------------------------------------------------------------------------------------------------------------------------
def e1_curve(n: int) -> dict:
    """Exakt für m = 1, ..., n: Zyklus-Strategie (P(kein Zyklus länger als m)) und Zufall ((m/n)^n)."""
    cdf = X.max_cycle_cdf(n)
    ms = list(range(1, n + 1))
    return {"m": ms, "cycle": [cdf[m] for m in ms], "random": [X.prob_all_random(n, m) for m in ms]}


def e1_rows(n: int, shares=C.E1_SHARES) -> list[dict]:
    cdf = X.max_cycle_cdf(n)
    rows = []
    for share in shares:
        m = S.boxes_per_person(n, share)
        rows.append({"share": share, "m": m, "single": m / n, "cycle": cdf[m], "random": X.prob_all_random(n, m)})
    return rows


def e1_live(n: int, runs: int, seed: int, shares=C.E1_SHARES) -> list[dict]:
    """Nachgespielt: Anteil der Läufe mit lauter Erfolgen der Zyklus-Strategie, zufällig gelegte Zettel."""
    rows = []
    for share in shares:
        m = S.boxes_per_person(n, share)
        sim = M.simulate(n, m, C.WARDEN_RANDOM, 0, runs, seed)
        rows.append({"share": share, "m": m, "hits": M.all_succeed_count(sim.s_cycle, n), "runs": runs})
    return rows


def verdict_e1(rows: list[dict], n: int) -> tuple[str, str]:
    by_share = {r["share"]: r for r in rows}
    lo, mid, hi = by_share[40], by_share[50], by_share[60]
    return "info", (f"Bei n = {n} Gefangenen: mit {lo['m']} Kästen je Person (40 %) gewinnt das Team mit {prob(lo['cycle'])}, mit {mid['m']} (50 %) mit {prob(mid['cycle'])}, mit {hi['m']} (60 %) mit {prob(hi['cycle'])}. "
                    f"Es gibt keine Schwelle bei 50 %: die Kurve steigt glatt (bei 25 %: {prob(by_share[25]['cycle'])}, bei 10 %: {prob(by_share[10]['cycle'])}), und bei 100 % ist es sicher. "
                    f"Zufälliges Öffnen bleibt dagegen bei 50 % bei {prob(mid['random'])}.")


# --- E2: wie viele Gefangene? ---------------------------------------------------------------------------------------------------------------------
def e2_rows(ns=C.E2_NS) -> list[dict]:
    return [{"n": n, "m": n // 2, "cycle": X.cycle_formula(n, n // 2), "random": X.prob_all_random(n, n // 2)} for n in ns]


def e2_limit() -> float:
    return 1 - math.log(2)


def e2_live(runs: int, seed: int, ns=C.E2_NS) -> list[dict]:
    rows = []
    for n in ns:
        sim = M.simulate(n, n // 2, C.WARDEN_RANDOM, 0, runs, seed)
        rows.append({"n": n, "hits": M.all_succeed_count(sim.s_cycle, n), "runs": runs})
    return rows


def verdict_e2(rows: list[dict]) -> tuple[str, str]:
    first, last = rows[0], rows[-1]
    limit = e2_limit()
    return "info", (f"Mit n/2 Kästen je Person fällt die Gewinnchance der Zyklus-Strategie von {prob(first['cycle'])} bei n = {first['n']} auf {prob(last['cycle'])} bei n = {last['n']}. "
                    f"Sie bleibt dabei über dem Grenzwert 1 − ln 2 = {pct(limit, 1)} und liegt bei n = {last['n']} nur {de(100 * (last['cycle'] - limit), 2)} Prozentpunkte darüber; "
                    f"zufälliges Öffnen fällt in derselben Reihe auf {prob(last['random'])}.")


# --- E3: der Wärter ---------------------------------------------------------------------------------------------------------------------------------
def e3_exact(n: int, share: int) -> dict:
    """P(alle haben Erfolg) je Szenario und Strategie, ohne Helfer, aus exact_table der Hauptansicht."""
    from gfk_evaluation import exact_table
    out = {}
    for warden in C.WARDENS:
        table = exact_table(S.Settings(n=n, share=share, warden=warden, swaps=0))
        out[warden] = {name: table[name].p_all for name in C.STRATEGIES}
    return out


def e3_live(n: int, share: int, runs: int, seed: int) -> dict:
    m = S.boxes_per_person(n, share)
    out = {}
    for warden in C.WARDENS:
        sim = M.simulate(n, m, warden, 0, runs, seed)
        out[warden] = {C.STRAT_RANDOM: M.all_succeed_count(sim.s_random, n), C.STRAT_FIXED: M.all_succeed_count(sim.s_fixed, n), C.STRAT_CYCLE: M.all_succeed_count(sim.s_cycle, n), "runs": runs}
    return out


def verdict_e3(table: dict, n: int, m: int) -> tuple[str, str]:
    z, w, u = table[C.WARDEN_RANDOM], table[C.WARDEN_KNOWS], table[C.WARDEN_SECRET]
    if m >= n:
        return "info", "Bei m = n sind alle Kästen offen: kein Wärter kann etwas ändern (alles 100 %)."
    return "info", (f"Bei n = {n} und m = {m} Kästen: Zyklus-Strategie gegen zufällige Zettel {prob(z[C.STRAT_CYCLE])}, gegen den Wärter, der sie kennt, {prob(w[C.STRAT_CYCLE])}, "
                    f"mit geheimer gemeinsamer Umnummerierung der Kästen wieder {prob(u[C.STRAT_CYCLE])} (so groß wie bei zufällig gelegten Zetteln, und zwar gegen jede Anordnung des Wärters). "
                    f"Zufälliges Öffnen ist in allen drei Fällen {prob(w[C.STRAT_RANDOM])}: ohne feste Regel gibt es nichts auszunutzen, aber sie bleibt hinter der Zyklus-Strategie bei zufälligen Zetteln zurück.")


# --- E4: ein Helfer vertauscht vorab ---------------------------------------------------------------------------------------------------------------
def e4_rows(n: int, shares=C.E4_SHARES, ks=tuple(range(C.SWAPS_MAX + 1))) -> list[dict]:
    rows = []
    for share in shares:
        m = S.boxes_per_person(n, share)
        joint = X.joint_distribution(n, m, max(ks) + 1)
        cum = np.cumsum(joint.sum(axis=0))
        rows.append({"share": share, "m": m, "p": [float(cum[k]) for k in ks], "worst": X.worst_case_cost(n, m)})
    return rows


def e4_live(n: int, runs: int, seed: int, shares=C.E4_SHARES) -> list[dict]:
    rows = []
    for share in shares:
        m = S.boxes_per_person(n, share)
        sim = M.simulate(n, m, C.WARDEN_RANDOM, 0, runs, seed)
        rows.append({"share": share, "m": m, "hits": [int((sim.cost <= k).sum()) for k in range(C.SWAPS_MAX + 1)], "runs": runs})
    return rows


def verdict_e4(rows: list[dict], n: int) -> tuple[str, str]:
    by_share = {r["share"]: r for r in rows}
    half, forty = by_share[50], by_share[40]
    quarter = by_share[25]
    return "info", (f"Bei n = {n} Gefangenen: mit {half['m']} Kästen je Person (50 %) gewinnt das Team ohne Eingriff mit {prob(half['p'][0])} und mit einer einzigen Vertauschung mit {prob(half['p'][1])}. "
                    f"Mit {forty['m']} Kästen (40 %) sind es {prob(forty['p'][0])}, {prob(forty['p'][1])} und {prob(forty['p'][2])} bei 0, 1 und 2 Vertauschungen; "
                    f"mit {quarter['m']} Kästen (25 %) {prob(quarter['p'][0])}, {prob(quarter['p'][1])}, {prob(quarter['p'][2])} und {prob(quarter['p'][3])} bei 0 bis 3. "
                    f"Eine Vertauschung teilt einen Zyklus in zwei Stücke; ein Zyklus der Länge L braucht ⌈L/m⌉ − 1 davon.")
