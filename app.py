"""Die 100 Gefangenen und die Kästen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Ein Teamrätsel: ein Team mit gemeinsamem Ziel, einer vorab abgesprochenen Strategie und beschränkter Information. Hier die Aufgabe der 100 Gefangenen, die in Kästen nach ihrer
eigenen Nummer suchen: mit der Zyklus-Strategie gewinnt das Team mit rund 31 %, obwohl jeder Einzelne nur eine Chance von 50 % hat.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import gfk_constants as C
import gfk_cycles as Y
import gfk_evaluation as V
import gfk_experiments as XP
import gfk_scenario as S
import gfk_visualization as Z
from gfk_layout import dunkles_design, kopf_css
from gfk_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)

st.set_page_config(page_title="Die 100 Gefangenen und die Kästen – Sebastian Hanisch", layout="wide")


# --- Zwischenspeicher (Schlüssel = alle Eingaben inklusive Zufalls-Seed) --------------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def _analyse(s):
    return V.analyse(s)


@st.cache_data(show_spinner=False)
def _e1_curve(n):
    return XP.e1_curve(n)


@st.cache_data(show_spinner=False)
def _e1_rows(n):
    return XP.e1_rows(n)


@st.cache_data(show_spinner=False)
def _e1_live(n, runs, seed):
    return XP.e1_live(n, runs, seed)


@st.cache_data(show_spinner=False)
def _e2_rows():
    return XP.e2_rows()


@st.cache_data(show_spinner=False)
def _e2_live(runs, seed):
    return XP.e2_live(runs, seed)


@st.cache_data(show_spinner=False)
def _e3_exact(n, share):
    return XP.e3_exact(n, share)


@st.cache_data(show_spinner=False)
def _e3_live(n, share, runs, seed):
    return XP.e3_live(n, share, runs, seed)


@st.cache_data(show_spinner=False)
def _e4_rows(n):
    return XP.e4_rows(n)


@st.cache_data(show_spinner=False)
def _e4_live(n, runs, seed):
    return XP.e4_live(n, runs, seed)


def show(verdict):
    kind, text = verdict
    getattr(st, kind)(text)


def table(rows):
    st.dataframe(rows, hide_index=True, width="stretch")


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in gfk_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🗝️ Die 100 Gefangenen und die Kästen")
st.markdown(
    """
**Ein Teamrätsel.** Ein Team hat ein gemeinsames Ziel, darf vorher eine Strategie absprechen und handelt dann ohne Verständigung. Hier: **100 Gefangene** suchen in **100 Kästen**
je den Zettel mit ihrer eigenen Nummer; jeder darf höchstens **50 Kästen** öffnen, alle zusammen gewinnen nur, wenn **jeder** seinen Zettel findet. Wer rät, hat als Team nur die Chance
0,5 hoch 100 (7,9·10⁻³¹). Wer nach der **Zyklus-Strategie** sucht, gewinnt mit rund **31 %**, und jeder Einzelne hat dabei trotzdem nur die Chance **50 %**: **die Chancen sind gleich, nur die Erfolge sind gekoppelt.**

Die Demo vergleicht drei Strategien (**Zufall**, **feste Kästen**, **Zyklus**), zeigt die **Zyklen** der Anordnung, fragt, was ein **Wärter** ausrichtet, der die Strategie kennt, und was ein **Helfer** bringt,
der vorab zwei Zettel vertauschen darf. Gerechnet wird exakt (Rekursion über die Zyklen) und nachgespielt (Simulation); das Rätsel ist ein **Lehrbuchresultat**, die Demo ordnet es nur ein.
**Das Modell ist eine Rechenaufgabe mit idealisierten Annahmen, keine Aussage über Menschen.**

