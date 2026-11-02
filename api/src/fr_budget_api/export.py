"""Exporte en JSON, pour le site statique, ce que sert l'API (mêmes fonctions, mêmes contenus).

Usage (depuis api/) : ``uv run python -m fr_budget_api.export ../web/donnees``

Aucune donnée saisie par un utilisateur n'entre ici : seulement les registres et les données
publiques traitées.

Cache facultatif des effets sur les ménages types (``FR_BUDGET_CACHE`` : un dossier) : leur
calcul avec OpenFisca prend une vingtaine de minutes. Le fichier en cache porte l'empreinte de
tout ce dont il dépend (code du moteur et de l'API, registres, données traitées, versions des
dépendances verrouillées) ; il n'est relu que si cette empreinte est identique. Sans la
variable, rien n'est mis en cache.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from fr_budget.apu import depenses_par_fonction
from fr_budget.registres.verification import RACINE_DEPOT

from fr_budget_api.app import (
    REGISTRES,
    budget_etat,
    catalogue_credits_missions,
    catalogue_depenses_fiscales,
    depense_menages,
    depenses_fonctions,
    effets_leviers_menages,
    empreinte_dossier,
    entreprises,
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


def _texte(contenu: Any, compact: bool = False) -> str:
    indent = None if compact else 1
    separateurs = (",", ":") if compact else None
    return (
        json.dumps(
            contenu, ensure_ascii=False, indent=indent, separators=separateurs, sort_keys=True
        )
        + "\n"
    )


def _ecrire(dossier: Path, nom: str, contenu: Any, compact: bool = False) -> None:
    (dossier / nom).write_text(_texte(contenu, compact), encoding="utf-8")


VARIABLE_CACHE = "FR_BUDGET_CACHE"
VERROUS = (RACINE_DEPOT / "moteur" / "uv.lock", RACINE_DEPOT / "api" / "uv.lock")


def empreinte_effets_menages() -> str:
    """Empreinte de tout ce dont dépendent les effets sur les ménages types."""
    h = hashlib.sha256()
    h.update(json.dumps(version_donnees(), sort_keys=True).encode())
    h.update(empreinte_dossier(Path(__file__).parent).encode())
    for verrou in VERROUS:
        h.update(verrou.read_bytes())
    return h.hexdigest()[:16]


def texte_effets_menages() -> str:
    """Fichier ``menages-effets.json`` (texte exact), relu du cache quand l'empreinte est la
    même : le fichier écrit est identique, avec ou sans cache."""
    dossier = os.environ.get(VARIABLE_CACHE)
    if not dossier:
        return _texte(effets_leviers_menages(), compact=True)
    chemin = Path(dossier) / f"menages-effets-{empreinte_effets_menages()}.json"
    if chemin.exists():
        return chemin.read_text(encoding="utf-8")
    texte = _texte(effets_leviers_menages(), compact=True)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(texte, encoding="utf-8")
    return texte


def exporter(dossier: Path) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    _ecrire(dossier, "version.json", version_donnees())
    _ecrire(dossier, "journal.json", journal())
    _ecrire(dossier, "menages-types.json", menages_types())
    _ecrire(dossier, "entreprises.json", entreprises())
    _ecrire(dossier, "depense-menages.json", depense_menages())
    (dossier / "menages-effets.json").write_text(texte_effets_menages(), encoding="utf-8")
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
    _ecrire(dossier, "budget-etat.json", budget_etat())
    _ecrire(dossier, "validation.json", resume_validation())
    _ecrire(dossier, "baseline.json", serie_baseline())
    _ecrire(dossier, "depenses-fiscales.json", catalogue_depenses_fiscales())
    _ecrire(dossier, "credits-missions.json", catalogue_credits_missions())
    # Fichier volumineux (réponses par levier, année d'entrée et trajectoire) : sans indentation.
    _ecrire(dossier, "scenario-unitaire.json", reponses_unitaires(), compact=True)


if __name__ == "__main__":
    exporter(Path(sys.argv[1]))
