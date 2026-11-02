"""Flux du budget de l'État 2026 (fr_budget.budget_etat)."""

from __future__ import annotations

import pytest

from fr_budget import budget_etat as be


def test_ressources_egales_aux_emplois() -> None:
    """Article 48 : recettes - prélèvements - dépenses nettes = solde du budget général."""
    b = be.budget()
    assert sum(f.montant for f in b.ressources) == pytest.approx(
        sum(f.montant for f in b.emplois), abs=1e-3
    )


def test_deficit_du_budget_general() -> None:
    """Solde du budget général du projet de loi de finances pour 2026 : -124 102 M€."""
    deficit = next(f for f in be.budget().ressources if f.identifiant == "deficit")
    assert deficit.montant == pytest.approx(124.102)


def test_missions_par_ordre_decroissant() -> None:
    missions = [f for f in be.budget().emplois if f.identifiant.startswith("mission_")]
    assert len(missions) == 32
    assert missions[0].libelle == "Enseignement scolaire"
    assert [m.montant for m in missions] == sorted((m.montant for m in missions), reverse=True)