Weiter unten: vier Tabs mit je einem **🔬 Experiment**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Zyklus-Strategie", expanded=True):
    st.markdown(
        """
1. **Die Regeln.** In den Kästen 1 bis n liegen die Zettel 1 bis n, jeder genau einmal, in zufälliger Anordnung. Gefangener *i* sucht den Zettel *i*. Er öffnet höchstens *m* Kästen, danach ist er fertig.
   Verständigen dürfen sich die Gefangenen nur vorab, danach nicht mehr.
2. **Die Regel der Strategie.** Gefangener *i* öffnet zuerst **Kasten *i*** (seine eigene Nummer). Liegt dort der Zettel *j*, öffnet er als Nächstes **Kasten *j***, usw.
3. **Warum das trägt.** Folgt man den Zetteln von Kasten zu Kasten, läuft man im Kreis (ein **Zyklus** der Anordnung). Der Zettel *i* liegt im Kasten **vor** Kasten *i* im Zyklus, also nach genau
   so vielen Öffnungen, wie der Zyklus Kästen hat. **Gefangener *i* hat Erfolg genau dann, wenn sein Zyklus höchstens *m* Kästen lang ist.**
4. **Das Team gewinnt, wenn kein Zyklus länger als *m* ist.** Bei *m* ≥ *n*/2 kann es höchstens einen langen Zyklus geben; die Chance zu gewinnen ist dann 1 − (1/(m+1) + … + 1/n), bei 100 Gefangenen und
   *m* = 50 gleich 31,2 %. Mit *m* = *n*/2 sinkt sie bei wachsender Gefangenenzahl auf den Grenzwert 1 − ln 2 = 30,7 %.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Das Rätsel**")
    n = st.slider("Zahl der Gefangenen n", *bounds("n_slider"), key="n_slider", step=1, help="So viele Gefangene und Kästen gibt es. Das klassische Rätsel hat 100.")
    share = st.slider("Erlaubte Kästen je Gefangenem (% von n)", *bounds("share_slider"), key="share_slider", step=1,
                      help="Wie viele Kästen jeder öffnen darf, in Prozent von n und auf ganze Kästen gerundet (50 % ergeben bei 100 Gefangenen 50 Kästen). Bei 100 % sind alle Kästen offen.")
    st.markdown("**Wärter und Helfer**")
    warden = st.selectbox("Wer legt die Zettel?", C.WARDENS, key="warden_select", format_func=C.WARDEN_LABELS.get,
                          help="Zufall: gleichverteilt. Wärter: er kennt die Strategie und wählt die Anordnung, die sie scheitern lässt. Mit geheimer Umnummerierung hat das Team vorab die Kästen untereinander "
                               "zufällig umbenannt, was der Wärter nicht kennt.")
    swaps = st.slider("Vertauschungen durch einen Helfer vorab", *bounds("swaps_slider"), key="swaps_slider", step=1,
                      help="Ein Helfer sieht alle Zettel und darf vor Beginn die Zettel zweier Kästen vertauschen, bis zu so oft. Er greift nur ein, wenn es reicht, damit alle Erfolg haben. "
                           "Wirkt nur auf die Zyklus-Strategie.")
    st.markdown("**Simulation**")
    runs = st.slider("Simulationsläufe", *bounds("runs_slider"), key="runs_slider", step=C.RUNS_STEP, help="So viele Anordnungen werden durchgespielt. Die exakten Werte hängen nicht daran.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)
    st.button("🎲 Neuen Zufalls-Seed ziehen", width="stretch", on_click=randomize_seed)

sync_query_params({"n_slider": int(n), "share_slider": int(share), "warden_select": warden, "swaps_slider": int(swaps), "runs_slider": int(runs), "seed_input": int(seed)})

settings = S.Settings(n=int(n), share=int(share), warden=warden, swaps=int(swaps), runs=int(runs), seed=int(seed))
with st.spinner(f"Spiele {V.thousands(settings.runs)} Anordnungen durch (rund {S.estimated_seconds(settings.n, settings.runs)} Sekunden) …"):
    view = _analyse(settings)
m = view.m
verdicts = []   # Verdikte für den PDF-Export

# --- Hauptansicht --------------------------------------------------------------------------------------------------------------------------
st.markdown("## 📊 Drei Strategien, gleiche Einzelchance")
cols = st.columns(3)
for col, name in zip(cols, C.STRATEGIES):
    ex = view.exact[name]
    single = "Einzelchance: nicht gerechnet" if ex.p_single is None else f"Einzelchance {V.pct(ex.p_single, 1)}"
    col.metric(f"{name}: alle haben Erfolg", V.prob(ex.p_all) if ex.p_all is not None else "–", delta=single, delta_color="off",
               help="Wahrscheinlichkeit, dass jeder Gefangene seinen Zettel findet (exakt gerechnet; bei festen Kästen nur bis n = 20). Darunter die Chance eines einzelnen Gefangenen.")

st.markdown("#### ❓ Kernfrage: Warum gewinnt das Team, obwohl jeder nur 50 % hat?")
v_hook = V.verdict_hook(view)
show(v_hook)
verdicts.append(v_hook)

table_data = V.table_rows(view)
st.dataframe(table_data, hide_index=True, width="stretch", column_config={
    "Einzelchance (exakt)": st.column_config.NumberColumn(format="%.1f %%"),
    "Einzelchance (Simulation)": st.column_config.NumberColumn(format="%.1f %%"),
})
st.caption(f"Gespielt: {V.thousands(settings.runs)} Anordnungen mit Zufalls-Seed {settings.seed}. Die Einzelchance ist der Anteil der Gefangenen mit Erfolg. "
           "„Exakt“ ist gerechnet (Rekursion über die Zyklen, Binomialformel, Permanent), „Simulation“ ist gezählt.")

st.plotly_chart(Z.build_pmf(settings.n, view.pmf_cycle, view.pmf_random, view.hist_fixed), width="stretch", key="pmf_chart")
st.caption(f"Wie viele Gefangene Erfolg haben. **Zufall** (Linie, Binomial): eine Glockenform um den Mittelwert; alle zusammen: {V.prob(view.exact[C.STRAT_RANDOM].p_all)}. **Zyklus-Strategie** (Balken): die Erfolge sind gekoppelt, "
           "ganz rechts alle zusammen, sonst bricht eine ganze Gruppe weg (bei m ≥ n/2 scheitern genau so viele, wie der eine zu lange Zyklus Kästen hat). **Feste Kästen** (Punkte): simuliert.")

# --- Die Zyklen ----------------------------------------------------------------------------------------------------------------------------
st.markdown("## 🔁 Die Zyklen einer Anordnung")
ex_ = view.example
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(Z.build_cycles(list(ex_.lengths), m), width="stretch", key="cycles_chart")
    st.caption(f"Eine Anordnung aus dem Zufalls-Seed {settings.seed} ({'aus Sicht des Teams' if settings.warden != C.WARDEN_RANDOM else 'zufällig gezogen'}): {len(ex_.lengths)} Zyklen, "
               f"erwartet im Mittel H_n = {V.de(sum(1 / k for k in range(1, settings.n + 1)), 2)}. Rot: länger als m.")
with c2:
    st.plotly_chart(Z.build_longest(list(view.longest_pmf), m), width="stretch", key="longest_chart")
    st.caption(f"Wie lang der längste Zyklus einer **zufälligen** Anordnung von {settings.n} Kästen wird (exakt). Die roten Balken (länger als m) summieren sich zur Misserfolgschance der Zyklus-Strategie.")
show_cycles = V.verdict_cycles(view)
show(show_cycles)
verdicts.append(show_cycles)

st.markdown("**Der Weg eines Gefangenen**")
if st.session_state.get("trace_prisoner", 1) > settings.n:
    st.session_state["trace_prisoner"] = settings.n
prisoner = int(st.number_input("Gefangener Nr.", 1, settings.n, key="trace_prisoner", step=1)) - 1
start = ex_.after if ex_.plan else ex_.q
opened, found = Y.follow_boxes(list(start), prisoner, m)
table([{"Öffnung": i + 1, "Kasten": b + 1, "Zettel darin": z + 1, "eigener Zettel": "ja" if z == prisoner else "nein"} for i, (b, z) in enumerate(opened)])
show(V.verdict_trace(opened, found, prisoner, m))
st.caption("Die Anordnung ist die oben gezeigte" + (", nachdem der Helfer die genannten Zettel vertauscht hat" if ex_.plan else "") + ". Nummern ab 1.")

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["1 Wie viele Kästen?", "2 Wie viele Gefangene?", "3 Der Wärter", "4 Ein Helfer vertauscht vorab"])

# --- Tab 1 ---------------------------------------------------------------------------------------------------------------------------------
with tab1:
    st.subheader("🔬 Experiment E1: Wie viele Kästen braucht das Team?")
    st.caption(f"Exakte Gewinnchance über die Zahl der erlaubten Kästen m, für n = {settings.n} Gefangene und zufällige Zettel (kein Wärter, kein Helfer).")
    curve = _e1_curve(settings.n)
    st.plotly_chart(Z.build_e1(curve, settings.n, m), width="stretch", key="e1_chart")
    rows1 = _e1_rows(settings.n)
    table([{"Anteil der Kästen": f"{r['share']} %", "m": r["m"], "Einzelchance": V.pct(r["single"], 1), "Zyklus-Strategie: alle": V.prob(r["cycle"]), "Zufall: alle": V.prob(r["random"])} for r in rows1])
    v1 = XP.verdict_e1(rows1, settings.n)
    show(v1)
    verdicts.append(v1)
    est1 = S.estimated_seconds(settings.n, settings.runs, len(C.E1_SHARES))
    st.markdown("**Mit den Reglern nachspielen** (n und Läufe aus der Seitenleiste, zufällige Zettel, Zyklus-Strategie)")
    if st.button("▶️ Anteile nachspielen", key="e1_button", help=f"{len(C.E1_SHARES)} Simulationen mit je {V.thousands(settings.runs)} Läufen; rechnet rund {est1} Sekunden."):
        st.session_state["e1_signature"] = (settings.n, settings.runs, settings.seed)
    if st.session_state.get("e1_signature") == (settings.n, settings.runs, settings.seed):
        with st.spinner(f"Spiele {len(C.E1_SHARES)} Reihen durch (rund {est1} Sekunden) …"):
            live1 = _e1_live(settings.n, settings.runs, settings.seed)
        table([{"Anteil der Kästen": f"{r['share']} %", "m": r["m"], "exakt": V.prob(x["cycle"]), "gespielt": f"{V.thousands(r['hits'])} von {V.thousands(r['runs'])}", "Anteil": V.prob(r["hits"] / r["runs"])}
               for r, x in zip(live1, rows1)])
        st.caption("Bei seltenen Ereignissen ist der gezählte Anteil grob: wenige Treffer sagen wenig (0 Treffer heißt nur: seltener als etwa 1 von den gespielten Läufen).")

# --- Tab 2 ---------------------------------------------------------------------------------------------------------------------------------
with tab2:
    st.subheader("🔬 Experiment E2: Wie viele Gefangene?")
    st.caption("Mit der Hälfte der Kästen je Person (m = n/2, gerade n) und zufälligen Zetteln: die exakte Gewinnchance der Zyklus-Strategie über die Zahl der Gefangenen. n und Anteil der Seitenleiste gelten hier nicht.")
    rows2 = _e2_rows()
    st.plotly_chart(Z.build_e2(rows2, XP.e2_limit()), width="stretch", key="e2_chart")
    table([{"Gefangene n": r["n"], "m = n/2": r["m"], "Zyklus-Strategie: alle": V.prob(r["cycle"]), "Zufall: alle": V.prob(r["random"]), "Abstand zu 1 − ln 2": f"{V.de(100 * (r['cycle'] - XP.e2_limit()), 2)} Prozentpunkte"} for r in rows2])
    v2 = XP.verdict_e2(rows2)
    show(v2)
    verdicts.append(v2)
    est2 = S.estimated_seconds(sum(r["n"] for r in rows2), settings.runs)
    st.markdown("**Mit den Reglern nachspielen** (Läufe aus der Seitenleiste)")
    if st.button("▶️ Gefangenenzahlen nachspielen", key="e2_button", help=f"{len(rows2)} Simulationen mit je {V.thousands(settings.runs)} Läufen; rechnet rund {est2} Sekunden."):
        st.session_state["e2_signature"] = (settings.runs, settings.seed)
    if st.session_state.get("e2_signature") == (settings.runs, settings.seed):
        with st.spinner(f"Spiele {len(rows2)} Reihen durch (rund {est2} Sekunden) …"):
            live2 = _e2_live(settings.runs, settings.seed)
        table([{"Gefangene n": r["n"], "exakt": V.prob(x["cycle"]), "gespielt": f"{V.thousands(r['hits'])} von {V.thousands(r['runs'])}", "Anteil": V.prob(r["hits"] / r["runs"])} for r, x in zip(live2, rows2)])

# --- Tab 3 ---------------------------------------------------------------------------------------------------------------------------------
with tab3:
    st.subheader("🔬 Experiment E3: Der Wärter kennt die Strategie")
    st.caption(f"n = {settings.n} Gefangene, {m} Kästen je Person ({settings.share} %), ohne Helfer. Drei Fälle: die Zettel liegen **zufällig**; der **Wärter** kennt die vereinbarte Strategie und legt die Zettel so, dass sie "
               "versagt (gegen die Zyklus-Strategie ein einziger Zyklus aus n Kästen, gegen feste Kästen jeder Zettel knapp außerhalb des Fensters); das Team hat die Kästen **geheim umnummeriert**.")
    ex3 = _e3_exact(settings.n, settings.share)
    names3 = {C.WARDEN_RANDOM: "Zufällige Zettel", C.WARDEN_KNOWS: "Wärter kennt die Strategie", C.WARDEN_SECRET: "Wärter, Kästen geheim umnummeriert"}
    table([{"Strategie": strat, **{names3[w]: V.prob(ex3[w][strat]) for w in C.WARDENS}} for strat in C.STRATEGIES])
    v3 = XP.verdict_e3(ex3, settings.n, m)
    show(v3)
    verdicts.append(v3)
    est3 = S.estimated_seconds(settings.n, settings.runs, 3)
    st.markdown("**Mit den Reglern nachspielen** (n, Anteil, Läufe aus der Seitenleiste, ohne Helfer)")
    if st.button("▶️ Drei Fälle nachspielen", key="e3_button", help=f"3 Simulationen mit je {V.thousands(settings.runs)} Läufen; rechnet rund {est3} Sekunden."):
        st.session_state["e3_signature"] = (settings.n, settings.share, settings.runs, settings.seed)
    if st.session_state.get("e3_signature") == (settings.n, settings.share, settings.runs, settings.seed):
        with st.spinner(f"Spiele drei Fälle durch (rund {est3} Sekunden) …"):
            live3 = _e3_live(settings.n, settings.share, settings.runs, settings.seed)
        table([{"Strategie": strat, **{names3[w]: f"{V.thousands(live3[w][strat])} von {V.thousands(live3[w]['runs'])}" for w in C.WARDENS}} for strat in C.STRATEGIES])
        st.caption("Gezählt: Läufe, in denen alle Gefangenen Erfolg haben. Der Wärter legt in jedem Lauf dieselbe Anordnung; die geheime Umnummerierung wird in jedem Lauf neu gezogen.")

# --- Tab 4 ---------------------------------------------------------------------------------------------------------------------------------
with tab4:
    st.subheader("🔬 Experiment E4: Ein Helfer vertauscht vorab")
    st.caption(f"Ein Helfer sieht alle Zettel und darf vor Beginn die Zettel zweier Kästen vertauschen, bis zu k-mal (0 bis {C.SWAPS_MAX}); er greift nur ein, wenn es für ein Gelingen aller reicht. "
               f"n = {settings.n} Gefangene, zufällige Zettel, vier Anteile erlaubter Kästen. Eine Vertauschung innerhalb eines Zyklus teilt ihn in zwei Stücke, ein Zyklus der Länge L braucht ⌈L/m⌉ − 1 Vertauschungen.")
    rows4 = _e4_rows(settings.n)
    st.plotly_chart(Z.build_e4(rows4), width="stretch", key="e4_chart")
    table([{"Anteil der Kästen": f"{r['share']} %", "m": r["m"], **{("keine Vertauschung" if k == 0 else f"{k} Vertauschung" + ("en" if k > 1 else "")): V.prob(p) for k, p in enumerate(r["p"])},
            "ein einziger Zyklus braucht": r["worst"]} for r in rows4])
    v4 = XP.verdict_e4(rows4, settings.n)
    show(v4)
    verdicts.append(v4)
    est4 = S.estimated_seconds(settings.n, settings.runs, len(C.E4_SHARES))
    st.markdown("**Mit den Reglern nachspielen** (n und Läufe aus der Seitenleiste, zufällige Zettel)")
    if st.button("▶️ Vertauschungen nachspielen", key="e4_button", help=f"{len(C.E4_SHARES)} Simulationen mit je {V.thousands(settings.runs)} Läufen; rechnet rund {est4} Sekunden."):
        st.session_state["e4_signature"] = (settings.n, settings.runs, settings.seed)
    if st.session_state.get("e4_signature") == (settings.n, settings.runs, settings.seed):
        with st.spinner(f"Spiele {len(C.E4_SHARES)} Reihen durch (rund {est4} Sekunden) …"):
            live4 = _e4_live(settings.n, settings.runs, settings.seed)
        table([{"Anteil der Kästen": f"{r['share']} %", "m": r["m"], **{f"k = {k}": f"{V.thousands(h)} von {V.thousands(r['runs'])}" for k, h in enumerate(r["hits"])}} for r in live4])

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------
st.markdown("---")
st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Die Zettel liegen gleichverteilt** (alle Anordnungen gleich wahrscheinlich) | Bei einem Wärter, der die Strategie kennt, scheitert die Zyklus-Strategie für m < n ohne Helfer sicher (E3). Eine geheime gemeinsame Umnummerierung stellt die Gleichverteilung her: das Team braucht dafür vorab einen gemeinsamen Zufall. | – |
| **Eine Strategie wird vorab festgelegt, danach keine Verständigung** | Dürften die Gefangenen nach dem ersten Öffnen etwas mitteilen, wäre das ein anderes Rätsel (hier nicht gerechnet). | – |
| **Alle haben dasselbe m** | Für ungleiche Zahlen erlaubter Kästen ist hier nichts gerechnet und die Optimalität der Zyklus-Strategie nicht untersucht. | – |
| **Optimalität** | Dass keine Strategie die Zyklus-Strategie übertrifft, wird laut Sekundärquellen in der Literatur bewiesen (Curtin und Warshauer; deren Volltext wurde nicht gelesen, Quellenangabe in der README) und ist hier weder bewiesen noch übernommen. Die Demo prüft das nur durch Aufzählung aller Strategien in den Tests, für n = 3 und n = 4 mit höchstens 2 Kästen je Person. | – |
| **Der Helfer sieht alle Zettel** | Er greift nur ein, wenn die erlaubten Vertauschungen für ein Gelingen aller reichen; andernfalls bleibt die Anordnung, wie sie ist. Seine Wirkung ist nur für die Zyklus-Strategie gerechnet (bei Zufall wäre er wirkungslos, bei festen Kästen nicht). | – |
| **Feste Kästen sind ein Beispiel** | Gemeint sind die Fenster „Kasten i bis i + m − 1“; andere feste Zuordnungen haben andere Zahlen (die Anzahl passender Anordnungen ist stets der Permanent der Zuordnungsmatrix). Exakt nur bis n = 20. | – |
| **Menschen und Gefängnisse** | Die Aufgabe ist ein Gedankenspiel; die Demo sagt nichts über Menschen, Gedächtnis oder Aufsicht. | – |
    """
)

