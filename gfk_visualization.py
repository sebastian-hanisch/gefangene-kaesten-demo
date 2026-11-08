"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import gfk_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=380):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_pmf(n, pmf_cycle, pmf_random, hist_fixed, cycle_label="Zyklus-Strategie (exakt)"):
    """Verteilung der Zahl erfolgreicher Gefangener: Zyklus-Strategie als Balken (exakt), Zufall als Linie (Binomial, exakt), feste Kästen als Punkte (Simulation)."""
    xs = list(range(n + 1))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=xs, y=[100 * float(p) for p in pmf_cycle], name=cycle_label, marker_color=C.COLOR_CYCLE, hovertemplate="%{x} erfolgreich: %{y:.2f} %<extra>Zyklus</extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100 * float(p) for p in pmf_random], mode="lines", name="Zufall (Binomial, exakt)", line=dict(color=C.COLOR_RANDOM, width=3),
                             hovertemplate="%{x} erfolgreich: %{y:.2f} %<extra>Zufall</extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[100 * float(p) for p in hist_fixed], mode="markers", name="Feste Kästen (Simulation)", marker=dict(color=C.COLOR_FIXED, size=6),
                             hovertemplate="%{x} erfolgreich: %{y:.2f} %<extra>Fest</extra>"))
    fig.update_xaxes(title_text="Gefangene mit Erfolg", range=[-1, n + 1])
    fig.update_yaxes(title_text="Wahrscheinlichkeit (%)")
    return _base(fig)


def build_cycles(lengths, m):
    """Die Zyklenlängen der gezeigten Anordnung, absteigend sortiert; zu lange Zyklen (länger als m) sind rot."""
    ordered = sorted(lengths, reverse=True)
    labels = [f"Z{i + 1}" for i in range(len(ordered))]
    colors = [C.COLOR_BAD if length > m else C.COLOR_GOOD for length in ordered]
    fig = go.Figure(go.Bar(x=labels, y=ordered, marker_color=colors, hovertemplate="%{x}: Länge %{y}<extra></extra>", name="Zyklenlänge"))
    fig.add_hline(y=m, line_dash="dash", line_color=C.COLOR_LINE, annotation_text=f"erlaubt: m = {m}", annotation_position="top right")
    fig.update_xaxes(title_text="Zyklen der Anordnung, nach Länge geordnet")
    fig.update_yaxes(title_text="Kästen im Zyklus", rangemode="tozero")
    return _base(fig, 340)


def build_longest(pmf, m):
    """Verteilung des längsten Zyklus einer zufälligen Anordnung; Längen über m (die Zyklus-Strategie scheitert) rot."""
    xs = list(range(1, len(pmf)))
    colors = [C.COLOR_BAD if length > m else C.COLOR_GOOD for length in xs]
    fig = go.Figure(go.Bar(x=xs, y=[100 * float(pmf[L]) for L in xs], marker_color=colors, hovertemplate="längster Zyklus %{x}: %{y:.2f} %<extra></extra>", name="längster Zyklus"))
    fig.add_vline(x=m + 0.5, line_dash="dash", line_color=C.COLOR_LINE, annotation_text=f"m = {m}", annotation_position="top")
    fig.update_xaxes(title_text="Länge des längsten Zyklus", range=[0, len(pmf)])
    fig.update_yaxes(title_text="Wahrscheinlichkeit (%)", rangemode="tozero")
    return _base(fig, 340)


def build_e1(curve, n, m_now):
    """Gewinnchance über die Zahl der erlaubten Kästen: Zyklus-Strategie und Zufall, jeweils exakt."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curve["m"], y=[100 * p for p in curve["cycle"]], mode="lines", name="Zyklus-Strategie", line=dict(color=C.COLOR_CYCLE, width=3),
                             hovertemplate="m = %{x}: %{y:.3f} %<extra>Zyklus</extra>"))
    fig.add_trace(go.Scatter(x=curve["m"], y=[100 * p for p in curve["random"]], mode="lines", name="Zufall", line=dict(color=C.COLOR_RANDOM, width=3),
                             hovertemplate="m = %{x}: %{y:.3g} %<extra>Zufall</extra>"))
    fig.add_vline(x=n / 2, line_dash="dot", line_color="rgba(128,128,128,0.8)", annotation_text="n/2", annotation_position="top")
    fig.add_vline(x=m_now, line_dash="dash", line_color=C.COLOR_LINE, annotation_text=f"Regler: m = {m_now}", annotation_position="bottom right")
    fig.update_xaxes(title_text="Erlaubte Kästen je Gefangenem m", range=[0, n + 1])
    fig.update_yaxes(title_text="Alle haben Erfolg (%)", range=[-2, 102])
    return _base(fig)


def build_e2(rows, limit):
    """Gewinnchance der Zyklus-Strategie bei m = n/2 über die Zahl der Gefangenen, mit Grenzwert 1 − ln 2."""
    xs = [r["n"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=[100 * r["cycle"] for r in rows], mode="lines+markers", name="Zyklus-Strategie, m = n/2", line=dict(color=C.COLOR_CYCLE, width=3),
                             hovertemplate="n = %{x}: %{y:.2f} %<extra></extra>"))
    fig.add_hline(y=100 * limit, line_dash="dash", line_color=C.COLOR_LINE, annotation_text=f"Grenzwert 1 − ln 2 = {100 * limit:.2f} %".replace(".", ","), annotation_position="top right")
    fig.update_xaxes(title_text="Zahl der Gefangenen n", range=[0, max(xs) + 2])
    fig.update_yaxes(title_text="Alle haben Erfolg (%)", range=[0, 55])
    return _base(fig)


def build_e4(rows):
    """Gewinnchance über die Zahl der Vertauschungen (0 bis 3), je ein Balkensatz für jeden Anteil erlaubter Kästen."""
    fig = go.Figure()
    palette = [C.COLOR_CYCLE, C.COLOR_LINE, C.COLOR_FIXED, C.COLOR_RANDOM]
    for color, r in zip(palette, rows):
        ks = list(range(len(r["p"])))
        fig.add_trace(go.Bar(x=[f"{k} Vertauschungen" if k != 1 else "1 Vertauschung" for k in ks], y=[100 * p for p in r["p"]], name=f"{r['share']} % der Kästen (m = {r['m']})", marker_color=color,
                             hovertemplate="%{x}: %{y:.2f} %<extra>" + f"m = {r['m']}" + "</extra>"))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Alle haben Erfolg (%)", range=[0, 105])
    return _base(fig)
