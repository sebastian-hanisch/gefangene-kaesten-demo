"""Orakel-Test gefangene-kaesten-demo: die Kernroutinen gegen ANDERE Rechenwege.

* Aufzählung aller Anordnungen (itertools, n <= 9) gegen die Rekursion über den Zyklus des ersten Kastens (Brüche) und gegen die Formel 1 - Summe 1/k.
* Summe über alle Zyklentypen (Partitionen von n, Gewicht 1 / Produkt k^m_k m_k!) gegen die Rekursion, n <= 25.
* Stirling-Zahlen erster Art (Rekursion c(n,k) = c(n-1,k-1) + (n-1) c(n-1,k)): Zahl der Zyklen gegen die Aufzählung; Erwartung H_n.
* Permanent der Fenster-Matrix: Aufzählung, Ryser-Formel, Teilmengen-DP der Demo.
* Verteilung der Erfolge und der Vertauschungskosten gegen die Aufzählung; Vertauschungen gegen die Aufzählung aller Vertauschungsfolgen.
* Geheime Umnummerierung: Mittel über alle Umbenennungen gegen die Rekursion.
"""

import itertools
import math
from fractions import Fraction

import numpy as np
import pytest

import gfk_cycles as Y
import gfk_exact as X
import gfk_simulation as M


def cycle_type_lengths(p):
    """Zykluslängen einer Anordnung, unabhängig von gfk_cycles geschrieben (Zeigerverfolgung mit Besuchsmarken)."""
    n, seen, out = len(p), set(), []
    for s in range(n):
        if s in seen:
            continue
        length, i = 0, s
        while i not in seen:
            seen.add(i)
            i = p[i]
            length += 1
        out.append(length)
    return out


def partitions(n, largest=None):
    largest = n if largest is None else largest
    if n == 0:
        yield []
        return
    for k in range(min(n, largest), 0, -1):
        for rest in partitions(n - k, k):
            yield [k] + rest


def partition_weight(parts):
    w = Fraction(1)
    for k in set(parts):
        mk = parts.count(k)
        w /= Fraction(k) ** mk * math.factorial(mk)
    return w


# --- Aufzählung aller Anordnungen --------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("n", range(2, 10))
def test_enumeration_equals_recursion_and_formula(n):
    perms = list(itertools.permutations(range(n)))
    longest = [max(cycle_type_lengths(p)) for p in perms]
    cdf = X.max_cycle_cdf(n, True)
    for m in range(1, n + 1):
        enum = Fraction(sum(1 for L in longest if L <= m), len(perms))
        assert enum == cdf[m], (n, m)
        if 2 * (m + 1) > n:
            assert enum == X.cycle_formula(n, m, True), (n, m)


def test_individual_chance_is_m_over_n_by_enumeration():
    n = 6
    perms = list(itertools.permutations(range(n)))
    for m in range(1, n + 1):
        total = sum(sum(1 for i in range(n) if Y.follow_boxes(p, i, m)[1]) for p in perms)
        assert Fraction(total, len(perms) * n) == Fraction(m, n)


