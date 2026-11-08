"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): Art, jede Zahl im Text und jeder Zweig; Formate."""

from dataclasses import replace

import gfk_constants as C
import gfk_evaluation as ev
import gfk_experiments as XP
import gfk_scenario as S


def view_with(settings, **exact):
    """Hauptansicht für kleine Einstellungen, mit von Hand gesetzten exakten Werten (Strategie → (p_all, p_single))."""
    view = ev.analyse(S.Settings(**{**dict(n=10, share=50, runs=1000), **settings}))
    table = dict(view.exact)
    for name, (p_all, p_single) in exact.items():
        table[name] = ev.Exact(p_all, p_single)
    return replace(view, exact=table)


# --- Formate -----------------------------------------------------------------------------------------------------------------------------------
def test_formats():
    assert ev.de(1.5, 1) == "1,5" and ev.de(-0.91, 3) == "−0,910" and ev.de(-0.0001, 3) == "0,000" and ev.de(7, 0) == "7"
    assert ev.thousands(1234567) == "1.234.567" and ev.thousands(0) == "0"
    assert ev.pct(0.3118, 1) == "31,2 %" and ev.pct(1.0, 0) == "100 %"
    assert ev.sci(7.8886e-31) == "7,9·10⁻³¹" and ev.sci(1.27e-10) == "1,3·10⁻¹⁰" and ev.sci(0.0) == "0" and ev.sci(9.96e-5) == "1,0·10⁻⁴"


def test_prob_has_five_regimes():
    assert ev.prob(None) == "nicht gerechnet" and ev.prob(0.0) == "0 %" and ev.prob(1.0) == "100 %" and ev.prob(1 - 1e-15) == "100 %"
    assert ev.prob(0.3118) == "31,2 %" and ev.prob(0.0057) == "0,57 %" and ev.prob(0.00099) == "9,9·10⁻⁴"


# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------------
def test_hook_for_random_arrangements_names_equal_single_chances_and_the_coupling():
    v = view_with({}, **{"Zufall": (0.001, 0.5), "Feste Kästen": (0.002, 0.5), "Zyklus-Strategie": (0.25, 0.5)})
    kind, text = ev.verdict_hook(v)
    assert kind == "info"
    assert "m/n = 5 von 10 Kästen = 50,0 %, bei allen drei Strategien." in text
    assert "bei Zufall mit 0,10 %" in text and "bei der Zyklus-Strategie mit 25,0 %" in text and "bei festen Kästen mit 0,20 %" in text
    assert "scheitert einer, scheitern alle 6 oder mehr in seinem Zyklus mit ihm" in text


def test_hook_kind_depends_on_the_cycle_chance():
    assert ev.verdict_hook(view_with({}, **{"Zyklus-Strategie": (0.995, 0.5)}))[0] == "success"
    assert ev.verdict_hook(view_with({}, **{"Zyklus-Strategie": (0.01, 0.5)}))[0] == "info"
    assert ev.verdict_hook(view_with({}, **{"Zyklus-Strategie": (0.009, 0.5)}))[0] == "warning"


def test_hook_names_the_fixed_strategy_count_when_there_is_no_exact_value():
    v = view_with({"n": 24}, **{"Feste Kästen": (None, 0.5)})
    text = ev.verdict_hook(v)[1]
    assert "bei festen Kästen in 1.000 Läufen 0 Mal (exakt nur bis n = 20 gerechnet)" in text


def test_hook_with_helper_names_the_raised_single_chance():
    v = view_with({"swaps": 1}, **{"Zyklus-Strategie": (1.0, 1.0)})
    kind, text = ev.verdict_hook(v)
    assert kind == "success" and "bei Zufall und festen Kästen; bei der Zyklus-Strategie hebt der Helfer sie auf 100,0 %" in text
    assert "bis zu 1 Mal die Zettel zweier Kästen vertauschen" in text


def test_hook_with_secret_renaming_says_the_wardens_knowledge_is_useless():
    text = ev.verdict_hook(view_with({"warden": C.WARDEN_SECRET}))[1]
    assert text.startswith("Der Wärter kennt die Strategie, aber das Team hat die Kästen geheim umnummeriert")


def test_hook_with_warden_and_no_helper_is_a_warning_with_the_cost():
    kind, text = ev.verdict_hook(view_with({"warden": C.WARDEN_KNOWS}))
    assert kind == "warning" and "Die Zyklus-Strategie scheitert ebenso (alle: 0 %)" in text and "reichen nicht (nötig sind 1)" in text
    assert "Feste Kästen scheitern sicher (alle: 0 %)" in text


def test_hook_with_warden_and_enough_helper_swaps():
    kind, text = ev.verdict_hook(view_with({"warden": C.WARDEN_KNOWS, "swaps": 1}))
    assert kind == "info" and "gelingt trotzdem (alle: 100 %)" in text and "mit seinen 1 Vertauschungen" in text and "(nötig sind 1)" in text


def test_hook_with_all_boxes_open_says_nothing_to_coordinate():
    kind, text = ev.verdict_hook(view_with({"share": 100}))
    assert kind == "info" and "alle 10 Kästen öffnen" in text and "nichts zu koordinieren" in text


