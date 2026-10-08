"""Lecture des registres par le moteur de calcul."""

from __future__ import annotations

from functools import cache

import yaml

from fr_budget.registres.schemas import Hypothese
from fr_budget.registres.verification import RACINE_DEPOT


@cache
def _hypotheses() -> dict[str, Hypothese]:
    contenu = yaml.safe_load(
        (RACINE_DEPOT / "registres" / "hypotheses.yaml").read_text(encoding="utf-8")
    )
    return {h["id"]: Hypothese.model_validate(h) for h in contenu["hypotheses"]}


def hypothese(identifiant: str) -> Hypothese:
    """Hypothèse du registre ; ``KeyError`` si elle n'existe pas."""
    return _hypotheses()[identifiant]
