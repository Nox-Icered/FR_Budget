"""Termes croisés entre leviers (combinaison sans double compte) : API et export du site."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

ANNEE = 2027
# Signes opposés : le terme croisé est négatif, ses bornes s'échangent.
MESURES = [("remunerations_point_indice", -2.0), ("csg_activite", 1.0)]
CROISE = "interaction__csg_activite__remunerations_point_indice"


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


@pytest.fixture(scope="module")
def unitaires(tmp_path_factory: pytest.TempPathFactory) -> Any:
    dossier: Path = tmp_path_factory.mktemp("export")
    exporter(dossier)
    return json.loads((dossier / "scenario-unitaire.json").read_text(encoding="utf-8"))


def _corps(mesures: list[tuple[str, float]]) -> dict[str, Any]:
    return {"mesures": [{"levier": lv, "valeur": x, "annee": ANNEE} for lv, x in mesures]}


def test_reponse_signale_les_interactions(client: TestClient) -> None:
    r = client.post("/scenario", json=_corps(MESURES)).json()
    assert r["interactions"] == [CROISE]
    assert r["interactions_non_chiffrees"] == []
    autre = client.post(
        "/scenario", json=_corps([("tva_taux_normal", 1.0), ("accise_gazole", 2.0)])
    ).json()
    assert autre["interactions"] == []
    assert autre["interactions_non_chiffrees"] == ["accises_tva"]


def test_terme_croise_refuse_en_entree(client: TestClient) -> None:
    r = client.post("/scenario", json=_corps([(CROISE, 1.0)]))
    assert r.status_code >= 400


def test_calcul_du_site_avec_terme_croise(client: TestClient, unitaires: Any) -> None:
    """Le calcul du site (web/lib/scenario.ts : avecInteractions puis calculer), reproduit
    ici, égale l'API pour deux mesures qui interagissent, de signes opposés."""
    assert unitaires["leviers"][CROISE]["interaction"] == [lv for lv, _ in MESURES]
    produit = MESURES[0][1] * MESURES[1][1]
    mesures = [*MESURES, (CROISE, produit)]
    attendu = client.post("/scenario", json=_corps(MESURES)).json()["valeurs"]
    reponses = {lv: unitaires["leviers"][lv]["reponses"][str(ANNEE)] for lv, _ in mesures}
    k_bas: int = unitaires["indices_effet"][1]
    k_haut: int = unitaires["indices_effet"][2]

    def indice(k: int, x: float) -> int:
        if x >= 0:
            return k
        return {k_bas: k_haut, k_haut: k_bas}.get(k, k)

    def somme(k: int, i: int) -> float:
        return float(sum(x * reponses[lv]["unite_dette"][indice(k, x)][i] for lv, x in mesures))

    for i, ligne in enumerate(attendu):
        ecarts = [somme(k, i) for k in unitaires["indices_effet"]]
        assert ecarts[0] == pytest.approx(ligne["ecart_dette"]["central"], abs=1e-8)
        assert min(ecarts) == pytest.approx(ligne["ecart_dette"]["bas"], abs=1e-8)
        assert max(ecarts) == pytest.approx(ligne["ecart_dette"]["haut"], abs=1e-8)


def test_export_des_interactions_non_chiffrees(unitaires: Any) -> None:
    mecanismes = {p["mecanisme"] for p in unitaires["interactions_non_chiffrees"]}
    assert "accises_tva" in mecanismes
    for p in unitaires["interactions_non_chiffrees"]:
        for levier in (*p["leviers_a"], *p["leviers_b"]):
            assert levier in unitaires["leviers"], levier
