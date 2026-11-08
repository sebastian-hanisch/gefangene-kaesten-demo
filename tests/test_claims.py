"""JEDE Zahl der README und der festen App-Texte wird hier nachgerechnet (DEMO-PLAYBOOK §4, §11a). Zählungen statt Urteilswörter, Voraussetzungen im Namen des Tests."""

import itertools
import math
from fractions import Fraction
from pathlib import Path

import pytest

import gfk_constants as C
import gfk_cycles as Y
import gfk_evaluation as ev
import gfk_exact as X
import gfk_experiments as XP
import gfk_scenario as S
import gfk_simulation as M

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
APP = (ROOT / "app.py").read_text(encoding="utf-8")


def cdf100():
    return X.max_cycle_cdf(100)


# --- Der Hook ----------------------------------------------------------------------------------------------------------------------------------
def test_claim_100_prisoners_50_boxes_cycle_strategy_wins_with_31_2_percent():
    assert ev.pct(float(X.cycle_formula(100, 50)), 1) == "31,2 %" and float(X.cycle_formula(100, 50)) == pytest.approx(0.3118278206898048, rel=1e-12)
    assert cdf100()[50] == pytest.approx(0.3118278206898048, rel=1e-12)        # Rekursion, anderer Rechenweg als die Formel
    assert "31,2 %" in README and "31,2 %" in APP


def test_claim_random_boxes_give_7_9_times_ten_to_minus_31_for_100_prisoners():
    assert ev.sci(0.5 ** 100) == "7,9·10⁻³¹" and "7,9·10⁻³¹" in README


def test_claim_every_strategy_gives_the_single_prisoner_50_percent_at_n_100_m_50():
    ex = ev.exact_table(S.Settings())
    assert [e.p_single for e in ex.values()] == pytest.approx([0.5, 0.5, 0.5], abs=1e-12)
    assert "50 %" in README


def test_claim_individual_chance_is_m_over_n_by_enumeration_for_n_7():
    """Aufzählung aller 5040 Anordnungen, jedes m: Anteil der Gefangenen mit Erfolg = m/7 (README: Einzelchance m/n)."""
    n = 7
    perms = list(itertools.permutations(range(n)))
    for m in range(1, n + 1):
        total = sum(sum(Y.follow_boxes(p, i, m)[1] for i in range(n)) for p in perms)
        assert Fraction(total, len(perms) * n) == Fraction(m, n)


def test_claim_cycle_strategy_failures_come_as_groups_of_at_least_m_plus_1_with_probability_1_over_L():
    """n = 8, m = 4, Aufzählung: genau L Gefangene scheitern mit Wahrscheinlichkeit 1/L (L = 5, 6, 7, 8), sonst keiner (307/840)."""
    n, m = 8, 4
    counts = {}
    for p in itertools.permutations(range(n)):
        failed = n - sum(length for length in Y.cycle_lengths(p) if length <= m)
        counts[failed] = counts.get(failed, 0) + 1
    total = math.factorial(n)
    assert {k: Fraction(v, total) for k, v in counts.items()} == {0: Fraction(307, 840), 5: Fraction(1, 5), 6: Fraction(1, 6), 7: Fraction(1, 7), 8: Fraction(1, 8)}


# --- Grenzwert ---------------------------------------------------------------------------------------------------------------------------------
def test_claim_limit_one_minus_ln_2_is_30_7_percent_and_n100_exceeds_it_by_0_50_points():
    limit = 1 - math.log(2)
    assert ev.pct(limit, 1) == "30,7 %"
    gap = float(X.cycle_formula(100, 50)) - limit
    assert ev.de(100 * gap, 2) == "0,50"
    assert "30,7 %" in README and "0,50 Prozentpunkte" in README


