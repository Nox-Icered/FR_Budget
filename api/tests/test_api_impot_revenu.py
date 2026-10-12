"""Tests de l'API et de l'export pour le levier « impôt sur le revenu » (lot 2.11)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

LEVIER = "ir_seuils_bareme"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_scenario_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": LEVIER, "valeur": -1, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {LEVIER: "beta"}
    assert "dgfip_statistiques_41" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_export(tmp_path: Path) -> None:
    exporter(tmp_path)
    u = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    assert u["leviers"][LEVIER]["bornes"] == [-3.0, 3.0]
    assert u["leviers"][LEVIER]["rendement_unitaire"] < 0
