"""Simulation: Anordnungen, Gegner, Umbenennung, Zweige (jede Variante weicht von der Nachbarvariante ab) und Bänder gegen die exakten Werte (feste Seeds)."""

import math

import numpy as np
import pytest

import gfk_constants as C
import gfk_cycles as Y
import gfk_exact as X
import gfk_simulation as M


def band(p, runs, sigmas=4.5):
    """4,5 Standardabweichungen einer Anteilsschätzung aus `runs` unabhängigen Läufen."""
    return sigmas * math.sqrt(p * (1 - p) / runs)


def test_random_arrangements_are_permutations_and_reproducible():
    a = M.random_arrangements(7, 50, 9)
    assert all(Y.is_permutation(row) for row in a)
    assert (a == M.random_arrangements(7, 50, 9)).all() and not (a == M.random_arrangements(8, 50, 9)).all()


def test_adversary_against_the_cycle_strategy_is_one_cycle_of_length_n():
    for n in (2, 5, 100):
        assert Y.cycle_lengths(list(M.adversary_against_cycle(n))) == [n]


def test_adversary_against_fixed_windows_defeats_every_prisoner_unless_m_is_n():
    for n, m in ((8, 4), (9, 1), (10, 9)):
        q = M.adversary_against_fixed(n, m)[None, :]
        assert Y.is_permutation(list(q[0])) and M.fixed_window_successes(q, m)[0] == 0
    q = M.adversary_against_fixed(6, 6)[None, :]
    assert M.fixed_window_successes(q, 6)[0] == 6


def test_fixed_window_successes_by_hand():
    """n = 4, m = 2, Fenster {i, i+1}. q = (1, 2, 3, 0) heißt: Zettel 1 in Kasten 0, Zettel 2 in Kasten 1, Zettel 3 in Kasten 2, Zettel 0 in Kasten 3.
    Gefangener 0: Zettel in Kasten 3, Fenster {0, 1}: nein. Gefangener 1: Kasten 0, Fenster {1, 2}: nein. Gefangener 2: Kasten 1, Fenster {2, 3}: nein.
    Gefangener 3: Kasten 2, Fenster {3, 0}: nein. Die Identität: jeder im eigenen Kasten, 4 Erfolge. q = (0, 2, 1, 3): Gefangene 0 (Kasten 0) und 3 (Kasten 3) ja,
    Gefangener 1 (Zettel 1 in Kasten 2, Fenster {1, 2}) ja, Gefangener 2 (Zettel 2 in Kasten 1, Fenster {2, 3}) nein: 3 Erfolge."""
    q = np.array([[1, 2, 3, 0], [0, 1, 2, 3], [0, 2, 1, 3]])
    assert list(M.fixed_window_successes(q, 2)) == [0, 4, 3]


def test_team_view_composes_the_renaming():
    q = np.array([[10, 11, 12, 13]])
    rho = np.array([[2, 0, 3, 1]])
    assert list(M.team_view(q, rho)[0]) == [12, 10, 13, 11] and M.team_view(q, None) is q


def test_warden_who_knows_the_strategy_beats_the_cycle_strategy_and_fixed_windows():
    r = M.simulate(20, 10, C.WARDEN_KNOWS, 0, 200, 3)
    assert (r.s_cycle == 0).all() and (r.s_fixed == 0).all() and (r.longest == 20).all() and (r.cost == 1).all()


def test_the_three_wardens_differ_for_the_cycle_strategy():
    """Zweig-Test: jede Variante weicht von der Nachbarvariante ab (Zufall ≠ Wärter ≠ geheime Umnummerierung)."""
    n, m, runs = 20, 10, 4000
    rates = {w: float((M.simulate(n, m, w, 0, runs, 5).s_cycle == n).mean()) for w in C.WARDENS}
    assert rates[C.WARDEN_KNOWS] == 0.0
    assert rates[C.WARDEN_RANDOM] > 0.25 and rates[C.WARDEN_SECRET] > 0.25
    assert rates[C.WARDEN_RANDOM] != rates[C.WARDEN_SECRET]       # andere Ströme, andere Anteile (kein toter Zweig)


