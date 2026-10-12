"""Tests de l'API et de l'export pour le levier « âge effectif moyen de départ » (lot 3.1)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application, reponses_unitaires

LEVIER = "retraites_age_depart"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_scenario_cite_le_cor(client: TestClient) -> None:
    corps = {"mesures": [{"levier": LEVIER, "valeur": 1.0, "annee": 2027}]}
    r = client.post("/scenario", json=corps).json()
    assert "cor_rapport_annuel_2026" in r["sources"]
    assert r["statuts"][LEVIER] == "beta"
    assert r["valeurs"][-1]["ecart_solde_primaire"]["central"] > 0


def test_export_du_levier() -> None:
    levier = reponses_unitaires()["leviers"][LEVIER]
    assert levier["bornes"] == [-1.0, 3.0]
    assert levier["duree_montee"] > 0
    assert levier["multiplicateur"] == {"bas": 0.0, "central": 0.0, "haut": 0.0}
