"""Tests de l'API et de l'export du module « entreprises »."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application, entreprises, registre
from fr_budget_api.export import exporter


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_entreprises(client: TestClient) -> None:
    reponse = client.get("/entreprises").json()
    leviers = {lv["id"]: lv for lv in reponse["leviers"]}
    assert set(leviers) == {
        "cotisations_patronales_taux",
        "allegements_generaux",
        "is_taux_normal",
        "is_surtaxe_grandes_entreprises",
    }
    cotisations = leviers["cotisations_patronales_taux"]
    total = sum(c["effet"]["central"] for c in cotisations["nomenclatures"]["taille"])
    assert total == pytest.approx(cotisations["effet_national"]["central"])
    # Surtaxe : pas de répartition par secteur.
    assert leviers["is_surtaxe_grandes_entreprises"]["nomenclatures"]["secteur"] == []


def test_controles_publies() -> None:
    controles = {c["id"]: c for c in entreprises()["controles"]}
    assert set(controles) == {"point_2025", "point_2017", "allegements"}
    assert all(abs(c["ecart"]) <= 0.10 for c in controles.values())


def test_sources_au_registre() -> None:
    connues = {s["id"] for s in registre("sources") or []}
    for levier in entreprises()["leviers"]:
        assert set(levier["sources"]) <= connues
    for controle in entreprises()["controles"]:
        assert controle["source"] in connues


def test_export(tmp_path: Path) -> None:
    exporter(tmp_path)
    contenu = json.loads((tmp_path / "entreprises.json").read_text(encoding="utf-8"))
    assert contenu == json.loads(json.dumps(entreprises()))
