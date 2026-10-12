"""Tests de l'API et de l'export pour le levier « indexation des pensions et prestations »."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

LEVIER = "indexation_pensions_prestations"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_scenario_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": LEVIER, "valeur": -1, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {LEVIER: "beta"}
    assert "drees_comptes_protection_sociale_2025" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_combinaison_avec_la_mission_solidarite_refusee(client: TestClient) -> None:
    corps = {
        "mesures": [
            {"levier": LEVIER, "valeur": -1, "annee": 2027},
            {
                "levier": "credits_mission_solidarite_insertion_et_egalite_des_chances",
                "valeur": -1,
                "annee": 2027,
            },
        ]
    }
    assert client.post("/scenario", json=corps).status_code == 422


def test_export_effet_brut(tmp_path: Path) -> None:
    exporter(tmp_path)
    u = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    donnees = u["leviers"][LEVIER]
    assert donnees["bornes"] == [-2.0, 1.0]
    assert donnees["effet_brut_unitaire"] < donnees["rendement_unitaire"] < 0
