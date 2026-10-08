"""Tests de l'API sans état (lot 1.4 du plan)."""

from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_sante(client: TestClient) -> None:
    assert client.get("/sante").json() == {"statut": "ok"}


def test_version_donne_les_empreintes(client: TestClient) -> None:
    version = client.get("/version").json()
    assert set(version) == {"moteur", "registres", "donnees"}
    assert len(version["registres"]) == 64
    assert len(version["donnees"]) == 64


@pytest.mark.parametrize(
    "nom", ["sources", "jeux-de-donnees", "hypotheses", "leviers", "chiffrages"]
)
def test_registres_lisibles(client: TestClient, nom: str) -> None:
    reponse = client.get(f"/registres/{nom}")
    assert reponse.status_code == 200
    assert isinstance(reponse.json(), list)
    assert reponse.json()


def test_registre_inconnu(client: TestClient) -> None:
    assert client.get("/registres/inconnu").status_code == 404


def test_comptes_apu_avec_source_et_unite(client: TestClient) -> None:
    reponse = client.get(
        "/comptes-apu", params={"sous_secteur": "S13", "indicateur": "dette_maastricht"}
    ).json()
    assert reponse["source"] == "insee_comptes_nationaux_2025"
    assert reponse["unite"] == "Md€"
    annees = [v["annee"] for v in reponse["valeurs"]]
    assert annees == sorted(annees)
    assert 2025 in annees


def test_comptes_apu_serie_inconnue(client: TestClient) -> None:
    reponse = client.get("/comptes-apu", params={"sous_secteur": "S99", "indicateur": "dette"})
    assert reponse.status_code == 404


def test_depenses_par_fonction(client: TestClient) -> None:
    reponse = client.get(
        "/depenses-par-fonction", params={"annee": 2024, "sous_secteur": "S13"}
    ).json()
    assert reponse["source"] == "eurostat_gov_10a_exp"
    codes = {v["cofog"] for v in reponse["valeurs"]}
    assert {"TOTAL", "GF01", "GF10"} <= codes


def test_depenses_par_fonction_annee_absente(client: TestClient) -> None:
    reponse = client.get("/depenses-par-fonction", params={"annee": 1800, "sous_secteur": "S13"})
    assert reponse.status_code == 404


def test_aucune_requete_journalisee(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    # Règle 5 de CLAUDE.md : rien de ce que saisit l'utilisateur n'est journalisé par l'API.
    # Le journal « httpx » est celui du client de test (côté appelant), pas du serveur : exclu.
    with caplog.at_level(logging.DEBUG):
        client.get("/comptes-apu", params={"sous_secteur": "S13", "indicateur": "TRACE_42"})
    serveur = [r.getMessage() for r in caplog.records if not r.name.startswith("httpx")]
    assert not any("TRACE_42" in message for message in serveur)
