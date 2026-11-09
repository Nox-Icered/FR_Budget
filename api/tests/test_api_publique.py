"""API publique versionnée (/v1) : contrat, erreurs sans écho de la saisie, garde-fous."""

from __future__ import annotations

import logging
from typing import Any

import pytest
from fastapi.testclient import TestClient
from fr_budget import scenario as sc
from fr_budget.menages import deciles as dc

from fr_budget_api.app import creer_application
from fr_budget_api.openapi import FICHIER, texte
from fr_budget_api.publique import LEVIERS_INTERNES, MESURES_MAX, TAILLE_MAX

ANNEE = 2027


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def _mesures(*paires: tuple[str, float]) -> dict[str, Any]:
    return {"mesures": [{"levier": lv, "valeur": x, "annee": ANNEE} for lv, x in paires]}


def test_presentation_et_version(client: TestClient) -> None:
    r = client.get("/v1/").json()
    assert r["version"]["api"] == "1"
    assert "/scenario" in r["routes"] and "/objectif" in r["routes"]
    assert r["licences"]["code"] == "AGPL-3.0-or-later"
    assert client.get("/v1/version").json()["api"] == "1"


def test_leviers(client: TestClient) -> None:
    leviers = client.get("/v1/leviers").json()
    ids = {lv["id"] for lv in leviers}
    assert {"tva_taux_normal", "ondam_progression", "csg_activite"} <= ids
    assert not ids & set(LEVIERS_INTERNES)
    for lv in leviers:
        assert lv["statut"] in {"beta", "valide", "non_publie"}
        assert "{" not in lv["libelle"]
        bas, haut = lv["bornes"]
        assert bas <= haut
        r = lv["rendement_unitaire_md_euros"]
        assert r["bas"] <= r["central"] <= r["haut"]
    tva = client.get("/v1/leviers/tva_taux_normal").json()
    assert tva["unite"] and tva["libelle"] and tva["sources"]


def test_levier_inconnu_format_d_erreur(client: TestClient) -> None:
    r = client.get("/v1/leviers/inconnu")
    assert r.status_code == 404
    assert r.json()["erreur"]["code"] == "levier_inconnu"


def test_scenario_identique_a_la_route_du_site(client: TestClient) -> None:
    corps = _mesures(("tva_taux_normal", 1.0), ("csg_activite", -0.5))
    v1 = client.post("/v1/scenario", json=corps).json()
    site = client.post("/scenario", json=corps).json()
    assert v1["valeurs"] == site["valeurs"]
    assert v1["version"]["api"] == "1"


def test_mesure_invalide_sans_echo_de_la_saisie(client: TestClient) -> None:
    r = client.post("/v1/scenario", json=_mesures(("tva_taux_normal", 987.654)))
    assert r.status_code == 422
    assert r.json()["erreur"]["code"] == "mesure_invalide"
    assert "987" not in r.text
    r = client.post(
        "/v1/scenario",
        json=_mesures(("ondam_progression", -1.0), ("franchises_participations", 10.0)),
    )
    assert r.json()["erreur"]["code"] == "mesure_invalide"


def test_requete_mal_formee_noms_de_champs_seulement(client: TestClient) -> None:
    corps = {"mesures": [{"levier": "tva_taux_normal", "valeur": "SECRET_77", "annee": ANNEE}]}
    r = client.post("/v1/scenario", json=corps)
    assert r.status_code == 422
    erreur = r.json()["erreur"]
    assert erreur["code"] == "requete_invalide"
    assert erreur["champs"] == ["mesures.0.valeur"]
    assert "SECRET_77" not in r.text


def test_garde_fous(client: TestClient) -> None:
    trop = _mesures(*[("tva_taux_normal", 0.1)] * (MESURES_MAX + 1))
    assert client.post("/v1/scenario", json=trop).status_code == 422
    gros = '{"mesures": [], "x": "' + "a" * TAILLE_MAX + '"}'
    r = client.post("/v1/scenario", content=gros, headers={"content-type": "application/json"})
    assert r.status_code == 413
    assert r.json()["erreur"]["code"] == "requete_trop_grande"
    hors = {"mesures": [{"levier": "tva_taux_normal", "valeur": 1.0, "annee": 2020}]}
    assert client.post("/v1/scenario", json=hors).status_code == 422


def test_deciles_identiques_au_moteur(client: TestClient) -> None:
    r = client.post("/v1/deciles", json=_mesures(("tva_taux_normal", 1.0))).json()
    moteur = dc.repartition([sc.Mesure("tva_taux_normal", 1.0, ANNEE)])
    assert len(r["euros_par_unite_de_consommation"]) == dc.NOMBRE
    for d in range(dc.NOMBRE):
        assert r["milliards_euros"][d]["central"] == pytest.approx(moteur.milliards[d].central)
    assert r["statut"] == "beta"
    assert client.post("/v1/deciles", json=_mesures(("inconnu", 1.0))).status_code == 422


def test_objectif(client: TestClient) -> None:
    base = client.post("/v1/scenario", json={"mesures": []}).json()
    dette_2040 = next(v for v in base["valeurs"] if v["annee"] == 2040)["dette"]["central"]
    corps = {
        "levier": "tva_taux_normal",
        "entree": ANNEE,
        "indicateur": "dette",
        "annee": 2040,
        "cible": dette_2040 - 0.2,
    }
    r = client.post("/v1/objectif", json=corps).json()
    assert r["atteignable"] and r["valeur"]["central"] > 0
    assert r["sans_mesure"] == pytest.approx(dette_2040)
    hors = client.post("/v1/objectif", json={**corps, "levier": "accise_gazole", "cible": 0}).json()
    assert hors["atteignable"] is False and hors["valeur"] is None
    assert (
        client.post("/v1/objectif", json={**corps, "annee": 2030, "entree": 2035}).status_code
        == 422
    )


def test_interactions(client: TestClient) -> None:
    r = client.get("/v1/interactions").json()
    assert r["chiffrees"] and r["non_chiffrees"]


def test_cors_ouvert_sans_cookies(client: TestClient) -> None:
    r = client.options(
        "/v1/scenario",
        headers={"Origin": "https://exemple.org", "Access-Control-Request-Method": "POST"},
    )
    assert r.headers.get("access-control-allow-origin") == "*"
    assert "access-control-allow-credentials" not in r.headers


def test_aucune_saisie_journalisee(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.DEBUG):
        client.post("/v1/scenario", json=_mesures(("TRACE_91", 1.0)))
        client.post(
            "/v1/objectif",
            json={
                "levier": "TRACE_92",
                "entree": ANNEE,
                "indicateur": "dette",
                "annee": 2040,
                "cible": 90,
            },
        )
    serveur = [r.getMessage() for r in caplog.records if not r.name.startswith("httpx")]
    assert not any("TRACE_9" in m for m in serveur)


def test_description_openapi_versionnee() -> None:
    """``api/openapi-v1.json`` est à jour : régénérer avec ``python -m fr_budget_api.openapi``."""
    assert FICHIER.read_text(encoding="utf-8") == texte()
