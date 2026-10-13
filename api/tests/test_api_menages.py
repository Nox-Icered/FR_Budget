"""Tests de l'API et de l'export des ménages types."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import creer_application, menages_types
from fr_budget_api.export import exporter


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_menages_types(client: TestClient) -> None:
    menages = client.get("/menages-types").json()
    assert {m["id"] for m in menages} >= {"celibataire_smic", "couple_2_enfants"}
    for m in menages:
        attendu = m["net_avant_impot"] - m["impot_revenu"] + sum(m["prestations"].values())
        assert m["net_apres_impot"] == pytest.approx(attendu, abs=0.05)


def test_export_des_menages_types(tmp_path: Path) -> None:
    exporter(tmp_path)
    contenu = json.loads((tmp_path / "menages-types.json").read_text(encoding="utf-8"))
    assert contenu == menages_types()