def test_helper_branch_changes_the_result():
    base = M.simulate(20, 10, C.WARDEN_RANDOM, 0, 1000, 9)
    helped = M.simulate(20, 10, C.WARDEN_RANDOM, 1, 1000, 9)
    assert (helped.s_cycle == 20).all() and not (base.s_cycle == 20).all()
    # nicht ausreichende Vertauschungen: der Helfer greift nicht ein, das Ergebnis bleibt das ohne Helfer
    weak = M.simulate(30, 5, C.WARDEN_RANDOM, 1, 1000, 9)
    plain = M.simulate(30, 5, C.WARDEN_RANDOM, 0, 1000, 9)
    needs_more = weak.cost > 1
    assert (weak.s_cycle[needs_more] == plain.s_cycle[needs_more]).all() and needs_more.any()
    assert (weak.s_cycle[weak.cost == 1] == 30).all()


def test_cycle_simulation_is_the_literal_strategy_on_the_same_arrangements():
    """Kleines Netz: die Zahl der Erfolge je Lauf (aus Zykluslängen) gleicht dem wörtlichen Öffnen der Kästen auf den Anordnungen desselben Stroms."""
    n, m, seed, runs = 9, 4, 11, 40
    r = M.simulate(n, m, C.WARDEN_RANDOM, 0, runs, seed)
    import gfk_scenario as S
    q = M.random_arrangements(S.stream_seed(seed, f"perm|{n}|{m}|{C.WARDEN_RANDOM}|0"), runs, n)
    literal = [sum(Y.follow_boxes(list(row), i, m)[1] for i in range(n)) for row in q]
    assert list(r.s_cycle) == literal


def test_zufall_strategy_literal_subsets_match_the_binomial():
    """Wörtlich: jeder wählt m verschiedene Kästen zufällig; Erfolg, wenn sein Zettel dabei ist. Anteil der Läufe mit lauter Erfolgen gegen (m/n)^n (n = 4, m = 3: 0,3164)."""
    rng = np.random.default_rng(2)
    n, m, runs = 4, 3, 20000
    wins = 0
    for _ in range(runs):
        q = rng.permutation(n)
        box_of = np.argsort(q)
        wins += all(box_of[i] in rng.choice(n, size=m, replace=False) for i in range(n))
    p = (m / n) ** n
    assert abs(wins / runs - p) < band(p, runs)


@pytest.mark.parametrize("warden", [C.WARDEN_RANDOM, C.WARDEN_SECRET])
def test_simulation_matches_the_exact_values_n8(warden):
    n, m, runs = 8, 4, 20000
    r = M.simulate(n, m, warden, 0, runs, 4)
    p = 307 / 840
    assert abs((r.s_cycle == n).mean() - p) < band(p, runs)
    assert abs(r.s_cycle.mean() / n - m / n) < 0.01                       # Einzelchance m/n
    assert abs((r.s_random.mean() / n) - m / n) < 0.01
    pf = X.fixed_window_probability(n, m)
    assert abs((r.s_fixed == n).mean() - pf) < band(pf, runs)
    assert abs(r.s_fixed.mean() / n - m / n) < 0.01


def test_simulation_matches_the_exact_values_n100():
    r = M.simulate(100, 50, C.WARDEN_RANDOM, 0, 20000, 6)
    p = X.cycle_formula(100, 50)
    assert abs((r.s_cycle == 100).mean() - p) < band(p, 20000)
    assert abs(r.s_cycle.mean() - 50) < 1.0
    assert (r.s_random == 100).sum() == 0 and (r.s_fixed == 100).sum() == 0


def test_chunks_do_not_change_the_meaning():
    """Mehr Läufe als ein Block: die Längen stimmen, und der Anteil liegt im Band."""
    n, m, runs = 10, 5, C.CHUNK_RUNS * 2 + 500
    r = M.simulate(n, m, C.WARDEN_RANDOM, 0, runs, 8)
    assert len(r.s_cycle) == len(r.cost) == len(r.longest) == len(r.s_random) == len(r.s_fixed) == runs
    p = float(X.cycle_formula(n, m))
    assert abs((r.s_cycle == n).mean() - p) < band(p, runs)


def test_same_seed_same_result_different_seed_different_result():
    a, b, c = (M.simulate(12, 6, C.WARDEN_RANDOM, 0, 500, s) for s in (1, 1, 2))
    assert (a.s_cycle == b.s_cycle).all() and not (a.s_cycle == c.s_cycle).all()


def test_all_succeed_count():
    assert M.all_succeed_count(np.array([3, 3, 1, 3]), 3) == 3
