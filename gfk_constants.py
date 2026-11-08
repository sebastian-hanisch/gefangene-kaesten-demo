"""Konstanten: Regler-Grenzen, feste Annahmen, Farben, Raster der Experimente und Presets."""

# Regler. Komplexität am Maximum: Simulation O(Läufe · n · log n) (Zeigerspringen), exakte Rekursion O(n² · Kostenstufen), fester Permanent O(2^n · n) nur bis EXACT_FIXED_MAX_N.
N_MIN, N_MAX, DEFAULT_N = 2, 100, 100
SHARE_MIN, SHARE_MAX, DEFAULT_SHARE = 1, 100, 50     # erlaubte Kästen je Gefangenem in Prozent von n (Rundung auf ganze Kästen)
SWAPS_MIN, SWAPS_MAX, DEFAULT_SWAPS = 0, 3, 0        # Vertauschungen, die ein Helfer vorab machen darf
RUNS_MIN, RUNS_MAX, DEFAULT_RUNS = 1000, 20000, 5000
RUNS_STEP = 1000
SEED_MAX, DEFAULT_SEED = 999999, 6
CHUNK_RUNS = 2000                                    # Simulationsläufe je Block (begrenzt den Speicher bei n = 100)
SIM_UNITS_PER_SECOND = 3_500_000                     # Läufe · Gefangene je Sekunde, gemessen rund 7 Mio. (n = 100, 20.000 Läufe in 0,27 s), hier halbiert

# Wer legt die Zettel in die Kästen?
WARDEN_RANDOM = "zufall"
WARDEN_KNOWS = "waerter"
WARDEN_SECRET = "umnummeriert"
WARDENS = (WARDEN_RANDOM, WARDEN_KNOWS, WARDEN_SECRET)
WARDEN_LABELS = {
    WARDEN_RANDOM: "Zufall: die Zettel liegen gleichverteilt",
    WARDEN_KNOWS: "Der Wärter kennt die Strategie und legt sie sich zurecht",
    WARDEN_SECRET: "Wärter kennt die Strategie, das Team nummeriert die Kästen geheim um",
}

# Strategien
STRAT_RANDOM = "Zufall"
STRAT_FIXED = "Feste Kästen"
STRAT_CYCLE = "Zyklus-Strategie"
STRATEGIES = (STRAT_RANDOM, STRAT_FIXED, STRAT_CYCLE)

EXACT_FIXED_MAX_N = 20                               # bis hierhin wird der Permanent der festen Fenster exakt gerechnet (2^20 Teilmengen)
ENUM_MAX_N = 9                                       # Aufzählung aller Permutationen in den Tests (9! = 362 880)

# Raster der Experimente
E1_SHARES = (10, 20, 25, 30, 40, 45, 49, 50, 51, 55, 60, 75, 90, 100)
E2_NS = (2, 4, 6, 8, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)
E4_SHARES = (50, 40, 30, 25)

# Farben (Achsen und Spuren der Diagramme)
COLOR_CYCLE = "#2F6B65"
COLOR_RANDOM = "#c7773a"
COLOR_FIXED = "#7a6bb0"
COLOR_BAD = "#c0392b"
COLOR_GOOD = "#2F6B65"
COLOR_LINE = "#4c78a8"
COLOR_OTHER = "rgba(150,150,150,0.55)"

PRESETS = {
    "Das klassische Rätsel": {"n": 100, "share": 50, "warden": WARDEN_RANDOM, "swaps": 0, "runs": DEFAULT_RUNS, "seed": DEFAULT_SEED},
    "Zum Nachzählen: 8 Gefangene": {"n": 8, "share": 50, "warden": WARDEN_RANDOM, "swaps": 0, "runs": DEFAULT_RUNS, "seed": DEFAULT_SEED},
    "Zu wenige Kästen: 40 von 100": {"n": 100, "share": 40, "warden": WARDEN_RANDOM, "swaps": 0, "runs": DEFAULT_RUNS, "seed": DEFAULT_SEED},
    "Der Wärter kennt die Strategie": {"n": 100, "share": 50, "warden": WARDEN_KNOWS, "swaps": 0, "runs": DEFAULT_RUNS, "seed": DEFAULT_SEED},
    "Der Wärter, aber geheim umnummeriert": {"n": 100, "share": 50, "warden": WARDEN_SECRET, "swaps": 0, "runs": DEFAULT_RUNS, "seed": DEFAULT_SEED},
    "Ein Helfer vertauscht vorab zwei Kästen": {"n": 100, "share": 50, "warden": WARDEN_RANDOM, "swaps": 1, "runs": DEFAULT_RUNS, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Das klassische Rätsel": "100 Gefangene, jeder darf 50 von 100 Kästen öffnen, die Zettel liegen zufällig. Alle Strategien werden verglichen.",
    "Zum Nachzählen: 8 Gefangene": "Nur 8 Gefangene mit je 4 Kästen: alle 40.320 Anordnungen lassen sich aufzählen, die Zyklus-Strategie gewinnt in 14.736 davon (307/840).",
    "Zu wenige Kästen: 40 von 100": "Jeder darf nur 40 statt 50 Kästen öffnen. Die Zyklus-Strategie verliert, sobald ein Zyklus länger als 40 ist, und das kommt oft vor.",
    "Der Wärter kennt die Strategie": "Der Wärter weiß, welche Strategie das Team abgesprochen hat, und legt die Zettel so, dass sie versagt (ein einziger langer Zyklus).",
    "Der Wärter, aber geheim umnummeriert": "Das Team hat vorab eine geheime Umnummerierung der Kästen vereinbart, die der Wärter nicht kennt: seine Anordnung wirkt dann wie eine zufällige.",
    "Ein Helfer vertauscht vorab zwei Kästen": "Ein Helfer, der alle Zettel sieht, darf vor Beginn die Zettel zweier Kästen vertauschen. Danach darf niemand mehr etwas sagen.",
}
