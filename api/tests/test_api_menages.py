"""Tests de l'API et de l'export des ménages types."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from fr_budget.menages import types as module_menages

from fr_budget_api.app import SOURCES_MENAGES, creer_application, menages_types, registre
from fr_budget_api.export import exporter


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_menages_types(client: TestClient) -> None:
    reponse = client.get("/menages-types").json()
    assert reponse["unite"] == "euros par an"
    assert "insee_premiere_2079" in reponse["sources"]
    menages = reponse["menages"]
    assert {m["id"] for m in menages} >= {
        "celibataire_smic",
        "couple_2_enfants",
        "retraite_seul",
        "artisan",
    }
    for m in menages:
        attendu = (
            m["net_avant_impot"]
            + m["pension_nette"]
            + m["revenu_independant_net"]
            - m["impot_revenu"]
            + sum(m["prestations"].values())
        )
        assert m["net_apres_impot"] == pytest.approx(attendu, abs=0.05)


def test_export_des_menages_types(tmp_path: Path) -> None:
    exporter(tmp_path)
    contenu = json.loads((tmp_path / "menages-types.json").read_text(encoding="utf-8"))
    assert contenu == menages_types()


def test_sources_des_menages_au_registre() -> None:
    connues = {s["id"] for s in registre("sources") or []}
    assert set(SOURCES_MENAGES) <= connues


MENAGE_SAISI = {
    "adultes": [
        {"statut": "salarie", "montant_mensuel": 2345.67, "annee_naissance": 1984},
        {"statut": "retraite", "montant_mensuel": 1432.1, "annee_naissance": 1957},
    ],
    "annees_naissance_enfants": [2014],
}


def test_mon_menage(client: TestClient) -> None:
    reponse = client.post("/mon-menage", json=MENAGE_SAISI)
    assert reponse.status_code == 200
    m = reponse.json()
    assert m["salaire_brut"] == pytest.approx(12 * 2345.67, abs=0.05)
    assert m["pension_brute"] == pytest.approx(12 * 1432.1, abs=0.05)
    attendu = (
        m["net_avant_impot"]
        + m["pension_nette"]
        + m["revenu_independant_net"]
        - m["impot_revenu"]
        + sum(m["prestations"].values())
    )
    assert m["net_apres_impot"] == pytest.approx(attendu, abs=0.05)


def test_mon_menage_comme_le_menage_type(client: TestClient) -> None:
    from fr_budget.menages import types as t

    brut = t.brut_mensuel(t.SMIC, t.ANNEE)
    corps = {"adultes": [{"statut": "salarie", "montant_mensuel": brut, "annee_naissance": 1995}]}
    m = client.post("/mon-menage", json=corps).json()
    type_ = next(x for x in menages_types()["menages"] if x["id"] == "celibataire_smic")
    assert m["net_apres_impot"] == pytest.approx(type_["net_apres_impot"])


@pytest.mark.parametrize(
    "corps",
    [
        {"adultes": []},
        {"adultes": [{"statut": "chomeur", "montant_mensuel": 1, "annee_naissance": 1990}]},
        {"adultes": [{"statut": "salarie", "montant_mensuel": -1, "annee_naissance": 1990}]},
        {"adultes": [{"statut": "salarie", "montant_mensuel": 1, "annee_naissance": 2024}]},
    ],
)
def test_mon_menage_saisie_invalide(client: TestClient, corps: dict[str, object]) -> None:
    assert client.post("/mon-menage", json=corps).status_code == 422


def test_mon_menage_non_journalise(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    # Règle 5 : aucune valeur saisie dans les journaux du serveur.
    with caplog.at_level(logging.DEBUG):
        client.post("/mon-menage", json=MENAGE_SAISI)
    serveur = [r.getMessage() for r in caplog.records if not r.name.startswith("httpx")]
    assert not any("2345" in m or "1432" in m or "1984" in m for m in serveur)


def test_bornes_saisie(client: TestClient) -> None:
    saisie = client.get("/menages-types").json()["saisie"]
    assert saisie["adultes_max"] == 2
    assert saisie["annee_naissance_adulte_max"] < saisie["annee"]
    assert saisie["annee_naissance_enfant_max"] == saisie["annee"]


def test_cors_absent_par_defaut(client: TestClient) -> None:
    reponse = client.options(
        "/mon-menage",
        headers={"Origin": "https://exemple.fr", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in reponse.headers


def test_cors_origine_configuree(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FR_BUDGET_ORIGINES", "https://exemple.fr")
    reponse = TestClient(creer_application()).options(
        "/mon-menage",
        headers={"Origin": "https://exemple.fr", "Access-Control-Request-Method": "POST"},
    )
    assert reponse.headers["access-control-allow-origin"] == "https://exemple.fr"


def test_effet_levier_route(client: TestClient) -> None:
    reponse = client.get("/menages-types/effet", params={"levier": "csg_activite", "valeur": 1})
    assert reponse.status_code == 200
    corps = reponse.json()
    assert set(corps["menages"]) == set(module_menages.PROFILS)
    avant = client.get("/menages-types").json()["menages"]
    median = next(m for m in avant if m["id"] == "celibataire_median")
    assert corps["menages"]["celibataire_median"]["net_avant_impot"] < median["net_avant_impot"]


@pytest.mark.parametrize(
    ("levier", "valeur", "statut"),
    [("tva_taux_normal", 1, 404), ("inconnu", 1, 404), ("csg_activite", 50, 422)],
)
def test_effet_levier_refuse(client: TestClient, levier: str, valeur: float, statut: int) -> None:
    reponse = client.get("/menages-types/effet", params={"levier": levier, "valeur": valeur})
    assert reponse.status_code == statut


def test_export_des_effets_des_leviers(tmp_path: Path) -> None:
    exporter(tmp_path)
    effets = json.loads((tmp_path / "menages-effets.json").read_text(encoding="utf-8"))
    assert {lev["id"] for lev in effets["leviers"]} == set(effets["effets"])
    for par_sens in effets["effets"].values():
        assert set(par_sens) == {"hausse", "baisse"}
        for menages in par_sens.values():
            assert set(menages) == set(module_menages.PROFILS)
    # Pension du retraité : effet de l'indexation non chiffré (part des pensions de base).
    assert effets["effets"]["indexation_pensions_prestations"]["hausse"]["retraite_seul"] is None
    assert "tva_taux_normal" in effets["sans_effet"]
