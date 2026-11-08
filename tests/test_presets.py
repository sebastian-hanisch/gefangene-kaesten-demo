"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Permalink (Begrenzen, Einrasten), Wirkung jedes Presets auf eine andere Größe."""

import gfk_constants as C
import gfk_evaluation as ev
import gfk_presets as P
import gfk_scenario as S


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for preset in C.PRESETS.values():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and C.SHARE_MIN <= preset["share"] <= C.SHARE_MAX
        assert preset["warden"] in C.WARDENS and C.SWAPS_MIN <= preset["swaps"] <= C.SWAPS_MAX
        assert C.RUNS_MIN <= preset["runs"] <= C.RUNS_MAX and (preset["runs"] - C.RUNS_MIN) % C.RUNS_STEP == 0 and 0 <= preset["seed"] <= C.SEED_MAX


def test_default_preset_equals_the_default_settings():
    assert S.Settings(**C.PRESETS["Das klassische Rätsel"]) == S.Settings()
    assert next(iter(C.PRESETS)) == "Das klassische Rätsel"


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_presets_differ_from_each_other_in_the_numbers_they_show():
    """Kein Preset ohne Wirkung: Wärter 0, Helfer 1, geheime Umnummerierung stellt den klassischen Wert wieder her (Absicht), n = 8 und 40 % zeigen andere Werte."""
    classic = ev.exact_table(S.settings_of_preset("Das klassische Rätsel"))["Zyklus-Strategie"].p_all
    secret = ev.exact_table(S.settings_of_preset("Der Wärter, aber geheim umnummeriert"))["Zyklus-Strategie"].p_all
    warden = ev.exact_table(S.settings_of_preset("Der Wärter kennt die Strategie"))["Zyklus-Strategie"].p_all
    helper = ev.exact_table(S.settings_of_preset("Ein Helfer vertauscht vorab zwei Kästen"))["Zyklus-Strategie"].p_all
    eight = ev.exact_table(S.settings_of_preset("Zum Nachzählen: 8 Gefangene"))["Zyklus-Strategie"].p_all
    forty = ev.exact_table(S.settings_of_preset("Zu wenige Kästen: 40 von 100"))["Zyklus-Strategie"].p_all
    assert secret == classic and warden == 0.0 and helper == 1.0
    assert len({round(x, 9) for x in (classic, warden, helper, eight, forty)}) == 5


def test_share_rounds_to_whole_boxes():
    assert S.boxes_per_person(100, 50) == 50 and S.boxes_per_person(8, 50) == 4 and S.boxes_per_person(7, 50) == 4      # 3,5 wird aufgerundet
    assert S.boxes_per_person(100, 1) == 1 and S.boxes_per_person(2, 1) == 1 and S.boxes_per_person(100, 100) == 100 and S.boxes_per_person(2, 100) == 2


def test_settings_only_with_keywords():
    import pytest
    with pytest.raises(TypeError):
        S.Settings(100, 50)
    assert S.with_(S.Settings(), n=8).n == 8
