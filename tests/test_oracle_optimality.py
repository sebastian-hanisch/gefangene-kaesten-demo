"""Orakel: ist die Zyklus-Strategie unter ALLEN deterministischen, anpassungsfähigen Strategien optimal? Aufzählung für kleine n (n = 3 und n = 4).

Eine Strategie eines Gefangenen ist ein Entscheidungsbaum: welchen Kasten er als Nächstes öffnet, hängt von den bisher gesehenen Zetteln ab; er hört auf, wenn er seinen Zettel
gesehen hat oder m Kästen offen waren. Für jede Anordnung wird festgehalten, ob der Gefangene mit seiner Strategie Erfolg hat (ein Bitmuster über alle n! Anordnungen). Das Team gewinnt in
den Anordnungen, in denen alle Erfolg haben (UND der Bitmuster); gesucht ist das beste UND über alle Strategiewahlen. Das ist die Aufzählung des Teams, nicht der Zyklus-Formel:
sie bestätigt die Optimalität nur für diese kleinen Fälle. Der allgemeine Beweis ist Literatur (README). Entspricht der Vormessung e1c im Ordner teamraetsel-planung."""

import itertools
from fractions import Fraction

import pytest

import gfk_exact as X


def strategies(i, n, m, opened, seen):
    """Alle Entscheidungsbäume als (Kasten, {gesehener Zettel: Unterbaum}); None = fertig."""
    if len(opened) == m:
        yield None
        return
    for box in range(n):
        if box in opened:
            continue
        values = [v for v in range(n) if v != i and v not in seen]
        choices = [list(strategies(i, n, m, opened | {box}, seen | {v})) for v in values]
        for combo in itertools.product(*choices):
            yield (box, dict(zip(values, combo)))


def success_mask(tree, i, perms):
    mask = 0
    for idx, p in enumerate(perms):
        node = tree
        while node is not None:
            box, children = node
            v = p[box]
            if v == i:
                mask |= 1 << idx
                break
            node = children[v]
    return mask


def prune(masks):
    masks = sorted(masks, key=lambda x: -bin(x).count("1"))
    keep = []
    for x in masks:
        if not any(x & k == x for k in keep):
            keep.append(x)
    return keep


def best_team(n, m):
    perms = list(itertools.permutations(range(n)))
    per_prisoner = [prune({success_mask(t, i, perms) for t in strategies(i, n, m, frozenset(), frozenset())}) for i in range(n)]
    acc = {(1 << len(perms)) - 1}
    for masks in per_prisoner:
        acc = set(prune({a & b for a in acc for b in masks}))
    return Fraction(max(bin(x).count("1") for x in acc), len(perms))


@pytest.mark.parametrize("n,m", [(3, 1), (3, 2), (4, 1), (4, 2)])
def test_best_team_strategy_equals_the_cycle_strategy_for_small_n(n, m):
    assert best_team(n, m) == X.max_cycle_cdf(n, True)[m]


def test_known_values():
    """n = 3, m = 2: 2/3; n = 4, m = 2: 5/12 (Handrechnung der Zyklus-Strategie: 1 - 1/3 - 1/4)."""
    assert best_team(3, 2) == Fraction(2, 3) and best_team(4, 2) == Fraction(5, 12)
