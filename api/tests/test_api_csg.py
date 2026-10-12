"""Tests de l'API et de l'export pour les leviers « CSG » (lot 2.9)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

LEVIERS = ("csg_activite", "csg_retraites", "csg_capital")


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_scenario_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": "csg_activite", "valeur": 1, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {"csg_activite": "beta"}
    assert "ccss_octobre_2026" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_export(tmp_path: Path) -> None:
    exporter(tmp_path)
    u = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    for levier in LEVIERS:
        assert u["leviers"][levier]["bornes"] == [-2.0, 2.0]
        assert u["leviers"][levier]["rendement_unitaire"] > 0
