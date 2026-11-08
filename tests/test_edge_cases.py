"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): n = 1 und n = 2, m = 1 und m = n, ungerade n, Grenzen inklusive."""

from fractions import Fraction

import numpy as np
import pytest

import gfk_constants as C
import gfk_cycles as Y
import gfk_evaluation as ev
import gfk_exact as X
import gfk_experiments as XP
import gfk_scenario as S
import gfk_simulation as M


def test_exactly_two_prisoners():
    """n = 2, m = 1: nur die Identität gewinnt (1/2); m = 2: sicher. Die Formel gilt hier (2(m+1) = 4 > 2)."""
    assert X.cycle_formula(2, 1, True) == X.max_cycle_cdf(2, True)[1] == Fraction(1, 2)
    assert X.max_cycle_cdf(2, True)[2] == 1
    r = M.simulate(2, 1, C.WARDEN_RANDOM, 1, 400, 1)
    assert (r.s_cycle == 2).all()                              # eine Vertauschung genügt immer


def test_single_prisoner_and_single_box():
    """n = 1: ein Kasten, ein Zettel, jeder Gefangene hat Erfolg (der Regler beginnt bei 2, die Kernroutinen vertragen n = 1)."""
    assert Y.cycles_of([0]) == [[0]] and Y.follow_boxes([0], 0, 1) == ([(0, 0)], True)
    assert X.max_cycle_cdf(1, True) == [0, 1]
    q = np.array([[0]])
    assert Y.swap_cost_batch(q, 1)[0] == 0 and Y.successes_batch(q, 1)[0] == 1
    r = M.simulate(1, 1, C.WARDEN_RANDOM, 0, 10, 1)
    assert (r.s_cycle == 1).all() and (r.s_random == 1).all() and (r.s_fixed == 1).all()


def test_m_equals_n_means_certain_success_in_every_scenario():
    for warden in C.WARDENS:
        r = M.simulate(10, 10, warden, 0, 300, 2)
        assert (r.s_cycle == 10).all() and (r.s_fixed == 10).all() and (r.s_random == 10).all()
        table = ev.exact_table(S.Settings(n=10, share=100, warden=warden))
        assert all(e.p_all == 1.0 and e.p_single == 1.0 for e in table.values())


def test_m_equals_one_only_the_identity_wins():
    """m = 1: jeder öffnet nur Kasten i; gewonnen wird nur, wenn die Zettel in Kasten i liegen (die Identität), Wahrscheinlichkeit 1/n!."""
    assert X.max_cycle_cdf(6, True)[1] == Fraction(X.fixed_window_count(6, 1), 720) == Fraction(1, 720)


def test_odd_n_rounding_and_formula_validity():
    """n = 9 und 50 % ergibt 4,5, aufgerundet 5 Kästen. Die Formel gilt für 2(m + 1) > n, also für m = 4 (10 > 9) noch, für m = 3 (8 < 9) nicht mehr."""
    assert S.boxes_per_person(9, 50) == 5
    assert X.cycle_formula(9, 4, True) == X.max_cycle_cdf(9, True)[4]
    with pytest.raises(ValueError):
        X.cycle_formula(9, 3)


def test_odd_n_one_swap_is_not_always_enough_when_m_is_below_half():
    """n = 99, m = 49: ein Zyklus der Länge 99 zerfällt bei einer Vertauschung in 50 + 49, und 50 > 49."""
    assert X.worst_case_cost(99, 49) == 2 and X.prob_all_with_swaps(99, 49, 1) < 1 and X.prob_all_with_swaps(99, 50, 1) == pytest.approx(1.0, abs=1e-12)


def test_share_bounds_are_inclusive():
    for share in (C.SHARE_MIN, C.SHARE_MAX):
        assert 1 <= S.boxes_per_person(C.N_MAX, share) <= C.N_MAX and 1 <= S.boxes_per_person(C.N_MIN, share) <= C.N_MIN


def test_all_zero_columns_do_not_hide_dead_branches():
    """Nullspalten: bei m < n scheitert der Wärter gegen feste Kästen und Zyklus (die Spalte ist 0, weil der Gegner wirkt), die Zufalls-Strategie nicht (sie hat nie lauter Erfolge, aber im Mittel m/n)."""
    r = M.simulate(10, 5, C.WARDEN_KNOWS, 0, 500, 3)
    assert r.s_cycle.sum() == 0 and r.s_fixed.sum() == 0 and r.s_random.sum() > 0


def test_experiment_grids_work_for_the_smallest_and_largest_n():
    for n in (C.N_MIN, 3, C.N_MAX):
        rows = XP.e1_rows(n)
        assert len(rows) == len(C.E1_SHARES) and all(0 <= r["cycle"] <= 1 for r in rows) and rows[-1]["cycle"] == pytest.approx(1.0)
        e4 = XP.e4_rows(n)
        assert all(r["p"] == sorted(r["p"]) for r in e4)                        # mehr Vertauschungen helfen nie weniger
        ex3 = XP.e3_exact(n, 50)
        assert set(ex3) == set(C.WARDENS)


def test_trace_with_m_one_and_a_fixed_point():
    assert Y.follow_boxes([0, 2, 1], 0, 1) == ([(0, 0)], True)
    assert Y.follow_boxes([0, 2, 1], 1, 1) == ([(1, 2)], False)