st.markdown("---")
with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Lesehilfe.** Gegeben sind $n$ Gefangene und $n$ Kästen, in denen die Zettel $1, \dots, n$ in einer gleichverteilten Anordnung $q$ liegen; jeder Gefangene darf $m$ Kästen öffnen.
Gesucht ist die Wahrscheinlichkeit, dass **alle** ihren Zettel finden. Alles hier ist eigene Rechnung, durch Aufzählung aller Anordnungen bis $n = 9$ und durch zweite Rechenwege gestützt;
der Beweis der Optimalität ist Literatur (README).

| Symbol | Bedeutung |
|---|---|
| $q(j)$ | der Zettel in Kasten $j$ (eine Permutation von $1, \dots, n$) |
| $\ell_i$ | Länge des Zyklus von $q$, der $i$ enthält |
| $m$ | erlaubte Kästen je Gefangenem, hier $m = \lfloor n \cdot \text{Anteil} + \tfrac{1}{2} \rfloor$ (halbe Kästen werden aufgerundet, mindestens 1, höchstens $n$) |
| $\rho$ | geheime Umnummerierung der Kästen (nur im dritten Fall) |
| $c(q)$ | Vertauschungen, die ein Helfer braucht, damit kein Zyklus länger als $m$ ist |

**Zyklus-Strategie.** Gefangener $i$ öffnet Kasten $i$, dann Kasten $q(i)$, dann $q(q(i))$, usw. Der Zettel $i$ liegt in dem Kasten, der im Zyklus vor $i$ steht, also nach $\ell_i$ Öffnungen:

$$\text{Gefangener } i \text{ hat Erfolg} \iff \ell_i \le m$$

**Einzelchance.** In einer gleichverteilten Anordnung ist die Länge des Zyklus eines festen Kastens gleichverteilt auf $1, \dots, n$ (Rekursion unten), also

$$\Pr(\ell_i \le m) = \frac{m}{n}$$

**Alle zusammen.** Das Team gewinnt genau dann, wenn kein Zyklus länger als $m$ ist. Für $m \ge n/2$ kann es höchstens einen langen Zyklus geben, und genau $n!/k$ Anordnungen haben einen Zyklus der Länge $k > n/2$:

$$\Pr(\text{alle}) = 1 - \sum_{k=m+1}^{n} \frac{1}{k}$$

**Grenzwert** für $n = 2m \to \infty$ (Differenz zweier harmonischer Zahlen):

$$1 - \sum_{k=m+1}^{2m} \frac{1}{k} \;\longrightarrow\; 1 - \ln 2 \approx 0{,}3069$$

**Rekursion für beliebiges $m$.** Der Zyklus des ersten Kastens hat jede Länge $k = 1, \dots, N$ mit Wahrscheinlichkeit $1/N$, der Rest ist wieder gleichverteilt. Mit $F_m(N)$ als Wahrscheinlichkeit, dass keiner von $N$ Kästen in einem Zyklus über $m$ liegt:

