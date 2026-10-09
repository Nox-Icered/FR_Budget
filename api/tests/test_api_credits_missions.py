"""Tests de l'API et de l'export pour les leviers « crédits par mission » (lot 2.5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

IDENT = "justice"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


@pytest.fixture(scope="module")
def export(tmp_path_factory: pytest.TempPathFactory) -> Path:
    dossier = tmp_path_factory.mktemp("export")
    exporter(dossier)
    return dossier


def _lire(dossier: Path, nom: str) -> dict:  # type: ignore[type-arg]
    return json.loads((dossier / nom).read_text(encoding="utf-8"))  # type: ignore[no-any-return]


def test_catalogue_exporte_identique_a_l_api(client: TestClient, export: Path) -> None:
    catalogue = client.get("/credits-missions").json()
    assert _lire(export, "credits-missions.json") == catalogue
    ids = {m["identifiant"] for m in catalogue["missions"]}
    assert IDENT in ids
    assert "relations_avec_les_collectivites_territoriales" not in ids


def test_scenario_d_une_mission_avec_statut_beta(client: TestClient) -> None:
    levier = f"credits_mission_{IDENT}"
    corps = {"mesures": [{"levier": levier, "valeur": -10, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    assert donnees["statuts"] == {levier: "beta"}
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_levier_generique_refuse_par_l_api(client: TestClient) -> None:
    corps = {"mesures": [{"levier": "credits_missions", "valeur": -1.0, "annee": 2027}]}
    assert client.post("/scenario", json=corps).status_code == 422


def test_site_hausses_et_baisses_par_l_unite_generique(client: TestClient, export: Path) -> None:
    """Calcul du site, reproduit ici : les baisses et les hausses de crédits forment deux
    mesures génériques (une par signe), et le résultat égale celui de l'API."""
    u = _lire(export, "scenario-unitaire.json")
    catalogue = {m["identifiant"]: m for m in _lire(export, "credits-missions.json")["missions"]}
    reglages = {IDENT: -10.0, "culture": 5.0}
    valeurs = [-x * catalogue[i]["rendement_pourcent"] for i, x in reglages.items()]
    baisses = sum(v for v in valeurs if v < 0)
    hausses = sum(v for v in valeurs if v > 0)
    reponse = u["leviers"]["credits_missions"]["reponses"]["2027"]
    k_bas: int = u["indices_effet"][1]
    k_haut: int = u["indices_effet"][2]

    def indice(k: int, x: float) -> int:
        if x >= 0:
            return k
        return {k_bas: k_haut, k_haut: k_bas}.get(k, k)

    corps = {
        "mesures": [
            {"levier": f"credits_mission_{i}", "valeur": x, "annee": 2027}
            for i, x in reglages.items()
        ]
    }
    attendu = client.post("/scenario", json=corps).json()["valeurs"]
    for i, ligne in enumerate(attendu):
        ecarts = [
            sum(x * reponse["unite_dette"][indice(k, x)][i] for x in (baisses, hausses))
            for k in u["indices_effet"]
        ]
        assert ecarts[0] == pytest.approx(ligne["ecart_dette"]["central"], abs=1e-8)
        assert min(ecarts) == pytest.approx(ligne["ecart_dette"]["bas"], abs=1e-8)
        assert max(ecarts) == pytest.approx(ligne["ecart_dette"]["haut"], abs=1e-8)
