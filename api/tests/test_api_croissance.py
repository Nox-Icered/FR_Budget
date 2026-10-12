"""Tests de l'API et de l'export pour l'effet de croissance (lot 3.2)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application
from fr_budget_api.export import exporter

ANNEE = 2027
MESURES = [("tva_taux_normal", 1.0), ("indexation_pensions_prestations", -1.0)]


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


@pytest.fixture(scope="module")
def unitaires(tmp_path_factory: pytest.TempPathFactory) -> Any:
    dossier: Path = tmp_path_factory.mktemp("export")
    exporter(dossier)
    return json.loads((dossier / "scenario-unitaire.json").read_text(encoding="utf-8"))


def _corps(croissance: bool) -> dict[str, Any]:
    return {
        "mesures": [{"levier": lv, "valeur": x, "annee": ANNEE} for lv, x in MESURES],
        "croissance": croissance,
    }


def test_desactive_par_defaut(client: TestClient) -> None:
    sans = client.post("/scenario", json={"mesures": _corps(False)["mesures"]}).json()
    assert sans["croissance"] is False
    assert sans["valeurs"] == client.post("/scenario", json=_corps(False)).json()["valeurs"]


def test_sources_de_la_croissance_citees(client: TestClient) -> None:
    avec = client.post("/scenario", json=_corps(True)).json()
    assert {"insee_mesange_2017", "ofce_policy_brief_146"} <= set(avec["sources"])
    assert "croissance_multiplicateur_tva" in avec["hypotheses"]


def test_calcul_du_site_avec_croissance(client: TestClient, unitaires: Any) -> None:
    """Le calcul du site (web/lib/scenario.ts), reproduit ici, égale l'API avec la croissance :
    trajectoires au multiplicateur central, plus les coins (effet bas ou haut, multiplicateur
    bas ou haut, commun à toutes les mesures)."""
    u = unitaires
    attendu = client.post("/scenario", json=_corps(True)).json()["valeurs"]
    k_bas: int = u["indices_effet"][1]
    k_haut: int = u["indices_effet"][2]

    def indice(k: int, x: float) -> int:
        return k if x >= 0 else {k_bas: k_haut, k_haut: k_bas}.get(k, k)

    def somme(k: int, j: str, i: int) -> float:
        total = 0.0
        for lv, x in MESURES:
            r = u["leviers"][lv]["reponses"][str(ANNEE)]
            m = u["leviers"][lv]["multiplicateur"][j]
            kk = indice(k, x)
            total += x * (r["unite_dette"][kk][i] + m * r["croissance_dette"][kk][i])
        return total

    coins = [(k, j) for j in ("bas", "haut") for k in (k_bas, k_haut)]
    for i, ligne in enumerate(attendu):
        ecarts = [somme(k, "central", i) for k in u["indices_effet"]]
        ecarts += [somme(k, j, i) for k, j in coins]
        assert ecarts[0] == pytest.approx(ligne["ecart_dette"]["central"])
        assert min(ecarts) == pytest.approx(ligne["ecart_dette"]["bas"])
        assert max(ecarts) == pytest.approx(ligne["ecart_dette"]["haut"])
        niveaux = [b[i] + somme(k, "central", i) for k, b in enumerate(u["base_dette"])]
        niveaux += [u["base_dette"][k][i] + somme(k, j, i) for k, j in coins]
        assert min(niveaux) == pytest.approx(ligne["dette"]["bas"])
        assert max(niveaux) == pytest.approx(ligne["dette"]["haut"])


def test_export_cite_les_sources_de_la_croissance(unitaires: Any) -> None:
    assert "ofce_policy_brief_146" in unitaires["croissance"]["sources"]
    m = unitaires["leviers"]["tva_taux_normal"]["multiplicateur"]
    assert m["bas"] <= m["central"] <= m["haut"]
