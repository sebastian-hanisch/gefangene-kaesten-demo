"""Abbildungen: alle Achsen gesperrt (fixedrange), Daten stimmen mit den übergebenen Werten überein, Randfälle (n = 2, ein einziger Zyklus)."""

import numpy as np
import pytest

import gfk_evaluation as ev
import gfk_exact as X
import gfk_experiments as XP
import gfk_scenario as S
import gfk_visualization as Z


def locked(fig):
    axes = [fig.layout[k] for k in fig.layout if k.startswith("xaxis") or k.startswith("yaxis")]
    return axes and all(a.fixedrange is True for a in axes)


def test_all_figures_have_locked_axes():
    view = ev.analyse(S.Settings(n=12, runs=1000))
    figs = [Z.build_pmf(12, view.pmf_cycle, view.pmf_random, view.hist_fixed), Z.build_cycles(list(view.example.lengths), view.m), Z.build_longest(list(view.longest_pmf), view.m),
            Z.build_e1(XP.e1_curve(12), 12, view.m), Z.build_e2(XP.e2_rows(), XP.e2_limit()), Z.build_e4(XP.e4_rows(12))]
    assert all(locked(f) for f in figs)


def test_pmf_figure_shows_the_exact_values_in_percent():
    pmf_c, pmf_r = X.successes_pmf_cycle(8, 4), X.successes_pmf_random(8, 4)
    fig = Z.build_pmf(8, pmf_c, pmf_r, np.zeros(9))
    bar, line = fig.data[0], fig.data[1]
    assert bar.y[8] == pytest.approx(100 * 307 / 840) and line.y[4] == pytest.approx(100 * 70 * 0.5 ** 8)
    assert len(fig.data) == 3 and list(bar.x) == list(range(9))


def test_cycle_figure_colors_the_too_long_cycles_red():
    fig = Z.build_cycles([1, 5, 2], 2)
    assert list(fig.data[0].y) == [5, 2, 1]
    assert [c == Z.C.COLOR_BAD for c in fig.data[0].marker.color] == [True, False, False]


def test_longest_figure_for_a_single_cycle_and_n_two():
    pmf = X.longest_cycle_pmf(2)
    fig = Z.build_longest(pmf, 1)
    assert list(fig.data[0].y) == [50.0, 50.0] and fig.data[0].marker.color[1] == Z.C.COLOR_BAD
    assert locked(Z.build_cycles([2], 1))


def test_e4_figure_has_one_bar_set_per_share_and_k_values():
    fig = Z.build_e4(XP.e4_rows(20))
    assert len(fig.data) == 4 and all(len(t.y) == 4 for t in fig.data)
