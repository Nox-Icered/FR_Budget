"""Tests de l'API pour le levier « plafond du quotient familial » (V2, impôt sur le revenu)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application, reponses_unitaires

LEVIER = "ir_plafond_quotient_familial"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_scenario_statut_beta(client: TestClient) -> None:
    """Une baisse des plafonds améliore le solde et réduit la dette ; levier en bêta."""
    corps = {"mesures": [{"levier": LEVIER, "valeur": -10, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {LEVIER: "beta"}
    assert "igf_igas_politiques_familiales_2026" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_bornes_et_rendement() -> None:
    u = reponses_unitaires()
    assert u["leviers"][LEVIER]["bornes"] == [-25.0, 25.0]
    assert u["leviers"][LEVIER]["rendement_unitaire"] < 0
