"""Tests de l'API et de l'export des ménages types."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

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
