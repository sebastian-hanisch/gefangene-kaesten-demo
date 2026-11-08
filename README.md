# Die 100 Gefangenen und die Kästen – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-gefangene-kaesten-demo.streamlit.app/)**

Erstes Stück der Reihe **„Teamrätsel“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Ein Team hat **ein gemeinsames Ziel**, darf **vorher eine Strategie absprechen** und handelt dann **ohne Verständigung**. Das Rätsel hier ist ein **Lehrbuchresultat** (bekannt); die Demo rechnet es exakt nach, zeigt die Zyklen, vergleicht drei Strategien und fragt, was ein Wärter und was ein Helfer ändern. Es ist eine **Rechenaufgabe mit idealisierten Annahmen, keine Aussage über Menschen.**

## Warum dieses Problem

100 Gefangene, 100 Kästen mit je einem Zettel mit einer Gefangenennummer (zufällig verteilt). Jeder darf höchstens 50 Kästen öffnen und seinen Zettel suchen; alle zusammen gewinnen nur, wenn **jeder** seinen findet. Wer zufällig 50 Kästen wählt, hat als Team die Chance 7,9·10⁻³¹ (jeder 50 %, unabhängig, 0,5 hoch 100). Wer nach der **Zyklus-Strategie** sucht (zuerst den Kasten mit der eigenen Nummer, dann den Kasten, dessen Nummer auf dem gefundenen Zettel steht), gewinnt mit **31,2 %**, und jeder Einzelne hat dabei trotzdem nur die Chance 50 %. Die Kernfrage: **warum ist das möglich?** Weil die Chancen gleich bleiben und nur die **Erfolge gekoppelt** sind: Es haben entweder alle Erfolg oder ganze Gruppen zusammen keinen.

Die Demo ordnet das ein: Wie viele Kästen braucht das Team (E1), hängt der Wert an der Zahl der Gefangenen (E2), was ändert ein Wärter, der die Strategie kennt, und was hilft dagegen (E3), und was bringt ein Helfer, der vorab zwei Zettel vertauscht (E4)?

## Modell

- **Anordnung.** Kasten *j* enthält den Zettel *q(j)*, eine gleichverteilte Permutation von 1 bis *n*. Gefangener *i* sucht den Zettel *i* und darf *m* Kästen öffnen. Die App stellt *m* als Anteil von *n* in Prozent ein und rundet auf ganze Kästen, halbe Kästen werden aufgerundet (50 % bei 7 Gefangenen ergeben 4 Kästen).
- **Drei Strategien.** *Zufall*: jeder wählt *m* Kästen zufällig. *Feste Kästen*: Gefangener *i* öffnet die Kästen *i*, *i* + 1, …, *i* + *m* − 1 (zyklisch), ein Beispiel für eine feste Zuordnung ohne Nachschlagen. *Zyklus-Strategie*: wie oben.
- **Wer legt die Zettel?** Zufall; der **Wärter**, der die Strategie kennt (gegen die Zyklus-Strategie ein einziger Zyklus aus *n* Kästen, gegen feste Kästen jeder Zettel knapp außerhalb des Fensters); der Wärter, aber das Team hat die Kästen vorab **geheim umnummeriert** (es nennt den Kasten *j* in Wirklichkeit ρ(*j*) und sieht die Anordnung *q∘ρ*).
- **Helfer.** Ein Helfer sieht alle Zettel und darf vor Beginn bis zu *k* Mal (0 bis 3) die Zettel zweier Kästen vertauschen. Er greift nur ein, wenn die Vertauschungen für ein Gelingen aller reichen; gerechnet wird seine Wirkung nur für die Zyklus-Strategie (bei Zufall wäre er wirkungslos, bei festen Kästen nicht).
- **Exakt und gespielt.** Die Gewinnchance der Zyklus-Strategie kommt aus einer Rekursion über den Zyklus des ersten Kastens (jede Länge hat die Wahrscheinlichkeit 1/*N*); daneben läuft eine Simulation mit SplitMix64 (feste Zufalls-Seeds). Die Zufalls-Strategie ist (*m*/*n*)ⁿ; die Gewinnchance fester Kästen ist der Permanent der Zuordnungsmatrix geteilt durch *n*!, **exakt gerechnet nur bis n = 20**. Mathematik und Annahmen: Expander **📐 Mathematische Formulierung** und Abschnitt **🚧 Wo die Annahmen enden** in der App.

## Methodik