# --- Zyklen und Weg -----------------------------------------------------------------------------------------------------------------------------
def with_example(view, q):
    """Hauptansicht, deren Beispiel die gegebene Anordnung ist (aus dem Mini-Fall von Hand)."""
    s = view.settings
    return replace(view, example=ev.Example(*_example_fields(q, view.m, s.swaps)))


def _example_fields(q, m, swaps):
    import gfk_cycles as Y
    lengths = Y.cycle_lengths(q)
    cost = Y.swap_cost_of_lengths(lengths, m)
    plan = tuple(Y.plan_swaps(q, m)) if 0 < cost <= swaps else ()
    after = list(q)
    for a, b in plan:
        after = Y.swap_contents(after, a, b)
    return tuple(q), tuple(tuple(c) for c in Y.cycles_of(q)), tuple(lengths), cost, plan, tuple(after)


def test_cycles_verdict_names_the_failing_prisoners(mini):
    v = with_example(view_with({"n": 6, "share": 33}), mini["q"])          # m = round(6 · 0,33) = 2
    assert v.m == 2
    kind, text = ev.verdict_cycles(v)
    assert kind == "warning" and "Der längste Zyklus hat 3 Kästen" in text and "die 3 Gefangenen in zu langen Zyklen scheitern, die übrigen 3 haben Erfolg" in text


def test_cycles_verdict_all_succeed(mini):
    kind, text = ev.verdict_cycles(with_example(view_with({"n": 6, "share": 50}), mini["q"]))                # m = 3
    assert kind == "success" and "höchstens m = 3: alle 6 Gefangenen haben Erfolg" in text


def test_cycles_verdict_with_helper_names_the_two_boxes(mini):
    v = with_example(view_with({"n": 6, "share": 33, "swaps": 1}), mini["q"])
    kind, text = ev.verdict_cycles(v)
    assert kind == "success" and "scheitern 3 Gefangene" in text and "Kasten 1 und Kasten 3" in text      # Plan: c_0 = 0 und c_2 = 2 (ab 1 gezählt)
    assert "alle 6 haben Erfolg" in text


def test_trace_verdict():
    kind, text = ev.verdict_trace([(0, 1), (1, 2), (2, 0)], True, 0, 3)
    assert kind == "success" and "Gefangener 1 findet seinen Zettel im 3. Kasten (Kasten 3), höchstens m = 3" in text
    kind, text = ev.verdict_trace([(0, 1), (1, 2)], False, 0, 2)
    assert kind == "warning" and "Gefangener 1 hat nach 2 Kästen seinen Zettel nicht gefunden (erlaubt: m = 2)" in text


# --- Experimente ----------------------------------------------------------------------------------------------------------------------------------
def test_e1_verdict_names_40_50_60_percent():
    rows = XP.e1_rows(100)
    kind, text = XP.verdict_e1(rows, 100)
    assert kind == "info"
    assert "mit 40 Kästen je Person (40 %) gewinnt das Team mit 13,5 %, mit 50 (50 %) mit 31,2 %, mit 60 (60 %) mit 49,2 %" in text
    assert "bei 25 %: 0,57 %, bei 10 %: 1,3·10⁻¹⁰" in text and "7,9·10⁻³¹" in text


def test_e2_verdict_names_first_last_and_the_distance_to_the_limit():
    rows = XP.e2_rows()
    text = XP.verdict_e2(rows)[1]
    assert "von 50,0 % bei n = 2 auf 31,2 % bei n = 100" in text and "nur 0,50 Prozentpunkte darüber" in text and "1 − ln 2 = 30,7 %" in text


def test_e3_verdict_branches():
    table = {C.WARDEN_RANDOM: {"Zyklus-Strategie": 0.25, "Zufall": 0.01, "Feste Kästen": 0.02},
             C.WARDEN_KNOWS: {"Zyklus-Strategie": 0.0, "Zufall": 0.01, "Feste Kästen": 0.0},
             C.WARDEN_SECRET: {"Zyklus-Strategie": 0.25, "Zufall": 0.01, "Feste Kästen": 0.02}}
    text = XP.verdict_e3(table, 10, 5)[1]
    assert "Zyklus-Strategie gegen zufällige Zettel 25,0 %, gegen den Wärter, der sie kennt, 0 %, mit geheimer gemeinsamer Umnummerierung der Kästen wieder 25,0 %" in text
    assert "in allen drei Fällen 1,0 %" in text
    assert "alle Kästen offen" in XP.verdict_e3(table, 10, 10)[1]


def test_e4_verdict_names_the_numbers():
    text = XP.verdict_e4(XP.e4_rows(100), 100)[1]
    assert "mit 50 Kästen je Person (50 %) gewinnt das Team ohne Eingriff mit 31,2 % und mit einer einzigen Vertauschung mit 100 %" in text
    assert "Mit 40 Kästen (40 %) sind es 13,5 %, 73,4 % und 100 % bei 0, 1 und 2 Vertauschungen" in text
    assert "mit 25 Kästen (25 %) 0,57 %, 10,4 %, 54,5 % und 100 % bei 0 bis 3" in text