$$F_m(N) = \frac{1}{N} \sum_{k=1}^{\min(m, N)} F_m(N - k), \qquad F_m(0) = 1$$

Dieselbe Rekursion mit einer zweiten Größe liefert die Verteilung der Zahl erfolgreicher Gefangener und der Vertauschungskosten $c$ gemeinsam.

**Zufall und feste Kästen.** Wählt jeder zufällig $m$ Kästen, sind die Erfolge unabhängig mit Wahrscheinlichkeit $m/n$:

$$\Pr(\text{alle}) = \left(\frac{m}{n}\right)^{n}$$

Bei festen Kästen (Matrix $A$ mit $A_{ij} = 1$, wenn Gefangener $i$ den Kasten $j$ öffnet) gewinnt das Team genau in den Anordnungen, in denen jeder Zettel in einem Kasten seines Gefangenen liegt:

$$\Pr(\text{alle}) = \frac{\operatorname{perm}(A)}{n!}, \qquad \operatorname{perm}(A) = \sum_{\pi} \prod_{i=1}^{n} A_{i,\pi(i)}$$

**Geheime Umnummerierung.** Nennt das Team den Kasten $j$ in Wirklichkeit $\rho(j)$, sieht es die Anordnung $q \circ \rho$. Ist $\rho$ gleichverteilt, ist $q \circ \rho$ für **jedes** feste $q$ gleichverteilt:

