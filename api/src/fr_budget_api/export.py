"""Exporte en JSON, pour le site statique, ce que sert l'API (mêmes fonctions, mêmes contenus).

Usage (depuis api/) : ``uv run python -m fr_budget_api.export ../web/donnees``

Aucune donnée saisie par un utilisateur n'entre ici : seulement les registres et les données
publiques traitées.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fr_budget_api.app import (
    REGISTRES,
    depenses_fonctions,
    registre,
    serie_comptes,
    version_donnees,
)

SOUS_SECTEURS = ("S13", "S1311", "S1313", "S1314")
INDICATEURS = (
    "depenses",
    "recettes",
    "capacite_financement",
    "interets_verses",
    "dette_maastricht",
)
DERNIERE_ANNEE_COFOG = 2024
"""Dernière année publiée par Eurostat dans le jeu téléchargé (voir docs/fiches/comptes_apu.md)."""


def _ecrire(dossier: Path, nom: str, contenu: Any) -> None:
    (dossier / nom).write_text(
        json.dumps(contenu, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )


def exporter(dossier: Path) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    _ecrire(dossier, "version.json", version_donnees())
    for nom in REGISTRES:
        _ecrire(dossier, f"registre-{nom}.json", registre(nom))
    _ecrire(
        dossier,
        "comptes-apu.json",
        {secteur: {i: serie_comptes(secteur, i) for i in INDICATEURS} for secteur in SOUS_SECTEURS}
        | {"S1": {"pib": serie_comptes("S1", "pib")}},
    )
    _ecrire(dossier, "cofog.json", depenses_fonctions(DERNIERE_ANNEE_COFOG, "S13"))


if __name__ == "__main__":
    exporter(Path(sys.argv[1]))
