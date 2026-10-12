"""Tests des contenus des pages Journal et Relectures (lot 3.5)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from fr_budget_api.app import FICHES, creer_application, journal
from fr_budget_api.export import exporter

# Ligne de tableau qui commence par une date complète : seules les sections « Journal » en ont.
DATEE = re.compile(r"^\| \d{4}-\d{2}-\d{2} \|")


@pytest.fixture(scope="module")
def client() -> TestClient:
    return TestClient(creer_application())


def test_journal_reprend_toutes_les_lignes_des_fiches() -> None:
    attendu = sum(
        sum(1 for ligne in f.read_text(encoding="utf-8").splitlines() if DATEE.match(ligne))
        for f in FICHES.glob("*.md")
        if not f.name.startswith("_")
    )
    assert len(journal()) == attendu


def test_journal_du_plus_recent_au_plus_ancien(client: TestClient) -> None:
    lignes = client.get("/journal").json()
    dates = [x["date"] for x in lignes]
    assert dates == sorted(dates, reverse=True)
    assert all((FICHES / f"{x['fiche']}.md").is_file() for x in lignes)
    assert not any("`" in x["changement"] or "](" in x["changement"] for x in lignes)


def test_registre_des_relectures_lisible(client: TestClient) -> None:
    assert isinstance(client.get("/registres/relectures").json(), list)


def test_export_du_journal(tmp_path: Path) -> None:
    exporter(tmp_path)
    assert json.loads((tmp_path / "journal.json").read_text(encoding="utf-8")) == journal()
    assert (tmp_path / "registre-relectures.json").is_file()
