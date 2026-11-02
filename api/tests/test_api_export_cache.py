"""Cache des effets sur les ménages types dans l'export (``FR_BUDGET_CACHE``)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from fr_budget_api import export


def test_cache_relu_si_empreinte_identique(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    appels: list[int] = []

    def calcul() -> dict[str, Any]:
        appels.append(1)
        return {"b": [1.5, 2], "a": {"x": None}}

    monkeypatch.setattr(export, "effets_leviers_menages", calcul)
    monkeypatch.setattr(export, "empreinte_effets_menages", lambda: "abc")
    monkeypatch.setenv(export.VARIABLE_CACHE, str(tmp_path))
    premier = export.texte_effets_menages()
    second = export.texte_effets_menages()
    assert premier == second
    assert len(appels) == 1
    # Une autre empreinte (code, registres, données ou dépendances modifiés) : nouveau calcul.
    monkeypatch.setattr(export, "empreinte_effets_menages", lambda: "def")
    export.texte_effets_menages()
    assert len(appels) == 2


def test_sans_variable_rien_en_cache(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv(export.VARIABLE_CACHE, raising=False)
    monkeypatch.setattr(export, "effets_leviers_menages", lambda: {"a": 1})
    assert export.texte_effets_menages() == export._texte({"a": 1}, compact=True)
    assert list(tmp_path.iterdir()) == []


def test_empreinte_stable() -> None:
    assert export.empreinte_effets_menages() == export.empreinte_effets_menages()
