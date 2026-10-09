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


def test_baseline_en_fourchette_avec_sources(client: TestClient) -> None:
    reponse = client.get("/baseline").json()
    assert reponse["sources"] == ["plf2027_resf", "ce_ageing_report_2024"]
    assert reponse["unite"] == "% du PIB"
    assert reponse["statut"] == "non_publie"
    annees = [v["annee"] for v in reponse["valeurs"]]
    assert annees == list(range(2025, 2047))
    for v in reponse["valeurs"]:
        for grandeur in ("dette", "solde_primaire"):
            f = v[grandeur]
            assert f["bas"] <= f["central"] <= f["haut"]
        assert v["segment"] == ("resf" if v["annee"] <= reponse["annee_raccord"] else "projection")
    hypotheses = {h["id"] for h in client.get("/registres/hypotheses").json()}
    assert set(reponse["hypotheses"]) <= hypotheses


def test_baseline_reprend_le_moteur(client: TestClient) -> None:
    from fr_budget.baseline import baseline

    reponse = client.get("/baseline").json()
    derniere = baseline()[-1]
    assert reponse["valeurs"][-1]["dette"]["central"] == pytest.approx(derniere.dette.central)


def test_export_baseline_identique_a_l_api(client: TestClient, tmp_path: Path) -> None:
    exporter(tmp_path)
    exporte = json.loads((tmp_path / "baseline.json").read_text(encoding="utf-8"))
    assert exporte == client.get("/baseline").json()


def test_scenario_tva_ecart_et_version(client: TestClient) -> None:
    corps = {"mesures": [{"levier": "tva_taux_normal", "valeur": 1.0, "annee": 2027}]}
    reponse = client.post("/scenario", json=corps)
    assert reponse.status_code == 200
    donnees = reponse.json()
    assert set(donnees["version"]) == {"moteur", "registres", "donnees"}
    assert donnees["unite"] == "% du PIB"
    assert donnees["mesures"] == corps["mesures"]
    assert donnees["statuts"] == {"tva_taux_normal": "beta"}
    # Provenance : sources et hypothèses de la baseline, du PIB et du levier, toutes au registre.
    sources = {s["id"] for s in client.get("/registres/sources").json()}
    hypotheses = {h["id"] for h in client.get("/registres/hypotheses").json()}
    assert {"plf2027_resf", "ce_ageing_report_2024", "insee_comptes_nationaux_2025"} <= set(
        donnees["sources"]
    )
    assert "insee_tes_2025" in donnees["sources"]
    assert set(donnees["sources"]) <= sources
    assert {"scenario_rendement_constant_pib", "baseline_part_refinancee"} <= set(
        donnees["hypotheses"]
    )
    assert set(donnees["hypotheses"]) <= hypotheses
    lignes = {v["annee"]: v for v in donnees["valeurs"]}
    assert lignes[2026]["ecart_dette"]["central"] == 0.0
    assert lignes[2046]["ecart_dette"]["central"] < 0.0


def test_scenario_sans_mesure_redonne_la_baseline(client: TestClient) -> None:
    donnees = client.post("/scenario", json={"mesures": []}).json()
    baseline = client.get("/baseline").json()
    for s, b in zip(donnees["valeurs"], baseline["valeurs"], strict=True):
        assert s["dette"] == pytest.approx(b["dette"])


@pytest.mark.parametrize(
    "mesure",
    [
        {"levier": "inexistant", "valeur": 1.0, "annee": 2027},
        {"levier": "tva_taux_normal", "valeur": 1.0, "annee": 2025},
        {"levier": "tva_taux_normal", "valeur": 50.0, "annee": 2027},
    ],
)
def test_scenario_mesure_invalide(client: TestClient, mesure: dict[str, object]) -> None:
    assert client.post("/scenario", json={"mesures": [mesure]}).status_code == 422


def test_scenario_non_journalise(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    corps = {"mesures": [{"levier": "tva_taux_normal", "valeur": 1.2345, "annee": 2031}]}
    with caplog.at_level(logging.DEBUG):
        client.post("/scenario", json=corps)
    serveur = [r.getMessage() for r in caplog.records if not r.name.startswith("httpx")]
    assert not any("1.2345" in m for m in serveur)


def attendu_provenance(client: TestClient) -> tuple[list[str], list[str]]:
    corps = {"mesures": [{"levier": "tva_taux_normal", "valeur": 1.0, "annee": 2027}]}
    donnees = client.post("/scenario", json=corps).json()
    return donnees["sources"], donnees["hypotheses"]


def test_export_reponses_unitaires(client: TestClient, tmp_path: Path) -> None:
    """x fois la réponse unitaire exportée redonne le scénario de l'API (calcul du site)."""
    exporter(tmp_path)
    unitaires = json.loads((tmp_path / "scenario-unitaire.json").read_text(encoding="utf-8"))
    assert unitaires["leviers"]["tva_taux_normal"]["sources"] == attendu_provenance(client)[0]
    reponse = unitaires["leviers"]["tva_taux_normal"]["reponses"]["2027"]
    x = 2.0
    corps = {"mesures": [{"levier": "tva_taux_normal", "valeur": x, "annee": 2027}]}
    attendu = client.post("/scenario", json=corps).json()["valeurs"]
    for i, ligne in enumerate(attendu):
        niveaux = [
            b[i] + x * u[i]
            for b, u in zip(unitaires["base_dette"], reponse["unite_dette"], strict=True)
        ]
        assert niveaux[0] == pytest.approx(ligne["dette"]["central"])
        assert min(niveaux) == pytest.approx(ligne["dette"]["bas"])
        assert max(niveaux) == pytest.approx(ligne["dette"]["haut"])
