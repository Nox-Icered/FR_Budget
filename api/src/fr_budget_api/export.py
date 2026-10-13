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

from fr_budget.apu import depenses_par_fonction

from fr_budget_api.app import (
    REGISTRES,
    catalogue_credits_missions,
    catalogue_depenses_fiscales,
    depenses_fonctions,
    journal,
    menages_types,
    registre,
    reponses_unitaires,
    resume_validation,
    serie_baseline,
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


def _ecrire(dossier: Path, nom: str, contenu: Any, compact: bool = False) -> None:
    indent = None if compact else 1
    separateurs = (",", ":") if compact else None
    (dossier / nom).write_text(
        json.dumps(
            contenu, ensure_ascii=False, indent=indent, separators=separateurs, sort_keys=True
        )
        + "\n",
        encoding="utf-8",
    )


def exporter(dossier: Path) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    _ecrire(dossier, "version.json", version_donnees())
    _ecrire(dossier, "journal.json", journal())
    _ecrire(dossier, "menages-types.json", menages_types())
    for nom in REGISTRES:
        _ecrire(dossier, f"registre-{nom}.json", registre(nom))
    _ecrire(
        dossier,
        "comptes-apu.json",
        {
            # Listes ordonnées : le site affiche exactement ce qui est exporté, dans cet ordre.
            "sous_secteurs": list(SOUS_SECTEURS),
            "indicateurs": list(INDICATEURS),
            "series": {
                secteur: {i: serie_comptes(secteur, i) for i in INDICATEURS}
                for secteur in SOUS_SECTEURS
            },
        },
    )
    derniere_annee = max(a for a, s, _ in depenses_par_fonction() if s == "S13")
    _ecrire(dossier, "cofog.json", depenses_fonctions(derniere_annee, "S13"))
    _ecrire(dossier, "validation.json", resume_validation())
    _ecrire(dossier, "baseline.json", serie_baseline())
    _ecrire(dossier, "depenses-fiscales.json", catalogue_depenses_fiscales())
    _ecrire(dossier, "credits-missions.json", catalogue_credits_missions())
    # Fichier volumineux (réponses par levier, année d'entrée et trajectoire) : sans indentation.
    _ecrire(dossier, "scenario-unitaire.json", reponses_unitaires(), compact=True)


if __name__ == "__main__":
    exporter(Path(sys.argv[1]))
