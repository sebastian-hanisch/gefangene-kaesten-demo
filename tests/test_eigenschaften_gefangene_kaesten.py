"""Eigenschaftstests: Aussagen, die für alle Eingaben eines Rasters gelten müssen (Monotonie, Symmetrie, Invarianz, Erwartungswerte)."""

import numpy as np
import pytest

import gfk_cycles as Y
import gfk_exact as X


def test_cycle_strategy_never_loses_to_random_boxes_on_the_whole_grid():
    """Zyklus-Strategie gegen Zufall, alle n bis 30 und alle m: (m/n)^n <= F_m(n), und für m < n strikt (n! < n^n)."""
    for n in range(2, 31):
        cdf = X.max_cycle_cdf(n)
        for m in range(1, n):
            assert cdf[m] > X.prob_all_random(n, m), (n, m)
        assert cdf[n] == pytest.approx(1.0)


def test_success_probability_rises_with_m_and_with_every_extra_swap():
    for n in (6, 11, 30):
        cdf = X.max_cycle_cdf(n)
        assert all(a < b for a, b in zip(cdf[1:], cdf[2:]))
        for m in (2, n // 3 or 1, n // 2):
            ps = [X.prob_all_with_swaps(n, m, k) for k in range(4)]
            assert all(a <= b + 1e-15 for a, b in zip(ps, ps[1:])) and ps[0] == pytest.approx(cdf[m])


def test_relabeling_prisoners_and_boxes_together_keeps_the_successes():
    """Konjugation: die Anordnung p q p^-1 hat dieselbe Zyklenstruktur, also gleich viele Erfolge (die Strategie hängt nicht an den Namen)."""
    rng = np.random.default_rng(3)
    for _ in range(200):
        n = int(rng.integers(2, 25))
        q = rng.permutation(n)
        p = rng.permutation(n)
        inv = np.argsort(p)
        conj = p[q[inv]]
        for m in (1, n // 2 or 1, n):
            assert Y.successes_batch(q[None, :], m)[0] == Y.successes_batch(conj[None, :], m)[0]


def test_inverse_arrangement_has_the_same_cycle_lengths():
    rng = np.random.default_rng(4)
    for _ in range(100):
        q = rng.permutation(int(rng.integers(2, 30)))
        assert sorted(Y.cycle_lengths(list(q))) == sorted(Y.cycle_lengths(list(np.argsort(q))))


def test_failing_prisoners_come_in_whole_cycles_longer_than_m():
    """Wer scheitert, liegt in einem Zyklus über m, und alle Mitglieder dieses Zyklus scheitern mit: die Zahl der Erfolglosen ist eine Summe von Zykluslängen über m (mindestens m + 1 je Zyklus)."""
    rng = np.random.default_rng(6)
    for _ in range(300):
        n = int(rng.integers(2, 40))
        q = rng.permutation(n)
        m = int(rng.integers(1, n + 1))
        failed = n - Y.successes_batch(q[None, :], m)[0]
        long_ = [length for length in Y.cycle_lengths(list(q)) if length > m]
        assert failed == sum(long_) and all(length >= m + 1 for length in long_)


def test_mean_number_of_successes_is_m_for_every_n_and_m():
    for n in (2, 3, 9, 20):
        for m in range(1, n + 1):
            pmf = X.successes_pmf_cycle(n, m)
            assert float((pmf * np.arange(n + 1)).sum()) == pytest.approx(m, rel=1e-9)


def test_number_of_failures_is_one_over_L_for_each_long_length_when_m_is_at_least_half():
    for n, m in ((10, 5), (11, 6), (20, 10)):
        pmf = X.successes_pmf_cycle(n, m)
        for length in range(m + 1, n + 1):
            assert pmf[n - length] == pytest.approx(1 / length, rel=1e-9), (n, m, length)


def test_worst_case_arrangement_needs_the_most_swaps():
    """Die Kosten jeder Anordnung sind höchstens die des einzelnen n-Zyklus (Verschmelzen erhöht die Kosten nie)."""
    rng = np.random.default_rng(8)
    for _ in range(200):
        n = int(rng.integers(2, 40))
        m = int(rng.integers(1, n + 1))
        q = rng.permutation(n)
        assert Y.swap_cost_of_lengths(Y.cycle_lengths(list(q)), m) <= X.worst_case_cost(n, m)