def test_joint_distribution_equals_enumeration():
    """P(s Gefangene in kurzen Zyklen, Vertauschungskosten c) für n = 7 und alle m, aufgezählt."""
    n = 7
    perms = list(itertools.permutations(range(n)))
    lengths = [cycle_type_lengths(p) for p in perms]
    for m in range(1, n + 1):
        counts = {}
        for L in lengths:
            s = sum(x for x in L if x <= m)
            c = min(3, sum(-(-x // m) - 1 for x in L))
            counts[(s, c)] = counts.get((s, c), 0) + 1
        joint = X.joint_distribution(n, m, 3, True)
        for s in range(n + 1):
            for c in range(4):
                assert joint[s, c] == Fraction(counts.get((s, c), 0), len(perms)), (m, s, c)


# --- Zyklentypen -------------------------------------------------------------------------------------------------------------------------------
def test_sum_over_cycle_types_equals_the_recursion():
    for n in (1, 2, 5, 12, 18, 25):
        cdf = X.max_cycle_cdf(n, True)
        types = [(p, partition_weight(p)) for p in partitions(n)]
        assert sum(w for _, w in types) == 1
        for m in sorted(x for x in {1, 2, 3, n // 3 or 1, n // 2 or 1, n - 1 or 1, n} if x <= n):
            assert sum(w for p, w in types if max(p) <= m) == cdf[m], (n, m)


def test_cycle_length_of_a_fixed_box_is_uniform():
    """Über die Zyklentypen: der Kasten 0 liegt in einem Zyklus der Länge k mit Wahrscheinlichkeit k · (Anteil der Anordnungen mit diesem Typ) / n, summiert 1/n je k."""
    n = 9
    prob = {k: Fraction(0) for k in range(1, n + 1)}
    for p in partitions(n):
        w = partition_weight(p)
        for k in set(p):
            prob[k] += w * p.count(k) * k / n
    assert all(v == Fraction(1, n) for v in prob.values())


# --- Stirling-Zahlen ---------------------------------------------------------------------------------------------------------------------------
def stirling_first_kind(n):
    """c[n][k] = Zahl der Anordnungen von n Kästen mit genau k Zyklen."""
    c = [[0] * (n + 2) for _ in range(n + 1)]
    c[0][0] = 1
    for i in range(1, n + 1):
        for k in range(1, i + 1):
            c[i][k] = c[i - 1][k - 1] + (i - 1) * c[i - 1][k]
    return c


def test_number_of_cycles_equals_stirling_numbers_and_has_mean_H_n():
    n = 7
    c = stirling_first_kind(n)
    perms = list(itertools.permutations(range(n)))
    counts = {}
    for p in perms:
        k = len(Y.cycles_of(p))
        counts[k] = counts.get(k, 0) + 1
    assert all(counts.get(k, 0) == c[n][k] for k in range(1, n + 1)) and sum(c[n]) == math.factorial(n)
    for nn in (5, 20, 60):
        cc = stirling_first_kind(nn)
        mean = Fraction(sum(k * cc[nn][k] for k in range(1, nn + 1)), math.factorial(nn))
        assert mean == sum(Fraction(1, j) for j in range(1, nn + 1))


# --- Fester Permanent --------------------------------------------------------------------------------------------------------------------------
def ryser(a):
    n = len(a)
    total = 0
    for mask in range(1, 1 << n):
        cols = [j for j in range(n) if mask >> j & 1]
        prod = 1
        for i in range(n):
            prod *= sum(a[i][j] for j in cols)
        total += (-1) ** (n - len(cols)) * prod
    return total


def test_fixed_windows_equal_enumeration_and_ryser():
    for n in range(2, 9):
        perms = list(itertools.permutations(range(n)))
        for m in range(1, n + 1):
            enum = sum(1 for q in perms if all((q.index(i) - i) % n < m for i in range(n)))
            assert X.fixed_window_count(n, m) == enum, (n, m)
    for n, m in ((9, 4), (10, 5), (10, 3)):
        assert X.fixed_window_count(n, m) == ryser(X.fixed_window_matrix(n, m).tolist()), (n, m)


# --- Vertauschungen ----------------------------------------------------------------------------------------------------------------------------
def min_swaps_by_search(p, m, kmax):
    """Kleinste Zahl von Vertauschungen (zwei Kästen tauschen ihre Zettel) bis kein Zyklus länger als m ist, durch Aufzählung aller Folgen; None, wenn mehr als kmax."""
    n = len(p)
    level = {tuple(p)}
    for k in range(kmax + 1):
        if any(max(cycle_type_lengths(q)) <= m for q in level):
            return k
        if k == kmax:
            return None
        level = {tuple(q[:i]) + (q[j],) + tuple(q[i + 1:j]) + (q[i],) + tuple(q[j + 1:]) for q in level for i in range(n) for j in range(i + 1, n)}
    return None


def test_swap_cost_equals_the_search_over_all_swap_sequences():
    for n in range(2, 7):
        for p in itertools.permutations(range(n)):
            lengths = cycle_type_lengths(p)
            for m in range(1, n + 1):
                cost = Y.swap_cost_of_lengths(lengths, m)
                found = min_swaps_by_search(p, m, 3)
                assert found == (cost if cost <= 3 else None), (p, m)


def test_one_swap_always_suffices_for_m_at_least_half_n8():
    perms = list(itertools.permutations(range(8)))
    assert all(Y.swap_cost_of_lengths(cycle_type_lengths(p), 4) <= 1 for p in perms)
    assert sum(1 for p in perms if min_swaps_by_search(p, 4, 1) is not None) == len(perms) == 40320


def test_prob_with_swaps_equals_enumeration_n8():
    perms = list(itertools.permutations(range(8)))
    costs = [Y.swap_cost_of_lengths(cycle_type_lengths(p), 3) for p in perms]      # m = 3 < n/2: Kosten bis 2
    for k in range(3):
        assert X.prob_all_with_swaps(8, 3, k) == pytest.approx(sum(1 for c in costs if c <= k) / len(perms), rel=1e-12)


# --- Geheime Umnummerierung --------------------------------------------------------------------------------------------------------------------
def test_secret_renaming_averages_to_the_uniform_value_for_every_arrangement_n7():
    n, m = 7, 4
    target = X.max_cycle_cdf(n, True)[m]
    renamings = list(itertools.permutations(range(n)))
    rng = np.random.default_rng(0)
    for q in [list(M.adversary_against_cycle(n))] + [list(rng.permutation(n)) for _ in range(4)]:
        wins = sum(1 for rho in renamings if max(cycle_type_lengths([q[r] for r in rho])) <= m)
        assert Fraction(wins, len(renamings)) == target


def test_secret_renaming_also_helps_the_fixed_windows_n6():
    n, m = 6, 3
    target = Fraction(X.fixed_window_count(n, m), math.factorial(n))
    q = list(M.adversary_against_fixed(n, m))
    wins = 0
    for rho in itertools.permutations(range(n)):
        team = [q[r] for r in rho]
        wins += all((team.index(i) - i) % n < m for i in range(n))
    assert Fraction(wins, math.factorial(n)) == target
