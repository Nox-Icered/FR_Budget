"""Tests de l'API et de l'export pour les leviers « dotations aux collectivités » (lot 2.6)."""

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


def test_scenario_dgf_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": "dotations_dgf", "valeur": -5, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {"dotations_dgf": "beta"}
    assert "cdc_eclairages_8_dotations_investissement" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_export_effet_etat(tmp_path: Path) -> None:
    exporter(tmp_path)
    u = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    for levier in ("dotations_dgf", "dotations_compensations"):
        donnees = u["leviers"][levier]
        assert donnees["bornes"] == [-10.0, 10.0]
        # Une hausse d'1 % coûte à l'État plus qu'elle ne dégrade le solde public.
        assert donnees["effet_etat_unitaire"] < donnees["rendement_unitaire"] < 0
    assert "effet_etat_unitaire" not in u["leviers"]["tva_taux_normal"]
