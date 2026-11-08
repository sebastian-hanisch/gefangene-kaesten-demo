"""End-to-end Smoke-Test via Streamlits offiziellem AppTest-Framework: laedt app.py mit den
Standardeinstellungen, klickt jeden Preset-Button und faehrt jeden Slider an seine Grenzen und prueft, dass
kein Python-Fehler auftritt - insbesondere `streamlit.errors.StreamlitDuplicateElementId` (mehrere
st.plotly_chart-Aufrufe ohne eindeutiges key= koennen zufaellig identischen Inhalt rendern und kollidieren)
und `StreamlitAPIException` bei Slidern mit berechneten Grenzen (min == max)."""

import os

from streamlit.testing.v1 import AppTest

APP_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))  # unter Last (parallele Läufe) reichen 180 s nicht immer; Umgebungsvariable zum Anpassen
AUTOPLAY_MARKER = "\u25b6"  # Auto-Play-Buttons (Animation mit sleep) im Smoke-Test auslassen


def _fresh_app() -> AppTest:
    at = AppTest.from_file(APP_PATH)
    at.run(timeout=TIMEOUT)
    assert not at.exception, [str(e) for e in at.exception]
    return at


def test_app_loads_without_exception():
    _fresh_app()


def test_every_button_click_does_not_raise():
    labels = [b.label for b in _fresh_app().button]
    assert labels, "keine Buttons gefunden"
    for index, label in enumerate(labels):
        if AUTOPLAY_MARKER in label:
            continue
        at = _fresh_app()
        at.button[index].click().run(timeout=TIMEOUT)
        assert not at.exception, (label, [str(e) for e in at.exception])


def test_every_slider_at_its_min_and_max_does_not_raise():
    labels = [s.label for s in _fresh_app().slider]
    assert labels, "keine Slider gefunden"
    for index, label in enumerate(labels):
        for edge in ("min", "max"):
            at = _fresh_app()
            slider = at.slider[index]
            value = slider.min if edge == "min" else slider.max
            if isinstance(slider.value, int):
                value = int(value)
            slider.set_value(value).run(timeout=TIMEOUT)
            assert not at.exception, (label, edge, [str(e) for e in at.exception])


# --- Eigene Fälle der Demo -----------------------------------------------------------------------------------------------------------------------------
def test_all_minima_and_all_maxima_together_do_not_raise():
    for edge in ("min", "max"):
        at = _fresh_app()
        for slider in list(at.sidebar.slider):
            slider.set_value(int(slider.min if edge == "min" else slider.max))
        at.run(timeout=TIMEOUT)
        assert not at.exception, (edge, [str(e) for e in at.exception])


def test_every_warden_with_every_helper_setting_and_extreme_shares():
    for warden in ("zufall", "waerter", "umnummeriert"):
        for swaps, share, n in ((0, 1, 2), (3, 100, 2), (3, 25, 100), (1, 50, 7)):
            at = _fresh_app()
            at.sidebar.selectbox(key="warden_select").set_value(warden)
            at.sidebar.slider(key="swaps_slider").set_value(swaps)
            at.sidebar.slider(key="share_slider").set_value(share)
            at.sidebar.slider(key="n_slider").set_value(n)
            at.run(timeout=TIMEOUT)
            assert not at.exception, (warden, swaps, share, n, [str(e) for e in at.exception])


def test_experiment_buttons_show_their_live_tables():
    at = _fresh_app()
    at.sidebar.slider(key="runs_slider").set_value(1000)
    at.run(timeout=TIMEOUT)
    before = len(at.dataframe)          # Hauptansicht, Weg eines Gefangenen und je Experiment eine exakte Tabelle
    assert before == 6
    for key in ("e1_button", "e2_button", "e3_button", "e4_button"):
        at.button(key=key).click().run(timeout=TIMEOUT)
        assert not at.exception, (key, [str(e) for e in at.exception])
        assert len(at.dataframe) == before + 1       # jeder Knopf fügt genau seine Nachspiel-Tabelle hinzu; die der vorigen Knöpfe bleiben
        before = len(at.dataframe)


def test_pdf_button_makes_a_download_button():
    at = _fresh_app()
    at.button(key="pdf_button").click().run(timeout=TIMEOUT)
    assert not at.exception
    assert len(at.session_state["pdf_bytes"]) > 1000 and at.session_state["pdf_bytes"][:5] == b"%PDF-"


def test_permalink_sets_the_controls_and_bad_values_are_ignored():
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.query_params["n"] = "8"
    at.query_params["share"] = "40"
    at.query_params["warden"] = "waerter"
    at.query_params["runs"] = "2400"        # rastet auf 2000 ein
    at.run(timeout=TIMEOUT)
    assert not at.exception
    assert at.sidebar.slider(key="n_slider").value == 8 and at.sidebar.slider(key="share_slider").value == 40
    assert at.sidebar.selectbox(key="warden_select").value == "waerter" and at.sidebar.slider(key="runs_slider").value == 2000
    bad = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    bad.query_params["warden"] = "unsinn"
    bad.query_params["n"] = "100000"
    bad.run(timeout=TIMEOUT)
    assert not bad.exception
    assert bad.sidebar.selectbox(key="warden_select").value == "zufall" and bad.sidebar.slider(key="n_slider").value == 100


def test_trace_prisoner_is_clamped_when_n_shrinks():
    at = _fresh_app()
    at.number_input(key="trace_prisoner").set_value(100).run(timeout=TIMEOUT)
    assert not at.exception
    at.sidebar.slider(key="n_slider").set_value(8).run(timeout=TIMEOUT)
    assert not at.exception and at.number_input(key="trace_prisoner").value == 8


def test_main_verdict_is_a_hook_with_the_exact_numbers():
    at = _fresh_app()
    text = " ".join(i.value for i in at.info)
    assert "31,2 %" in text and "7,9·10⁻³¹" in text and "50,0 %" in text
