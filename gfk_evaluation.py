"""Kennzahlen, Formate und Verdikte der Hauptansicht. Verdikte sind reine Funktionen (Art, Text); die App ruft getattr(st, Art)(Text)."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

import gfk_constants as C
import gfk_cycles as Y
import gfk_exact as X
import gfk_scenario as S
import gfk_simulation as M

_SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


# --- Formate (deutsch: Dezimalkomma, Tausenderpunkt) -------------------------------------------------------------------------------------------------
def de(x: float, nd: int = 1) -> str:
    """Zahl mit Dezimalkomma und echtem Minuszeichen."""
    s = f"{x:.{nd}f}".replace(".", ",")
    if s.startswith("-") and float(s.replace(",", ".")) == 0:
        s = s[1:]
    return s.replace("-", "−")


def thousands(x: float) -> str:
    return f"{round(x):,}".replace(",", ".")


def sci(x: float, digits: int = 1) -> str:
    """7,9·10⁻³¹ für sehr kleine Wahrscheinlichkeiten."""
    if x == 0:
        return "0"
    exponent = math.floor(math.log10(x))
    mantissa = x / 10 ** exponent
    if round(mantissa, digits) >= 10:
        mantissa, exponent = mantissa / 10, exponent + 1
    return f"{de(mantissa, digits)}·10{str(exponent).translate(_SUP)}"


def pct(p: float, nd: int = 1) -> str:
    return f"{de(100 * p, nd)} %"


def prob(p: float | None) -> str:
    """Wahrscheinlichkeit lesbar: 0 und 1 knapp, ab 0,1 % in Prozent, darunter als Zehnerpotenz."""
    if p is None:
        return "nicht gerechnet"
    if p <= 0:
        return "0 %"
    if p >= 1 - 1e-12:
        return "100 %"
    if p >= 0.01:
        return pct(p, 1)
    if p >= 0.001:
        return pct(p, 2)
    return sci(p)


def boxes_text(m: int, n: int) -> str:
    return f"{m} von {n} Kästen"


# --- Exakte Tabelle -----------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Exact:
    """Exakte Werte einer Strategie: P(alle haben Erfolg), Einzelchance (mittlerer Anteil der Erfolgreichen), oder None, wenn nicht gerechnet."""
    p_all: float | None
    p_single: float | None


def exact_table(s: S.Settings) -> dict[str, Exact]:
    n, m, k = s.n, S.m_of(s), s.swaps
    out = {C.STRAT_RANDOM: Exact(X.prob_all_random(n, m), m / n)}
    if s.warden == C.WARDEN_KNOWS:
        fixed_ok = 1.0 if m == n else 0.0
        cycle_ok = 1.0 if X.worst_case_cost(n, m) <= k else 0.0
        out[C.STRAT_FIXED] = Exact(fixed_ok, fixed_ok)
        out[C.STRAT_CYCLE] = Exact(cycle_ok, cycle_ok)
        return out
    fixed = X.fixed_window_probability(n, m) if n <= C.EXACT_FIXED_MAX_N else None
    out[C.STRAT_FIXED] = Exact(fixed, m / n)
    pmf = X.successes_pmf_cycle(n, m, k)
    out[C.STRAT_CYCLE] = Exact(min(1.0, float(pmf[n])), min(1.0, float((pmf * np.arange(n + 1)).sum() / n)))
    return out


def exact_pmf_cycle(s: S.Settings) -> np.ndarray:
    """Verteilung der Zahl erfolgreicher Gefangener bei der Zyklus-Strategie (im Wärter-Fall ohne Umnummerierung ein einziger Wert)."""
    n, m, k = s.n, S.m_of(s), s.swaps
    if s.warden == C.WARDEN_KNOWS:
        pmf = np.zeros(n + 1)
        pmf[n if X.worst_case_cost(n, m) <= k else 0] = 1.0
        return pmf
    return X.successes_pmf_cycle(n, m, k)


# --- Hauptansicht -------------------------------------------------------------------------------------------------------------------------------------
@dataclass(frozen=True)
class Example:
    """Eine Anordnung (aus Sicht des Teams) mit ihren Zyklen und dem Plan des Helfers."""
    q: tuple[int, ...]
    cycles: tuple[tuple[int, ...], ...]
    lengths: tuple[int, ...]
    cost: int
    plan: tuple[tuple[int, int], ...]     # Vertauschungen, die der Helfer machen würde (leer, wenn er nicht eingreift)
    after: tuple[int, ...]                # Anordnung nach dem Eingriff


@dataclass(frozen=True)
class MainView:
    settings: S.Settings
    m: int
    exact: dict
    sim: M.SimResult
    pmf_cycle: np.ndarray
    pmf_random: np.ndarray
    hist_fixed: np.ndarray
    example: Example
    longest_pmf: tuple


def make_example(s: S.Settings) -> Example:
    n, m = s.n, S.m_of(s)
    if s.warden == C.WARDEN_RANDOM:
        q = M.random_arrangements(S.stream_seed(s.seed, "example"), 1, n)[0]
    else:
        q = M.adversary_against_cycle(n)
        if s.warden == C.WARDEN_SECRET:
            rho = M.random_arrangements(S.stream_seed(s.seed, "example-rho"), 1, n)
            q = M.team_view(q[None, :], rho)[0]
    q = [int(x) for x in q]
    lengths = Y.cycle_lengths(q)
    cost = Y.swap_cost_of_lengths(lengths, m)
    plan = tuple(Y.plan_swaps(q, m)) if 0 < cost <= s.swaps else ()
    after = list(q)
    for a, b in plan:
        after = Y.swap_contents(after, a, b)
    return Example(tuple(q), tuple(tuple(c) for c in Y.cycles_of(q)), tuple(lengths), cost, plan, tuple(after))


def analyse(s: S.Settings) -> MainView:
    n, m = s.n, S.m_of(s)
    sim = M.simulate(n, m, s.warden, s.swaps, s.runs, s.seed)
    hist_fixed = np.bincount(sim.s_fixed, minlength=n + 1) / s.runs
    return MainView(s, m, exact_table(s), sim, exact_pmf_cycle(s), X.successes_pmf_random(n, m), hist_fixed, make_example(s), tuple(X.longest_cycle_pmf(n)))


def sim_all(view: MainView, strategy: str) -> int:
    arr = {C.STRAT_RANDOM: view.sim.s_random, C.STRAT_FIXED: view.sim.s_fixed, C.STRAT_CYCLE: view.sim.s_cycle}[strategy]
    return M.all_succeed_count(arr, view.settings.n)


def sim_single(view: MainView, strategy: str) -> float:
    arr = {C.STRAT_RANDOM: view.sim.s_random, C.STRAT_FIXED: view.sim.s_fixed, C.STRAT_CYCLE: view.sim.s_cycle}[strategy]
    return float(arr.mean() / view.settings.n)


def table_rows(view: MainView) -> list[dict]:
    """Zeilen der Strategientabelle: exakte Werte neben der Simulation (Treffer von Läufen)."""
    runs = view.sim.runs
    rows = []
    for name in C.STRATEGIES:
        ex = view.exact[name]
        hits = sim_all(view, name)
        rows.append({
            "Strategie": name,
            "Einzelchance (exakt)": None if ex.p_single is None else 100 * ex.p_single,
            "Einzelchance (Simulation)": 100 * sim_single(view, name),
            "Alle haben Erfolg (exakt)": prob(ex.p_all),
            "Alle haben Erfolg (Simulation)": f"{thousands(hits)} von {thousands(runs)} Läufen",
        })
    return rows


# --- Verdikte -----------------------------------------------------------------------------------------------------------------------------------------
def verdict_hook(view: MainView) -> tuple[str, str]:
    """Kernfrage: gleiche Einzelchance, ganz verschiedene gemeinsame Chance. Jeder Zweig nennt seine Voraussetzung (Wärter, Helfer) im Text."""
    s, m, n = view.settings, view.m, view.settings.n
    ex = view.exact
    r, f, c = ex[C.STRAT_RANDOM], ex[C.STRAT_FIXED], ex[C.STRAT_CYCLE]
    hits_fixed = thousands(sim_all(view, C.STRAT_FIXED))
    fixed_txt = (f"mit {prob(f.p_all)}" if f.p_all is not None
                 else f"in {thousands(s.runs)} Läufen {hits_fixed} Mal (exakt nur bis n = {C.EXACT_FIXED_MAX_N} gerechnet)")
    if m == n:
        return "info", f"Jeder darf alle {n} Kästen öffnen: dann findet jeder seinen Zettel, bei jeder Strategie (100 %). Es gibt nichts zu koordinieren."
    if s.warden == C.WARDEN_KNOWS:
        need = X.worst_case_cost(n, m)
        if c.p_all == 1.0:
            cycle_txt = (f"Die Zyklus-Strategie gelingt trotzdem (alle: 100 %), weil der Helfer mit seinen {s.swaps} Vertauschungen den einen langen Zyklus aus {n} Kästen "
                         f"in Stücke von höchstens {m} Kästen teilt (nötig sind {need}).")
        else:
            cycle_txt = f"Die Zyklus-Strategie scheitert ebenso (alle: 0 %): ein einziger Zyklus aus {n} Kästen ist für jeden zu lang, und die {s.swaps} Vertauschungen des Helfers reichen nicht (nötig sind {need})."
        return ("info" if c.p_all == 1.0 else "warning"), (f"Der Wärter kennt die Strategie und legt die Zettel entsprechend. Gegen die Zufalls-Strategie hilft ihm das nichts (alle: {prob(r.p_all)}; die Wahl der Kästen kennt er nicht). "
                           f"Feste Kästen scheitern sicher (alle: {prob(f.p_all)}). {cycle_txt}")
    base = f"Jeder Gefangene findet seinen Zettel mit Wahrscheinlichkeit m/n = {boxes_text(m, n)} = {pct(m / n, 1)}"
    head = base + (", bei allen drei Strategien. " if s.swaps == 0 else " bei Zufall und festen Kästen; bei der Zyklus-Strategie hebt der Helfer sie auf " + pct(c.p_single, 1) + ". ")
    together = f"Gemeinsam gelingt es bei Zufall mit {prob(r.p_all)}, bei der Zyklus-Strategie mit {prob(c.p_all)}, bei festen Kästen {fixed_txt}. "
    link = (f"Bei der Zyklus-Strategie hängen die Erfolge zusammen: scheitert einer, scheitern alle {m + 1} oder mehr in seinem Zyklus mit ihm." if s.swaps == 0
            else f"Ein Helfer darf vor Beginn bis zu {s.swaps} Mal die Zettel zweier Kästen vertauschen (nur für die Zyklus-Strategie gerechnet).")
    prefix = "Der Wärter kennt die Strategie, aber das Team hat die Kästen geheim umnummeriert: sein Wissen nützt ihm nichts, es gilt wie bei zufälligen Zetteln. " if s.warden == C.WARDEN_SECRET else ""
    kind = "success" if c.p_all >= 0.99 else ("info" if c.p_all >= 0.01 else "warning")
    return kind, prefix + head + together + link


def verdict_cycles(view: MainView) -> tuple[str, str]:
    """Zu den Zyklen des gezeigten Beispiels: längster Zyklus gegen m, mit der Nennung der Gefangenen, die scheitern."""
    ex, m, n = view.example, view.m, view.settings.n
    longest = max(ex.lengths)
    failing = sum(length for length in ex.lengths if length > m)
    if ex.plan:
        a, b = ex.plan[0]
        more = f" und {len(ex.plan) - 1} weitere" if len(ex.plan) > 1 else ""
        return "success", (f"Der längste Zyklus hat {longest} Kästen und ist damit länger als m = {m}: ohne Helfer scheitern {failing} Gefangene. Der Helfer vertauscht die Zettel in Kasten {a + 1} und Kasten {b + 1}{more}; "
                           f"danach hat jeder Zyklus höchstens {m} Kästen und alle {n} haben Erfolg.")
    if longest <= m:
        return "success", f"Der längste Zyklus hat {longest} Kästen, höchstens m = {m}: alle {n} Gefangenen haben Erfolg."
    return "warning", f"Der längste Zyklus hat {longest} Kästen, mehr als m = {m}: die {failing} Gefangenen in zu langen Zyklen scheitern, die übrigen {n - failing} haben Erfolg."


def verdict_trace(opened: list[tuple[int, int]], found: bool, prisoner: int, m: int) -> tuple[str, str]:
    """Weg eines einzelnen Gefangenen (Nummern ab 1)."""
    if found:
        return "success", f"Gefangener {prisoner + 1} findet seinen Zettel im {len(opened)}. Kasten (Kasten {opened[-1][0] + 1}), höchstens m = {m} waren erlaubt."
    return "warning", f"Gefangener {prisoner + 1} hat nach {len(opened)} Kästen seinen Zettel nicht gefunden (erlaubt: m = {m}): sein Zyklus ist länger als m."