def test_claim_the_value_at_m_equals_n_over_2_decreases_toward_the_limit_for_all_even_n_up_to_200():
    values = [float(X.cycle_formula(n, n // 2)) for n in range(2, 201, 2)]
    limit = 1 - math.log(2)
    assert all(a > b for a, b in zip(values, values[1:])) and min(values) > limit and values[0] == 0.5
    assert ev.pct(values[0], 1) == "50,0 %"


def test_claim_small_cases_n8_and_n10_and_the_count_of_the_n8_preset():
    assert X.cycle_formula(8, 4, True) == Fraction(307, 840) and ev.pct(307 / 840, 1) == "36,5 %"
    assert ev.pct(float(X.cycle_formula(10, 5)), 1) == "35,4 %"
    assert Fraction(307, 840) * math.factorial(8) == 14736
    perms = itertools.permutations(range(8))
    assert sum(1 for p in perms if max(Y.cycle_lengths(p)) <= 4) == 14736 and "14.736" in README and "14.736" in C.PRESET_HELP["Zum Nachzählen: 8 Gefangene"]


def test_claim_expected_number_of_cycles_for_100_boxes_is_5_19():
    h = sum(1 / k for k in range(1, 101))
    assert ev.de(h, 2) == "5,19"


# --- Wie viele Kästen --------------------------------------------------------------------------------------------------------------------------
def test_claim_n100_other_box_counts():
    cdf = cdf100()
    assert [ev.prob(cdf[m]) for m in (40, 60, 49, 51, 25, 10)] == ["13,5 %", "49,2 %", "29,2 %", "33,1 %", "0,57 %", "1,3·10⁻¹⁰"]
    for text in ("13,5 %", "49,2 %", "29,2 %", "33,1 %", "0,57 %", "1,3·10⁻¹⁰"):
        assert text in README, text
    assert cdf[1] == pytest.approx(1 / math.factorial(100), rel=1e-9)         # m = 1: nur die Identität gewinnt


# --- Feste Kästen ------------------------------------------------------------------------------------------------------------------------------
def test_claim_fixed_windows_beat_random_by_the_factors_1_3_1_7_1_8():
    cases = {4: (Fraction(1, 12), Fraction(1, 16), "1,3"), 8: (Fraction(11, 1680), Fraction(1, 256), "1,7"), 20: (None, Fraction(1, 2 ** 20), "1,8")}
    for n, (expect, rand, factor) in cases.items():
        count = X.fixed_window_count(n, n // 2)
        p = Fraction(count, math.factorial(n))
        if expect is not None:
            assert p == expect
        assert ev.de(float(p / rand), 1) == factor, n
    assert X.fixed_window_count(20, 10) == 4152609019392
    assert ev.pct(11 / 1680, 2) == "0,65 %" and ev.sci(X.fixed_window_probability(20, 10)) == "1,7·10⁻⁶" and ev.sci(0.5 ** 20) == "9,5·10⁻⁷"
    for text in ("11/1680", "0,65 %", "1,7·10⁻⁶", "9,5·10⁻⁷"):
        assert text in README, text


# --- Wärter und Umnummerierung -------------------------------------------------------------------------------------------------------------------
def test_claim_warden_who_knows_the_strategy_wins_always_when_m_below_n():
    for n, m in ((8, 4), (100, 50), (100, 99)):
        assert max(Y.cycle_lengths(list(M.adversary_against_cycle(n)))) == n > m
    t = XP.e3_exact(100, 50)
    assert t[C.WARDEN_KNOWS]["Zyklus-Strategie"] == 0.0 and t[C.WARDEN_SECRET]["Zyklus-Strategie"] == pytest.approx(0.3118278206898048, rel=1e-9)


def test_claim_secret_renaming_of_the_boxes_gives_307_over_840_averaged_over_all_8_factorial_renamings():
    q = list(M.adversary_against_cycle(8))
    wins = sum(1 for rho in itertools.permutations(range(8)) if max(Y.cycle_lengths([q[r] for r in rho])) <= 4)
    assert Fraction(wins, math.factorial(8)) == Fraction(307, 840) and "40.320" in README


# --- Helfer ------------------------------------------------------------------------------------------------------------------------------------
def test_claim_one_swap_always_suffices_for_n8_m4_by_enumeration_of_all_40320_arrangements():
    perms = list(itertools.permutations(range(8)))
    assert len(perms) == 40320 and all(Y.swap_cost_of_lengths(Y.cycle_lengths(p), 4) <= 1 for p in perms)
    # Gegenprobe ohne die Kostenformel: wirklich alle 28 Vertauschungen ausprobieren
    for p in perms:
        if max(Y.cycle_lengths(p)) > 4:
            assert any(max(Y.cycle_lengths(Y.swap_contents(p, i, j))) <= 4 for i in range(8) for j in range(i + 1, 8))


def test_claim_one_swap_suffices_for_every_n_up_to_100_when_m_is_at_least_half_n_rounded_up():
    for n in range(2, 101):
        m = S.boxes_per_person(n, 50)
        assert m == -(-n // 2)
        assert X.prob_all_with_swaps(n, m, 1) == pytest.approx(1.0, abs=1e-12), n
    assert "⌈*L*/2⌉ und ⌊*L*/2⌋" in README                # die Beweisidee steht im Text: ein Zyklus der Länge L <= n wird in zwei Stücke von höchstens ceil(n/2) geteilt


def test_claim_helper_numbers_for_n100():
    rows = {r["share"]: r for r in XP.e4_rows(100)}
    assert [ev.prob(p) for p in rows[40]["p"][:3]] == ["13,5 %", "73,4 %", "100 %"]
    assert [ev.prob(p) for p in rows[25]["p"]] == ["0,57 %", "10,4 %", "54,5 %", "100 %"]
    for text in ("73,4 %", "10,4 %", "54,5 %"):
        assert text in README, text


def test_claim_odd_n99_m49_one_swap_gives_98_99_percent():
    assert ev.pct(X.prob_all_with_swaps(99, 49, 1), 2) == "98,99 %" and "98,99 %" in README
    assert X.prob_all_with_swaps(99, 50, 1) == pytest.approx(1.0, abs=1e-12)


def test_claim_swap_cost_formula_is_exact_for_n_up_to_6_all_m_up_to_3_swaps():
    """Die Mindestzahl der Vertauschungen = Summe (ceil(L/m) - 1), gegen die Breitensuche über alle Vertauschungsfolgen (README: Kosten-Formel)."""
    def search(p, m, kmax):
        n, level = len(p), {tuple(p)}
        for k in range(kmax + 1):
            if any(max(Y.cycle_lengths(q)) <= m for q in level):
                return k
            level = {tuple(Y.swap_contents(q, i, j)) for q in level for i in range(n) for j in range(i + 1, n)}
        return None
    for n in range(2, 7):
        for p in itertools.permutations(range(n)):
            for m in range(1, n + 1):
                cost = Y.swap_cost_of_lengths(Y.cycle_lengths(p), m)
                assert search(p, m, 3) == (cost if cost <= 3 else None)


# --- Optimalität -------------------------------------------------------------------------------------------------------------------------------
def test_claim_best_team_for_n3_and_n4_equals_the_cycle_strategy():
    from test_oracle_optimality import best_team
    assert best_team(3, 1) == Fraction(1, 6) and best_team(3, 2) == Fraction(2, 3) and best_team(4, 1) == Fraction(1, 24) and best_team(4, 2) == Fraction(5, 12)
    for text in ("1/6", "2/3", "1/24", "5/12"):
        assert text in README, text


# --- Feste Texte der App -------------------------------------------------------------------------------------------------------------------------
def test_claim_exact_fixed_window_limit_is_n_20_in_app_and_readme():
    assert C.EXACT_FIXED_MAX_N == 20 and "n = 20" in README and "bis n = 20" in APP


def test_claim_first_slider_values_named_in_the_text_exist():
    assert C.N_MAX == 100 and C.SWAPS_MAX == 3 and "0 bis 3" in README
