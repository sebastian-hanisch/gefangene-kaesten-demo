"""Szenario: die Einstellungen der App und die daraus abgeleiteten Größen. Zufall kommt aus SplitMix64 (gfk_rng)."""

from __future__ import annotations

import math
import zlib
from dataclasses import dataclass, replace

import gfk_constants as C
from gfk_rng import SplitMix64


@dataclass(frozen=True, kw_only=True)
class Settings:
    """Alle Regler der Seitenleiste. Nur mit Schlüsselwörtern anlegen: ein eingefügtes Feld darf nie still Werte verschieben."""
    n: int = C.DEFAULT_N                 # Zahl der Gefangenen (und Kästen)
    share: int = C.DEFAULT_SHARE         # erlaubte Kästen je Gefangenem in Prozent von n
    warden: str = C.WARDEN_RANDOM        # wer legt die Zettel: Zufall, Wärter, Wärter + geheime Umnummerierung
    swaps: int = C.DEFAULT_SWAPS         # Vertauschungen, die ein Helfer vorab machen darf
    runs: int = C.DEFAULT_RUNS           # Simulationsläufe
    seed: int = C.DEFAULT_SEED


def settings_of_preset(name: str) -> Settings:
    return Settings(**C.PRESETS[name])


def with_(s: Settings, **changes) -> Settings:
    """Kopie mit geänderten Feldern (nur Schlüsselwörter)."""
    return replace(s, **changes)


def boxes_per_person(n: int, share: int) -> int:
    """Erlaubte Kästen m = n · share / 100, auf ganze Kästen gerundet (0,5 wird aufgerundet), mindestens 1, höchstens n."""
    return max(1, min(n, (2 * n * share + 100) // 200))


def m_of(s: Settings) -> int:
    return boxes_per_person(s.n, s.share)


def stream_seed(seed: int, label: str) -> int:
    """Eigener Zufallsstrom je Zweck: aus dem Zufalls-Seed und einer Marke abgeleitet (crc32 ist über Prozesse hinweg stabil, anders als hash())."""
    return SplitMix64((seed * 1_000_003 + zlib.crc32(label.encode("utf-8"))) & ((1 << 64) - 1)).next()


def estimated_seconds(n: int, runs: int, points: int = 1) -> int:
    """Grobe Sekundenzahl für `points` Simulationen mit je `runs` Läufen (nur für die Angabe an Knopf und Spinner): gemessen rund 7 Mio. Läufe·Gefangene je Sekunde, hier mit Sicherheitsfaktor 2."""
    return max(1, math.ceil(runs * n * points / C.SIM_UNITS_PER_SECOND))
