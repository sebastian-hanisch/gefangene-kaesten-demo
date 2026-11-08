"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Strategientabelle und Verdikte. Erst nach Klick erzeugt (DEMO-PLAYBOOK §1c)."""

from __future__ import annotations

from fpdf import FPDF

import gfk_constants as C
import gfk_evaluation as V

_REPLACE = {"–": "-", "—": "-", "≤": "<=", "≥": ">=", "≠": "!=", "²": "2", "Σ": "Summe", "·": "*", "−": "-", "„": '"', "“": '"', "→": "->", "×": "x", "≈": "~", "½": "1/2",
            "⁻": "^-", "¹": "1", "⁵": "5", "⁶": "6", "⁰": "0", "⁴": "4", "³": "3", "⁸": "8", "⁷": "7", "⁹": "9", "∈": "in", "…": "...", "’": "'", "”": '"', "⌈": "ceil(", "⌉": ")"}


def _latin(text: str) -> str:
    """Kernschriften kennen nur Latin-1: Sonderzeichen ersetzen, Markdown-Sterne entfernen."""
    for a, b in _REPLACE.items():
        text = text.replace(a, b)
    return text.replace("**", "").replace("`", "").encode("latin-1", "replace").decode("latin-1")


def build_pdf(view: V.MainView, verdicts: list[tuple[str, str]]) -> bytes:
    s = view.settings
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _latin("Die 100 Gefangenen und die Kästen"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _latin(f"{s.n} Gefangene, {view.m} erlaubte Kästen je Person ({s.share} % von n); {C.WARDEN_LABELS[s.warden]}; Vertauschungen vorab: {s.swaps}; "
                                f"{V.thousands(s.runs)} Simulationsläufe; Zufalls-Seed {s.seed}."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Strategien", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for name in C.STRATEGIES:
        ex = view.exact[name]
        hits = V.sim_all(view, name)
        single = "nicht gerechnet" if ex.p_single is None else V.pct(ex.p_single, 1)
        pdf.multi_cell(0, 5, _latin(f"{name}: Einzelchance {single}; alle haben Erfolg: {V.prob(ex.p_all)} (Simulation: {V.thousands(hits)} von {V.thousands(view.sim.runs)} Läufen)."),
                       new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Verdikte", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for _, text in verdicts:
        pdf.multi_cell(0, 5, _latin(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _latin("Das Modell ist eine Rechenaufgabe mit idealisierten Annahmen (gleichverteilte Zettel, vorab abgesprochene Strategie, keine Verständigung während der Aufgabe), keine Aussage "
                                "über Menschen. Alle Zahlen sind eigene Rechnung, durch Aufzählung aller Anordnungen bei kleinen n, zweite Rechenwege und Simulation gestützt."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
