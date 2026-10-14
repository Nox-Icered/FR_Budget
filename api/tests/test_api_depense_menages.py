"""Tests de l'API et de l'export de la dépense supplémentaire des ménages (TVA, accises)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application, depense_menages, registre
from fr_budget_api.export import exporter


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_depense_menages(client: TestClient) -> None:
    reponse = client.get("/depense-menages").json()
    assert set(reponse["leviers"]) == {"tva_taux_normal", "accise_gazole", "accise_essences"}
    deciles = {c["id"]: c for c in reponse["nomenclatures"]["decile"]}
    assert set(deciles) == {*map(str, range(1, 11)), "TOT"}
    assert {c["id"] for c in reponse["nomenclatures"]["type_menage"]} == {
        "1",
        "2",
        "3",
        "4",
        "5",
        "TOT",
    }
    tva = deciles["1"]["effets"]["tva_taux_normal"]
    assert 0 < tva["bas"] <= tva["central"] <= tva["haut"]


def test_controles_et_sources() -> None:
    donnees = depense_menages()
    assert [c["annee"] for c in donnees["controles"]] == [2015, 2022]
    connues = {s["id"] for s in registre("sources") or []}
    assert set(donnees["sources"]) <= connues
    assert all(c["source"] in connues for c in donnees["controles"])


def test_export(tmp_path: Path) -> None:
    exporter(tmp_path)
    donnees = json.loads((tmp_path / "depense-menages.json").read_text(encoding="utf-8"))
    assert donnees["annee_enquete"] == 2017
