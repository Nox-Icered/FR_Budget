"""Données de l'éditeur de barème de l'impôt sur le revenu (export du site)."""

from __future__ import annotations

from fr_budget_api.app import bareme_ir


def test_donnees_editeur() -> None:
    d = bareme_ir()
    assert d["levier"] == "ir_bareme"
    assert d["annee_bareme"] == 2025
    assert "dgfip_ir_tableaux_statistiques" in d["sources"]
    assert d["hypotheses"] == ["ir_bareme_ecart"]
    assert len(d["segments"]) == 12
    reference = d["bareme_reference"]
    assert reference["seuils"][0] == 0.0 and reference["decote"] is not None


def test_controles_redonnent_le_moteur() -> None:
    for c in bareme_ir()["controles"]:
        assert c["effet"]["bas"] <= c["effet"]["central"] <= c["effet"]["haut"]
