"""Tests de l'API et de l'export pour les leviers « dépenses fiscales » (lot 2.4)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

CODE = "110201"


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
    catalogue = client.get("/depenses-fiscales").json()
    assert _lire(export, "depenses-fiscales.json") == catalogue
    assert {"tva", "accise_energies"} == set(catalogue["impots_exclus"])
    codes = {d["code"] for d in catalogue["depenses"]}
    assert CODE in codes
    assert "800221" not in codes


def test_scenario_d_une_depense_avec_statut_beta(client: TestClient) -> None:
    corps = {"mesures": [{"levier": f"depense_fiscale_{CODE}", "valeur": 100, "annee": 2027}]}
    reponse = client.post("/scenario", json=corps)
    assert reponse.status_code == 200
    donnees = reponse.json()
    assert donnees["statuts"] == {f"depense_fiscale_{CODE}": "beta"}
    assert "plf2026_voies_et_moyens_tome2" in donnees["sources"]
    assert donnees["valeurs"][-1]["ecart_dette"]["central"] < 0


def test_double_compte_refuse(client: TestClient) -> None:
    corps = {
        "mesures": [
            {"levier": f"depense_fiscale_{CODE}", "valeur": 50, "annee": 2027},
            {"levier": "depenses_fiscales_impot_revenu", "valeur": 50, "annee": 2027},
        ]
    }
    assert client.post("/scenario", json=corps).status_code == 422


def test_site_une_depense_par_l_unite_generique(client: TestClient, export: Path) -> None:
    """Calcul du site : x % d'une dépense = x * rendement_pourcent sur le levier générique."""
    u = _lire(export, "scenario-unitaire.json")
    catalogue = _lire(export, "depenses-fiscales.json")
    depense = next(d for d in catalogue["depenses"] if d["code"] == CODE)
    x = 40.0
    valeur = x * depense["rendement_pourcent"]
    reponse = u["leviers"]["depense_fiscale"]["reponses"]["2028"]
    corps = {"mesures": [{"levier": f"depense_fiscale_{CODE}", "valeur": x, "annee": 2028}]}
    attendu = client.post("/scenario", json=corps).json()["valeurs"]
    for i, ligne in enumerate(attendu):
        ecarts = [valeur * reponse["unite_dette"][k][i] for k in u["indices_effet"]]
        assert ecarts[0] == pytest.approx(ligne["ecart_dette"]["central"], abs=1e-8)
        assert min(ecarts) == pytest.approx(ligne["ecart_dette"]["bas"], abs=1e-8)
        assert max(ecarts) == pytest.approx(ligne["ecart_dette"]["haut"], abs=1e-8)
