"""Zyklen: Mini-Anordnung von Hand, wörtliche Strategie gegen die Zyklenlänge, vektorisierte Fassung gegen die Schleife, Vertauschungskosten und -plan."""

import numpy as np
import pytest

import gfk_cycles as Y


def test_cycles_and_lengths_of_the_mini_arrangement(mini):
    assert Y.cycles_of(mini["q"]) == mini["cycles"]
    assert Y.cycle_lengths(mini["q"]) == mini["lengths"]


def test_follow_boxes_by_hand(mini):
    opened, found = Y.follow_boxes(mini["q"], 0, 3)
    assert opened == [(0, 1), (1, 2), (2, 0)] and found
    opened2, found2 = Y.follow_boxes(mini["q"], 0, 2)
    assert opened2 == [(0, 1), (1, 2)] and not found2
    assert Y.follow_boxes(mini["q"], 5, 1) == ([(5, 5)], True)


def test_prisoner_succeeds_exactly_when_the_cycle_is_at_most_m(mini):
    """Die Kernaussage der Strategie, für jeden Gefangenen und jedes m an der Mini-Anordnung und an 200 Zufallsanordnungen (n = 7)."""
    rng = np.random.default_rng(1)
    for q in [mini["q"]] + [list(rng.permutation(7)) for _ in range(200)]:
        length_of = {}
        for cyc in Y.cycles_of(q):
            for box in cyc:
                length_of[box] = len(cyc)
        for m in range(1, len(q) + 1):
            for i in range(len(q)):
                assert Y.follow_boxes(q, i, m)[1] == (length_of[i] <= m), (q, i, m)


@pytest.mark.parametrize("n", [1, 2, 5, 17, 100])
def test_batch_cycle_lengths_equal_the_loop(n):
    rng = np.random.default_rng(n)
    perms = np.array([rng.permutation(n) for _ in range(60)])
    lengths, reps = Y.element_cycle_lengths(perms)
    for r in range(len(perms)):
        cycles = Y.cycles_of(list(perms[r]))
        expected = np.zeros(n, dtype=int)
        for cyc in cycles:
            expected[cyc] = len(cyc)
        assert (lengths[r] == expected).all()
        assert sorted(np.flatnonzero(reps[r])) == sorted(c[0] for c in cycles)   # Vertreter = kleinster Kasten (Zyklen beginnen beim kleinsten)


def test_min_label_is_the_smallest_box_of_the_cycle(mini):
    label = Y.min_label_batch(np.array([mini["q"]]))
    assert list(label[0]) == [0, 0, 0, 3, 3, 5]


def test_swap_cost_by_hand(mini):
    assert Y.swap_cost_of_lengths(mini["lengths"], 2) == mini["cost_m2"]
    assert Y.swap_cost_of_lengths(mini["lengths"], 1) == mini["cost_m1"]
    assert Y.swap_cost_of_lengths(mini["lengths"], 3) == 0
    q = np.array([mini["q"]])
    assert Y.swap_cost_batch(q, 2)[0] == 1 and Y.swap_cost_batch(q, 1)[0] == 3 and Y.successes_batch(q, 2)[0] == mini["success_m2"]


def test_plan_swaps_has_the_cost_length_and_fixes_every_cycle():
    rng = np.random.default_rng(5)
    for _ in range(100):
        n = int(rng.integers(2, 30))
        q = [int(x) for x in rng.permutation(n)]
        for m in (1, 2, 3, max(1, n // 2), n):
            plan = Y.plan_swaps(q, m)
            assert len(plan) == Y.swap_cost_of_lengths(Y.cycle_lengths(q), m)
            after = q
            for a, b in plan:
                after = Y.swap_contents(after, a, b)
            assert Y.is_permutation(after) and max(Y.cycle_lengths(after)) <= m


def test_swap_contents_exchanges_two_entries_and_keeps_the_original():
    q = [2, 0, 1]
    assert Y.swap_contents(q, 0, 2) == [1, 0, 2] and q == [2, 0, 1]


def test_is_permutation():
    assert Y.is_permutation([2, 0, 1]) and not Y.is_permutation([0, 0, 1]) and not Y.is_permutation([1, 2, 3])
