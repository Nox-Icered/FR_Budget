"""Tests de l'API et de l'export pour le levier « prime d'activité » (lot 2.12)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

LEVIER = "prime_activite_pente"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_scenario_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": LEVIER, "valeur": -1, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {LEVIER: "beta"}
    assert "senat_note_presentation_siec_plf2026" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_export(tmp_path: Path) -> None:
    exporter(tmp_path)
    u = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    assert u["leviers"][LEVIER]["bornes"] == [-5.0, 5.0]
    assert u["leviers"][LEVIER]["rendement_unitaire"] < 0
