"""Tests de l'API et de l'export pour les leviers « rémunérations publiques » (lot 2.7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_scenario_point_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": "remunerations_point_indice", "valeur": 1, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {"remunerations_point_indice": "beta"}
    assert "dgafp_rapport_annuel_2025" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] > 0


def test_combinaison_avec_les_missions_refusee(client: TestClient) -> None:
    corps = {
        "mesures": [
            {"levier": "remunerations_effectifs", "valeur": -1, "annee": 2027},
            {"levier": "credits_mission_justice", "valeur": -1, "annee": 2027},
        ]
    }
    assert client.post("/scenario", json=corps).status_code == 422


def test_export_effet_brut(tmp_path: Path) -> None:
    exporter(tmp_path)
    u = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    for levier in ("remunerations_point_indice", "remunerations_effectifs"):
        donnees = u["leviers"][levier]
        assert donnees["bornes"] == [-5.0, 5.0]
        assert donnees["effet_brut_unitaire"] < donnees["rendement_unitaire"] < 0
