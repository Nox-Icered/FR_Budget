"""Tests de l'API et de l'export pour les leviers « cotisations patronales » (lot 2.10)."""

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


def test_scenario_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": "allegements_generaux", "valeur": -10, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {"allegements_generaux": "beta"}
    assert "ccss_octobre_2026" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_export(tmp_path: Path) -> None:
    exporter(tmp_path)
    u = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    assert u["leviers"]["cotisations_patronales_taux"]["bornes"] == [-2.0, 2.0]
    assert u["leviers"]["allegements_generaux"]["bornes"] == [-20.0, 20.0]
    assert u["leviers"]["allegements_generaux"]["rendement_unitaire"] < 0
