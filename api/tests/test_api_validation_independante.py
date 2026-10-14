"""Confrontations à des sources indépendantes dans le résumé de validation."""

from __future__ import annotations

from fr_budget_api.app import resume_validation


def test_references_independantes_marquees() -> None:
    lignes = {r["reference"]: r for r in resume_validation()}
    assert lignes["tva_point_brut_ipp_2025_quatre_taux"]["independante"] is True
    assert lignes["tva_point_brut_ipp_2025_quatre_taux"]["levier"] == "tva"
    assert lignes["ir_gel_bareme_2026"]["independante"] is False
