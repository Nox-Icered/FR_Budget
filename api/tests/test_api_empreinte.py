"""Empreinte de version (fr_budget_api.app.empreinte_dossier)."""

from __future__ import annotations

from pathlib import Path

from fr_budget_api.app import empreinte_dossier


def test_empreinte_sans_les_caches_d_execution(tmp_path: Path) -> None:
    """Le bytecode écrit à l'exécution (__pycache__, .pyc) ne change pas l'empreinte : un lien
    partagé reproduit la même version quelle que soit la machine qui a lancé le code."""
    (tmp_path / "calcul.py").write_text("x = 1\n", encoding="utf-8")
    avant = empreinte_dossier(tmp_path)
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "calcul.cpython-312.pyc").write_bytes(b"\x00\x01")
    (tmp_path / "ancien.pyc").write_bytes(b"\x02")
    assert empreinte_dossier(tmp_path) == avant
    (tmp_path / "calcul.py").write_text("x = 2\n", encoding="utf-8")
    assert empreinte_dossier(tmp_path) != avant
