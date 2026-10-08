"""API FastAPI sans état (lot 1.4 du plan).

Règles (CLAUDE.md) : l'API ne stocke rien et ne journalise aucune donnée saisie par
l'utilisateur ; chaque réponse chiffrée indique sa source (identifiant du registre) et son
unité. Lancer sans journal d'accès :

    uv run uvicorn fr_budget_api.app:application --no-access-log

Points d'entrée : ``/sante``, ``/version``, ``/registres/{nom}``, ``/comptes-apu``,
``/depenses-par-fonction``. La baseline et les scénarios viendront avec les lots 1.3 et suivants.
"""

from __future__ import annotations

import hashlib
from functools import cache
from importlib.metadata import version
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fr_budget.apu import comptes_apu, depenses_par_fonction
from fr_budget.registres.verification import RACINE_DEPOT, Rapport, charger

SOURCE_COMPTES_APU = "insee_comptes_nationaux_2025"
SOURCE_COFOG = "eurostat_gov_10a_exp"
UNITE = "Md€"
REGISTRES = {
    "sources": "sources",
    "jeux-de-donnees": "datasets",
    "hypotheses": "hypotheses",
    "leviers": "leviers",
    "chiffrages": "chiffrages",
}


def empreinte_dossier(dossier: Path) -> str:
    """Empreinte SHA-256 du contenu d'un dossier (chemins relatifs et octets, ordre trié)."""
    h = hashlib.sha256()
    for fichier in sorted(p for p in dossier.rglob("*") if p.is_file()):
        h.update(fichier.relative_to(dossier).as_posix().encode())
        h.update(fichier.read_bytes())
    return h.hexdigest()


@cache
def _version() -> dict[str, str]:
    return {
        "moteur": version("fr-budget"),
        "registres": empreinte_dossier(RACINE_DEPOT / "registres"),
        "donnees": empreinte_dossier(RACINE_DEPOT / "data" / "processed"),
    }


@cache
def _registres() -> dict[str, list[dict[str, Any]]]:
    rapport = Rapport()
    contenu = charger(RACINE_DEPOT / "registres", rapport)
    if rapport.erreurs:
        msg = f"registres invalides : {rapport.erreurs}"
        raise RuntimeError(msg)
    return {
        nom: [m.model_dump(mode="json", exclude_none=True) for m in getattr(contenu, attribut)]
        for nom, attribut in REGISTRES.items()
    }


def creer_application() -> FastAPI:
    app = FastAPI(
        title="Simulateur du budget des administrations publiques",
        description="API sans état : aucune donnée saisie n'est stockée ni journalisée.",
        version=version("fr-budget-api"),
    )

    @app.get("/sante")
    def sante() -> dict[str, str]:
        return {"statut": "ok"}

    @app.get("/version")
    def version_donnees() -> dict[str, str]:
        """Version du moteur et empreintes des registres et des données traitées."""
        return _version()

    @app.get("/registres/{nom}")
    def registre(nom: str) -> list[dict[str, Any]]:
        if nom not in REGISTRES:
            raise HTTPException(status_code=404, detail="registre inconnu")
        return _registres()[nom]

    @app.get("/comptes-apu")
    def comptes(sous_secteur: str, indicateur: str) -> dict[str, Any]:
        """Série annuelle d'un indicateur des comptes des APU pour un sous-secteur."""
        c = comptes_apu()
        annees = c.annees(sous_secteur, indicateur)
        if not annees:
            raise HTTPException(status_code=404, detail="série inconnue")
        return {
            "source": SOURCE_COMPTES_APU,
            "unite": UNITE,
            "sous_secteur": sous_secteur,
            "indicateur": indicateur,
            "valeurs": [
                {"annee": a, "valeur": c.valeur(a, sous_secteur, indicateur)} for a in annees
            ],
        }

    @app.get("/depenses-par-fonction")
    def fonctions(annee: int, sous_secteur: str) -> dict[str, Any]:
        """Dépenses par fonction COFOG d'un sous-secteur pour une année."""
        valeurs = [
            {"cofog": code, "valeur": v}
            for (a, s, code), v in sorted(depenses_par_fonction().items())
            if a == annee and s == sous_secteur
        ]
        if not valeurs:
            raise HTTPException(status_code=404, detail="année ou sous-secteur absent")
        return {
            "source": SOURCE_COFOG,
            "unite": UNITE,
            "annee": annee,
            "sous_secteur": sous_secteur,
            "valeurs": valeurs,
        }

    return app


application = creer_application()
