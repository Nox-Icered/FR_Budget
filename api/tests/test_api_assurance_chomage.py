"""Tests de l'API pour les leviers « assurance chômage » (première étape)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application, reponses_unitaires

LEVIERS = {
    "chomage_contribution_patronale": ([-1.0, 1.0], "unedic_etude_impact_convention_2024", 1),
    "chomage_revalorisation": ([-2.0, 2.0], "unedic_revalorisation_mode_emploi_2023", -1),
    "chomage_duree_indemnisation": ([-0.25, 0.25], "unedic_effets_adaptation_conjoncture_2023", -1),
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


@pytest.mark.parametrize("levier", LEVIERS)
def test_scenario_statut_beta(client: TestClient, levier: str) -> None:
    """Une hausse : solde amélioré (contribution) ou dégradé (allocations), dette en regard."""
    _, source, signe = LEVIERS[levier]
    corps = {"mesures": [{"levier": levier, "valeur": 0.1, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {levier: "beta"}
    assert source in donnees["sources"]
    assert signe * donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_reponses_unitaires() -> None:
    leviers = reponses_unitaires()["leviers"]
    for levier, (bornes, _, signe) in LEVIERS.items():
        assert leviers[levier]["bornes"] == bornes
        assert leviers[levier]["statut"] == "beta"
        assert signe * leviers[levier]["rendement_unitaire"] > 0