$$\Pr(\text{alle}) = 1 - \sum_{k=m+1}^{n} \frac{1}{k} \quad \text{für jede Anordnung } q \text{ des Wärters (} m \ge n/2 \text{)}$$

**Vertauschungen vorab.** Eine Vertauschung innerhalb eines Zyklus teilt ihn in zwei beliebige Stücke, eine zwischen zwei Zyklen verschmilzt sie. Die Mindestzahl der Vertauschungen, bis kein Zyklus länger als $m$ ist, ist

$$c(q) = \sum_{\text{Zyklen}} \left( \left\lceil \frac{\ell}{m} \right\rceil - 1 \right)$$

**Literatur.** Die Quellen stehen in der README mit dem Stand der Prüfung; Formeln und Zahlen dieser Demo sind eigene Rechnung.
        """
    )

st.markdown("---")
st.subheader("📄 Ergebnisse als PDF")
if st.button("PDF erstellen", key="pdf_button"):
    from gfk_pdf_export import build_pdf
    st.session_state["pdf_bytes"] = build_pdf(view, verdicts)
if st.session_state.get("pdf_bytes"):
    st.download_button("⬇️ PDF herunterladen", st.session_state["pdf_bytes"], file_name="gefangene-kaesten.pdf", mime="application/pdf", key="pdf_download")

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
