"""Exakte Rekursionen und Formeln: Handrechnung auf Mini-Fällen, Summenprobe, Grenzfälle."""

import math
from fractions import Fraction

import numpy as np
import pytest

import gfk_exact as X


def test_cdf_by_hand():
    """F_1(2) = 1/2 (nur die Identität); F_1(3) = 1/6; F_2(3) = 4/6 = 2/3 (alle außer den beiden 3-Zyklen); F_2(4) = (1/4)(F_2(3) + F_2(2)) = (1/4)(2/3 + 1) = 5/12."""
    assert X.max_cycle_cdf(2, True)[1] == Fraction(1, 2)
    assert X.max_cycle_cdf(3, True)[1] == Fraction(1, 6)
    assert X.max_cycle_cdf(3, True)[2] == Fraction(2, 3)
    assert X.max_cycle_cdf(4, True)[2] == Fraction(5, 12)


def test_formula_by_hand_and_n8():
    assert X.cycle_formula(4, 2, True) == 1 - Fraction(1, 3) - Fraction(1, 4) == Fraction(5, 12)
    assert X.cycle_formula(8, 4, True) == Fraction(307, 840)
    assert X.cycle_formula(100, 50) == pytest.approx(0.3118278206898048, rel=1e-12)


def test_formula_rejects_m_below_half():
    with pytest.raises(ValueError):
        X.cycle_formula(8, 3)


def test_cdf_ends_at_one_and_is_monotone():
    cdf = X.max_cycle_cdf(30)
    assert cdf[30] == pytest.approx(1.0) and all(a <= b for a, b in zip(cdf, cdf[1:]))
    pmf = X.longest_cycle_pmf(30)
    assert sum(pmf) == pytest.approx(1.0) and min(pmf) >= 0


def test_longest_cycle_pmf_above_half_is_one_over_L():
    """Für L > n/2 hat der Anteil 1/L aller Anordnungen einen Zyklus der Länge L und keinen längeren (Beweis im Expander)."""
    pmf = X.longest_cycle_pmf(10, True)
    for length in range(6, 11):
        assert pmf[length] == Fraction(1, length)


def test_joint_distribution_sums_to_one_and_its_cost_marginal_matches_the_cdf():
    j = X.joint_distribution(7, 3, 3, True)
    assert j.sum() == 1
    assert j[:, 0].sum() == X.max_cycle_cdf(7, True)[3]           # Kosten 0 = kein Zyklus länger als m


def test_joint_distribution_cost_zero_means_everyone_succeeds():
    j = X.joint_distribution(6, 3, 2, True)
    assert all(j[s, 0] == 0 for s in range(6)) and j[6, 0] > 0
    assert all(j[6, c] == 0 for c in (1, 2))


def test_successes_pmf_random_by_hand():
    assert list(X.successes_pmf_random(2, 1)) == [0.25, 0.5, 0.25]
    assert X.prob_all_random(100, 50) == pytest.approx(0.5 ** 100)


def test_successes_pmf_cycle_with_helper_by_hand():
    """n = 2, m = 1: die Anordnungen (0 1) und (1 0). Identität: beide Erfolg (s = 2). Vertauschung: ein Zyklus der Länge 2, beide scheitern (s = 0), Kosten 1.
    Ohne Helfer also P(s = 0) = P(s = 2) = 1/2; mit einer Vertauschung ist der Helfer immer erfolgreich: P(s = 2) = 1."""
    assert list(X.successes_pmf_cycle(2, 1, 0)) == [0.5, 0.0, 0.5]
    assert list(X.successes_pmf_cycle(2, 1, 1)) == [0.0, 0.0, 1.0]


def test_mean_successes_of_the_cycle_strategy_is_m():
    for n, m in ((10, 5), (10, 3), (30, 7)):
        pmf = X.successes_pmf_cycle(n, m)
        assert float((pmf * np.arange(n + 1)).sum()) == pytest.approx(m, rel=1e-9)


def test_worst_case_cost():
    assert X.worst_case_cost(8, 4) == 1 and X.worst_case_cost(100, 25) == 3 and X.worst_case_cost(9, 4) == 2 and X.worst_case_cost(5, 5) == 0


def test_fixed_window_by_hand():
    """n = 3, m = 1: jeder öffnet nur Kasten i, nur die Identität gewinnt (Permanent 1). m = 3: alle 6. n = 4, m = 2: die 0/1-Matrix hat zwei Perfect Matchings
    (alle Gefangenen auf den eigenen Kasten, oder alle auf den nächsten), Permanent 2."""
    assert X.fixed_window_count(3, 1) == 1 and X.fixed_window_count(3, 3) == 6 and X.fixed_window_count(4, 2) == 2
    assert X.fixed_window_probability(4, 2) == pytest.approx(2 / math.factorial(4))


def test_fixed_window_rejects_large_n():
    with pytest.raises(ValueError):
        X.fixed_window_count(21, 10)
