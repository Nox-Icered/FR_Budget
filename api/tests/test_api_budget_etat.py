"""Export du budget de l'État 2026 pour le diagramme de la page d'accueil."""

from __future__ import annotations

import pytest

from fr_budget_api.app import budget_etat


def test_ressources_egales_aux_emplois_et_sources() -> None:
    b = budget_etat()
    assert b["annee"] == 2026
    assert sum(f["montant"] for f in b["ressources"]) == pytest.approx(
        sum(f["montant"] for f in b["emplois"]), abs=0.05
    )
    assert "plf2026_projet_loi" in b["sources"]
    # Libellé fourni par le site pour les postes, publié pour les missions.
    assert all(f["libelle"] is None for f in b["ressources"])
    assert any(f["libelle"] == "Défense" for f in b["emplois"])
