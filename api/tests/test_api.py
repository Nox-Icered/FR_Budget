"""Tests de l'API sans état (lot 1.4 du plan)."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_sante(client: TestClient) -> None:
    assert client.get("/sante").json() == {"statut": "ok"}


def test_version_donne_les_empreintes(client: TestClient) -> None:
    version = client.get("/version").json()
    assert set(version) == {"moteur", "registres", "donnees"}
    assert len(version["moteur"]) == 64
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


def test_export_identique_a_l_api(client: TestClient, tmp_path: Path) -> None:
    exporter(tmp_path)
    comptes = json.loads((tmp_path / "comptes-apu.json").read_text(encoding="utf-8"))
    attendu = client.get(
        "/comptes-apu", params={"sous_secteur": "S13", "indicateur": "dette_maastricht"}
    ).json()
    assert comptes["series"]["S13"]["dette_maastricht"] == attendu
    sources = json.loads((tmp_path / "registre-sources.json").read_text(encoding="utf-8"))
    assert sources == client.get("/registres/sources").json()


def test_ratio_au_pib_fourni_par_le_moteur(client: TestClient) -> None:
    serie = client.get(
        "/comptes-apu", params={"sous_secteur": "S13", "indicateur": "dette_maastricht"}
    ).json()
    derniere = serie["valeurs"][-1]
    pib = client.get("/comptes-apu", params={"sous_secteur": "S1", "indicateur": "pib"}).json()
    pib_meme_annee = next(v["valeur"] for v in pib["valeurs"] if v["annee"] == derniere["annee"])
    assert derniere["pourcent_pib"] == pytest.approx(derniere["valeur"] / pib_meme_annee * 100)
    assert "pourcent_pib" not in pib["valeurs"][-1]


def test_journal_d_acces_desactive_par_l_application(caplog: pytest.LogCaptureFixture) -> None:
    creer_application()
    acces = logging.getLogger("uvicorn.access")
    assert acces.disabled
    with caplog.at_level(logging.DEBUG):
        acces.info("GET /comptes-apu?indicateur=TRACE_43")
    assert "TRACE_43" not in caplog.text


def test_validation_publie_les_ecarts(client: TestClient) -> None:
    resume = client.get("/validation").json()
    choc = next(c for c in resume if c["reference"] == "dette_etat_choc_taux_100pb_an_1")
    assert choc["valeur_reference"] == pytest.approx(3.4)
    assert choc["ecart"] == pytest.approx((choc["modele"] - 3.4) / 3.4)
    assert choc["dans_la_tolerance"] is (abs(choc["ecart"]) <= choc["tolerance"])
    assert choc["unite"] == "Md€"
