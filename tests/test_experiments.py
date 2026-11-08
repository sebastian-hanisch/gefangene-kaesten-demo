"""Experimente: exakte Reihen gegen Rekursion und Formel, Nachspielen gegen die exakten Werte (feste Seeds, Band), Raster."""

import math

import pytest

import gfk_constants as C
import gfk_exact as X
import gfk_experiments as XP


def inside_band(hits, runs, p, sigmas=4.5):
    return abs(hits / runs - p) <= sigmas * math.sqrt(max(p * (1 - p), 1e-12) / runs) + 1.0 / runs


def test_e1_curve_equals_the_recursion_and_is_monotone():
    curve = XP.e1_curve(40)
    assert curve["m"] == list(range(1, 41)) and curve["cycle"][-1] == pytest.approx(1.0)
    assert all(a <= b for a, b in zip(curve["cycle"], curve["cycle"][1:])) and all(a <= b for a, b in zip(curve["random"], curve["random"][1:]))
    assert curve["cycle"][19] == pytest.approx(float(X.cycle_formula(40, 20)), rel=1e-12)           # m = n/2
    assert curve["random"][19] == pytest.approx(0.5 ** 40)


def test_e1_rows_use_the_grid_and_the_rounding_rule():
    rows = XP.e1_rows(100)
    assert [r["share"] for r in rows] == list(C.E1_SHARES) and [r["m"] for r in rows] == list(C.E1_SHARES)       # n = 100: Anteil in Prozent = m
    assert rows[7]["cycle"] == pytest.approx(0.3118278206898048, rel=1e-12)


def test_e1_live_is_inside_the_band_of_the_exact_values():
    runs = 4000
    live = XP.e1_live(20, runs, 3)
    exact = XP.e1_rows(20)
    assert [r["m"] for r in live] == [r["m"] for r in exact]
    for lv, ex in zip(live, exact):
        assert inside_band(lv["hits"], runs, ex["cycle"]), (lv, ex)


def test_e2_rows_and_limit():
    rows = XP.e2_rows()
    assert [r["n"] for r in rows] == list(C.E2_NS) and all(r["m"] * 2 == r["n"] for r in rows)
    values = [r["cycle"] for r in rows]
    assert values == sorted(values, reverse=True) and min(values) > XP.e2_limit()
    assert XP.e2_limit() == pytest.approx(0.3068528194400547, rel=1e-12)
    assert rows[-1]["cycle"] - XP.e2_limit() == pytest.approx(0.004975001249750088, abs=1e-12)


def test_e2_live_is_inside_the_band():
    runs = 4000
    live = XP.e2_live(runs, 5, ns=(2, 8, 20))
    for lv in live:
        n = lv["n"]
        assert inside_band(lv["hits"], runs, float(X.cycle_formula(n, n // 2))), lv


def test_e3_exact_table_has_the_three_cases():
    t = XP.e3_exact(100, 50)
    assert t[C.WARDEN_RANDOM]["Zyklus-Strategie"] == pytest.approx(0.3118278206898048, rel=1e-9)
    assert t[C.WARDEN_KNOWS]["Zyklus-Strategie"] == 0.0 and t[C.WARDEN_KNOWS]["Feste Kästen"] == 0.0
    assert t[C.WARDEN_SECRET]["Zyklus-Strategie"] == t[C.WARDEN_RANDOM]["Zyklus-Strategie"]
    assert all(t[w]["Zufall"] == pytest.approx(0.5 ** 100) for w in C.WARDENS)


def test_e3_live_matches_the_exact_cases_n8():
    runs = 6000
    live = XP.e3_live(8, 50, runs, 7)
    exact = XP.e3_exact(8, 50)
    for warden in C.WARDENS:
        for strategy in C.STRATEGIES:
            assert inside_band(live[warden][strategy], runs, exact[warden][strategy]), (warden, strategy)
    assert live[C.WARDEN_KNOWS]["Zyklus-Strategie"] == 0 and live[C.WARDEN_KNOWS]["Feste Kästen"] == 0


def test_e4_rows_by_hand_and_branches():
    rows = {r["share"]: r for r in XP.e4_rows(8)}
    assert rows[50]["p"][0] == pytest.approx(307 / 840) and rows[50]["p"][1:] == [1.0, 1.0, 1.0] and rows[50]["worst"] == 1
    assert rows[25]["m"] == 2 and rows[25]["worst"] == 3 and rows[25]["p"][3] == pytest.approx(1.0)
    assert rows[25]["p"][0] < rows[25]["p"][1] < rows[25]["p"][2] < 1.0                # echte Wirkung jeder weiteren Vertauschung (kein toter Zweig)


def test_e4_exact_rows_equal_the_enumeration_n8():
    """n = 8, m = 3 (aus dem Anteil 40 %): P(Kosten <= k) gegen die Aufzählung, hier über die Zyklentyp-Summe der Tests (Kosten = Summe ceil(L/3) - 1)."""
    from fractions import Fraction

    def partitions(n, largest=None):
        largest = n if largest is None else largest
        if n == 0:
            yield []
            return
        for k in range(min(n, largest), 0, -1):
            for rest in partitions(n - k, k):
                yield [k] + rest

    def weight(parts):
        w = Fraction(1)
        for k in set(parts):
            w /= Fraction(k) ** parts.count(k) * math.factorial(parts.count(k))
        return w

    row = {r["share"]: r for r in XP.e4_rows(8)}[40]
    assert row["m"] == 3
    for k in range(4):
        exact = sum(weight(p) for p in partitions(8) if sum(-(-x // 3) - 1 for x in p) <= k)
        assert row["p"][k] == pytest.approx(float(exact), rel=1e-12)


def test_e4_live_is_inside_the_band():
    runs = 4000
    live = XP.e4_live(20, runs, 2)
    exact = {r["share"]: r for r in XP.e4_rows(20)}
    for lv in live:
        for k, hits in enumerate(lv["hits"]):
            assert inside_band(hits, runs, exact[lv["share"]]["p"][k]), (lv["share"], k)
