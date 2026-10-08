"""Règle 3 de CLAUDE.md : aucun texte du site n'emploie un terme orientant.

Les termes interdits sont ceux de registres/libelles_interdits.yaml, déjà appliqués aux
libellés des leviers ; ici, à tous les textes affichés par le site (web/messages/fr.json).
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator
from typing import Any

import yaml

from fr_budget.registres.verification import RACINE_DEPOT


def _textes(noeud: Any) -> Iterator[str]:
    if isinstance(noeud, dict):
        for valeur in noeud.values():
            yield from _textes(valeur)
    elif isinstance(noeud, str):
        yield noeud


def test_aucun_terme_interdit_dans_les_textes_du_site() -> None:
    termes = yaml.safe_load(
        (RACINE_DEPOT / "registres" / "libelles_interdits.yaml").read_text(encoding="utf-8")
    )["termes"]
    messages = json.loads(
        (RACINE_DEPOT / "web" / "messages" / "fr.json").read_text(encoding="utf-8")
    )
    trouves = [
        (terme, texte)
        for texte in _textes(messages)
        for terme in termes
        if re.search(rf"\b{re.escape(str(terme))}\b", texte, re.IGNORECASE)
    ]
    assert not trouves, trouves
