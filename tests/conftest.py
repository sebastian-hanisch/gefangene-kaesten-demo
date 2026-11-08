"""Gemeinsame Fixtures: die Mini-Anordnungen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b). Alle Erwartungswerte stehen als Rechnung dabei."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def mini():
    """Sechs Kästen (ab 0 gezählt), Kasten j enthält den Zettel q[j]: q = (1, 2, 0, 4, 3, 5).
    Zyklen: 0 → 1 → 2 → 0 (Länge 3), 3 → 4 → 3 (Länge 2), 5 → 5 (Länge 1). Zykluslängen also 3, 2, 1.
    Gefangener 0 öffnet Kasten 0 (Zettel 1), Kasten 1 (Zettel 2), Kasten 2 (Zettel 0): gefunden nach der 3. Öffnung.
    Bei m = 3 haben alle Erfolg; bei m = 2 nur die Gefangenen 3, 4 und 5 (3 Erfolge). Vertauschungskosten bei m = 2: ceil(3/2) - 1 = 1, bei m = 1: (3 - 1) + (2 - 1) = 3."""
    return {"q": [1, 2, 0, 4, 3, 5], "lengths": [3, 2, 1], "cycles": [[0, 1, 2], [3, 4], [5]], "success_m2": 3, "cost_m2": 1, "cost_m1": 3}