| Einheit | Datei | Anmerkung |
|---|---|---|
| Zyklen, wörtliche Strategie, Vertauschungskosten und -plan | `gfk_cycles.py` | Zeigerverdopplung für viele Anordnungen; die wörtliche Fassung (`follow_boxes`) ist der Maßstab der Tests |
| Rekursionen und Formeln | `gfk_exact.py` | in Brüchen für die Tests (`exact=True`); Permanent fester Fenster per Teilmengen-DP |
| Simulation | `gfk_simulation.py` | vektorisiert, Blöcke zu 2.000 Läufen, eigener Strom je Zweck (`gfk_scenario.stream_seed`) |
| Kennzahlen, Verdikte | `gfk_evaluation.py` | Verdikte als reine Funktionen (Art, Text) |
| Experimente E1 bis E4 | `gfk_experiments.py` | exakte Reihen plus Nachspielen auf Knopfdruck |

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind eigene Rechnung unter den genannten Voraussetzungen (gleichverteilte Anordnung, Strategie vorab fest, alle dasselbe *m*), jede in `tests/test_claims.py` nachgerechnet.

| Frage | Befund |
|---|---|
| **Hook:** gemeinsame Chance bei 100 Gefangenen, 50 Kästen, zufällige Zettel | Zyklus-Strategie 31,2 % (Formel gleich Rekursion), Zufall 7,9·10⁻³¹; die Einzelchance ist bei allen drei Strategien 50 % (`test_claim_100_prisoners_50_boxes_cycle_strategy_wins_with_31_2_percent`, `…random_boxes…`, `…every_strategy_gives…`) |
| Einzelchance allgemein | Anteil der erfolgreichen Gefangenen ist *m*/*n*: durch Aufzählung aller 5.040 Anordnungen für *n* = 7 und jedes *m* bestätigt (`test_claim_individual_chance_…`) |
| Wie die Erfolge gekoppelt sind | *n* = 8, *m* = 4, Aufzählung aller 40.320 Anordnungen: entweder alle haben Erfolg (307/840, das sind 14.736 der 40.320) oder genau *L* Gefangene scheitern, mit Wahrscheinlichkeit 1/*L* für *L* = 5, 6, 7, 8 (1/5, 1/6, 1/7, 1/8) (`test_claim_cycle_strategy_failures_…`) |
| Grenzwert | Mit *m* = *n*/2 sinkt die Gewinnchance von 50,0 % (*n* = 2) auf 31,2 % (*n* = 100) und bleibt für alle geraden *n* bis 200 über 1 − ln 2 = 30,7 %; bei *n* = 100 liegt sie 0,50 Prozentpunkte darüber (`test_claim_limit_…`, `test_claim_the_value_at_m_equals_n_over_2_…`). *n* = 8: 307/840 = 36,5 %, *n* = 10: 35,4 % (`test_claim_small_cases_…`) |
| Weniger oder mehr Kästen, *n* = 100 | *m* = 10: 1,3·10⁻¹⁰, 25: 0,57 %, 40: 13,5 %, 49: 29,2 %, 51: 33,1 %, 60: 49,2 % (`test_claim_n100_other_box_counts`); mit *m* = 1 gewinnt nur die Identität (1/100!). Die Kurve steigt in *m* streng, getestet für *n* = 6, 11 und 30 |
| Feste Kästen (Fenster *i* bis *i* + *m* − 1) | *m* = *n*/2: *n* = 8: 11/1680 = 0,65 % gegen 0,39 % bei Zufall (Faktor 1,7); *n* = 4: Faktor 1,3; *n* = 20: 1,7·10⁻⁶ gegen 9,5·10⁻⁷ bei Zufall (Faktor 1,8, 4.152.609.019.392 passende Anordnungen); über *n* = 20 nicht exakt gerechnet (`test_claim_fixed_windows_…`) |
| Der Wärter kennt die Strategie | Ohne Helfer scheitert das Team gegen die Zyklus-Strategie und gegen feste Kästen für *m* < *n* sicher (0 %); die Zufalls-Strategie ist unberührt (7,9·10⁻³¹ bei *n* = 100) (`test_claim_warden_…`) |
| Geheime Umnummerierung der Kästen | Der Mittelwert über alle Umnummerierungen ist gleich der Gewinnchance einer zufälligen Anordnung, weil *q∘ρ* für gleichverteiltes ρ gleichverteilt ist (Begründung im Expander). Aufgezählt: *n* = 8, *m* = 4 und der einzelne Zyklus des Wärters: über alle 40.320 Umnummerierungen genau 307/840 (`test_claim_secret_renaming_…`); *n* = 7, *m* = 4 an fünf Anordnungen (Orakel-Test). Bei *n* = 100 gilt 31,2 % (E3) |
| Helfer mit einer Vertauschung | *n* = 8, *m* = 4: in allen 40.320 Anordnungen reicht eine (auch durch Ausprobieren aller 28 Vertauschungen bestätigt); für jedes *n* von 2 bis 100 mit *m* = ⌈*n*/2⌉ ist die Gewinnchance mit einer Vertauschung 100 %, weil eine Vertauschung einen Zyklus der Länge *L* ≤ *n* in ⌈*L*/2⌉ und ⌊*L*/2⌋ teilt (`test_claim_one_swap_…`). Mit *m* = 40: 13,5 %, 73,4 %, 100 % bei 0, 1, 2 Vertauschungen; mit *m* = 25: 0,57 %, 10,4 %, 54,5 %, 100 % bei 0 bis 3 (`test_claim_helper_numbers_for_n100`). Bei ungeradem *n* = 99 und *m* = 49 reicht eine nur zu 98,99 % (`test_claim_odd_n99_…`) |
| Kosten der Vertauschungen | Mindestzahl = Summe über die Zyklen von ⌈*L*/*m*⌉ − 1, gegen die Breitensuche über alle Vertauschungsfolgen für *n* bis 6, alle *m*, bis 3 Vertauschungen (`test_claim_swap_cost_formula_…`) |
| Optimalität für kleine Fälle | Unter allen deterministischen, anpassungsfähigen Strategien ist das beste Team gleich der Zyklus-Strategie: *n* = 3 (*m* = 1: 1/6, *m* = 2: 2/3) und *n* = 4 (*m* = 1: 1/24, *m* = 2: 5/12), durch Aufzählung aller Entscheidungsbäume (`test_claim_best_team_…`). Größere Fälle sind nicht aufgezählt |

## Quellen

- **Bekannt (Lehrbuch):** Zyklenstruktur zufälliger Permutationen (Länge des Zyklus eines festen Elements gleichverteilt, ein Zyklus über *n*/2 mit Wahrscheinlichkeit 1/*L*), harmonische Zahlen, Permanente. Die Zyklus-Strategie wird in der Literatur als Lösung des Rätsels geführt.
- Curtin, E.; Warshauer, M.: „The Locker Puzzle“, *The Mathematical Intelligencer* 28 (2006), S. 28–31. **Geprüft** ist nur die Fundstelle und der Grenzwert 1 − ln 2 für 2*n* Gefangene mit *n* Kästen (über den MathWorld-Eintrag „100 Prisoners Problem“, der diese Arbeit nennt). Dass dort die Optimalität der Zyklus-Strategie bewiesen wird, steht nur in Sekundärquellen (ein Blog), der Volltext wurde **nicht gelesen**; die Demo übernimmt deshalb die Optimalität nicht als Aussage und prüft sie nur für *n* = 3 und *n* = 4 durch Aufzählung.
- Zu Urheberschaft und Herkunft der Aufgabe macht die Demo keine Angabe (nicht geprüft, Stand 2026-11-08).

## Ehrliche Grenzen

- **Gleichverteilte Anordnung.** Bei einem Wärter, der die Strategie kennt, scheitert die Zyklus-Strategie sicher; erst eine geheime gemeinsame Zufallsentscheidung des Teams (die Umnummerierung) stellt die Gleichverteilung her. Sie ist eine **gemeinsame Zufallsquelle**, die das Rätsel in der ursprünglichen Fassung nicht hat.
- **Keine Verständigung nach der Absprache.** Dürften die Gefangenen nach dem ersten Öffnen etwas mitteilen, wäre das ein anderes Rätsel.
- **Alle dasselbe *m*.** Für ungleiche Zahlen erlaubter Kästen ist nichts gerechnet und die Optimalität der Zyklus-Strategie nicht untersucht.
- **Der Helfer** greift nur ein, wenn die erlaubten Vertauschungen reichen; sonst bleibt die Anordnung. Er sieht alle Zettel, was in der ursprünglichen Aufgabe nicht vorgesehen ist.
- **Feste Kästen** sind ein Beispiel (Fenster); andere feste Zuordnungen haben andere Zahlen. Exakt nur bis *n* = 20, darüber nur die Zählung in der Simulation (bei *n* = 100 kein Treffer in den gespielten Läufen, das ist keine Aussage über die Wahrscheinlichkeit).
- **Seltene Ereignisse in der Simulation:** 0 Treffer heißt nur „seltener als etwa 1 von den gespielten Läufen“; die exakten Werte stehen daneben.
- **Menschen und Gefängnisse:** Die Demo sagt nichts über Gedächtnis, Aufsicht oder reale Gruppen.

## Verifikation

- **Kern:** Zyklen, wörtliche Strategie, Zeigerverdopplung gegen die Schleife, Vertauschungskosten und -plan an der Mini-Anordnung (`tests/conftest.py`) und an Zufallsanordnungen; Rekursion gegen Handrechnung (*n* = 2, 3, 4).
- **Orakel** (`tests/test_oracle_gefangene_kaesten.py`): Aufzählung aller Anordnungen für *n* = 2 bis 9 gegen die Rekursion (in Brüchen) und gegen die Formel 1 − Σ 1/*k*; Summe über alle Zyklentypen (Partitionen von *n*, *n* ≤ 25) gegen die Rekursion; Stirling-Zahlen erster Art gegen die Aufzählung der Zyklenzahl und die Erwartung *H*ₙ; Permanent fester Fenster gegen Aufzählung und die Formel von Ryser; Verteilung der Erfolge und der Kosten gemeinsam gegen die Aufzählung; Vertauschungen gegen die Aufzählung aller Folgen; Umnummerierung gegen die Aufzählung aller Umnummerierungen. `tests/test_oracle_optimality.py`: beste Strategie für *n* = 3 und *n* = 4 durch Aufzählung aller Entscheidungsbäume.
- **Simulation:** gegen die exakten Werte in einem Band von 4,5 Standardabweichungen (feste Seeds); die Zufalls-Strategie wörtlich mit gezogenen Teilmengen; jede Variante (Wärter, Umnummerierung, Helfer) weicht auf mindestens einer Instanz von ihrer Nachbarvariante ab (Zweig-Tests).
- **Eigenschaften** (`tests/test_eigenschaften_gefangene_kaesten.py`): Zyklus-Strategie schlägt Zufall für alle *n* bis 30 und *m* < *n*; Monotonie in *m* und in den Vertauschungen; Invarianz unter gleichzeitiger Umbenennung von Gefangenen und Kästen; Misserfolge kommen in ganzen Zyklen über *m*; Mittel der Erfolge gleich *m*.
- **Verdikte, Randfälle, Presets:** jede Zahl im Text der Verdikte an Handwerten (`tests/test_verdicts.py`); *n* = 1, 2, *m* = 1, *m* = *n*, ungerade *n* (`tests/test_edge_cases.py`); alle Presets vollständig und mit unterschiedlichen Werten.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum, alle Minima und alle Maxima zusammen, jeder Wärter mit Randeinstellungen, die vier Nachspiel-Knöpfe, PDF, Permalink), Footer-Test, Laufzeit-Importe.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben (`tests/test_layout.py`).
- **Nicht geprüft:** der Volltext von Curtin und Warshauer; die Optimalität für *n* ≥ 5; ungleiche Zahlen erlaubter Kästen; Verhalten in der Streamlit Cloud (nicht deployt).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `gfk_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Raster der Experimente, Presets |
| `gfk_cycles.py` | Zyklen, wörtliche Strategie, Vertauschungskosten und -plan |
| `gfk_exact.py` | Rekursionen, Formeln, Permanent fester Fenster |
| `gfk_simulation.py` | Simulation der drei Strategien |
| `gfk_evaluation.py` | Kennzahlen, Formate, Verdikte |
| `gfk_experiments.py` | Experimente E1 bis E4 |
| `gfk_layout.py` | Fester Kopf (Stylesheet) |
| `gfk_pdf_export.py` | PDF-Export (erst nach Klick) |
| `gfk_presets.py` | Permalink (Begrenzen, Einrasten), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben), Zufalls-Seed-Button |
| `gfk_rng.py` | SplitMix64, wörtliche Kopie aus `ab-test-demo` |
| `gfk_scenario.py` | Einstellungen, Rundung auf ganze Kästen, Zufallsströme |
| `gfk_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Tests wie unter Verifikation |

## Bewusst nicht umgesetzt

- Ungleiche Zahlen erlaubter Kästen je Gefangenem und die Frage ihrer Optimalität.
- Ein Beweis der Optimalität der Zyklus-Strategie; die Demo nennt ihn als Literaturresultat und prüft nur *n* ≤ 4.
- Eine Quantenfassung oder Fassungen mit Verständigung nach der Absprache.
- Andere feste Strategien als die Fenster (etwa zufällig gewählte feste Mengen) und eine exakte Rechnung fester Fenster über *n* = 20.

## Abgrenzung

[`permanente-demo`](https://github.com/sebastian-hanisch/permanente-demo) zählt perfekte Paarungen über die Permanente und führt Derangements nur als Matrixbeispiel (J − I) ein; hier erscheint der Permanent nur als Zählung der Anordnungen, in denen feste Kästen gewinnen, und die Statistik zufälliger Permutationen (Zyklen) ist der Kern. `fokalpunkt-demo` und die übrigen Stücke der Koordinationsspiele-Reihe behandeln Eigennutz, Gleichgewichte und Lernen; hier gilt ein gemeinsames Ziel und es geht um Wahrscheinlichkeiten.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Die Suite umfasst 179 Tests. Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
