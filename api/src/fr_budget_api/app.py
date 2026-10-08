"""API FastAPI sans état (lot 1.4 du plan).

Règles (CLAUDE.md) : l'API ne stocke rien et ne journalise aucune donnée saisie par
l'utilisateur ; chaque réponse chiffrée indique sa source (identifiant du registre) et son
unité. Le journal d'accès d'uvicorn (qui contiendrait les paramètres des requêtes) est
désactivé par ``creer_application`` elle-même ; lancer avec ``python -m fr_budget_api.serveur``.

Points d'entrée : ``/sante``, ``/version``, ``/registres/{nom}``, ``/comptes-apu``,
``/depenses-par-fonction``, ``/validation``. La baseline et les scénarios viendront avec les
lots 1.3 et suivants.
"""

from __future__ import annotations

import hashlib
import logging
from functools import cache
from importlib.metadata import version
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fr_budget.apu import comptes_apu, depenses_par_fonction, libelles_cofog, ratio_pib
from fr_budget.registres.verification import RACINE_DEPOT, Rapport, charger
from fr_budget.validation import comparaisons

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
        # Empreinte du code du moteur : change à chaque modification d'un calcul.
        "moteur": empreinte_dossier(RACINE_DEPOT / "moteur" / "src" / "fr_budget"),
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


def serie_comptes(sous_secteur: str, indicateur: str) -> dict[str, Any] | None:
    """Série annuelle d'un indicateur des comptes des APU ; ``None`` si elle n'existe pas.

    Chaque valeur porte aussi son ratio au PIB de la même année (``pourcent_pib``), calculé
    par ``fr_budget.apu.ratio_pib``, sauf pour le PIB lui-même.
    """
    c = comptes_apu()
    annees = c.annees(sous_secteur, indicateur)
    if not annees:
        return None
    pib = {a: c.valeur(a, "S1", "pib") for a in c.annees("S1", "pib")}
    valeurs: list[dict[str, Any]] = []
    for a in annees:
        valeur = c.valeur(a, sous_secteur, indicateur)
        point: dict[str, Any] = {"annee": a, "valeur": valeur}
        if indicateur != "pib" and a in pib:
            point["pourcent_pib"] = ratio_pib(valeur, pib[a])
        valeurs.append(point)
    return {
        "source": SOURCE_COMPTES_APU,
        "unite": UNITE,
        "sous_secteur": sous_secteur,
        "indicateur": indicateur,
        "valeurs": valeurs,
    }


def depenses_fonctions(annee: int, sous_secteur: str) -> dict[str, Any] | None:
    """Dépenses par fonction COFOG d'un sous-secteur pour une année ; ``None`` si absentes."""
    valeurs = [
        {"cofog": code, "libelle": libelles_cofog()[code], "valeur": v}
        for (a, s, code), v in sorted(depenses_par_fonction().items())
        if a == annee and s == sous_secteur
    ]
    if not valeurs:
        return None
    return {
        "source": SOURCE_COFOG,
        "unite": UNITE,
        "annee": annee,
        "sous_secteur": sous_secteur,
        "valeurs": valeurs,
    }


def registre(nom: str) -> list[dict[str, Any]] | None:
    """Contenu d'un registre ; ``None`` si le nom est inconnu."""
    return _registres()[nom] if nom in REGISTRES else None


def version_donnees() -> dict[str, str]:
    """Version du moteur et empreintes des registres et des données traitées."""
    return _version()


def resume_validation() -> list[dict[str, Any]]:
    """Valeur du modèle, référence et écart pour chaque référence de validation."""
    unites = {c["id"]: c["unite"] for c in _registres()["chiffrages"]}
    return [
        {
            "reference": c.reference,
            "modele": c.modele,
            "valeur_reference": c.valeur_reference,
            "ecart": c.ecart,
            "tolerance": c.tolerance,
            "dans_la_tolerance": c.dans_la_tolerance,
            "unite": unites[c.reference],
        }
        for c in comparaisons()
    ]


def creer_application() -> FastAPI:
    # Règle 5 : aucune requête (et donc aucun paramètre saisi) dans les journaux.
    logging.getLogger("uvicorn.access").disabled = True
    app = FastAPI(
        title="Simulateur du budget des administrations publiques",
        description="API sans état : aucune donnée saisie n'est stockée ni journalisée.",
        version=version("fr-budget-api"),
    )

    @app.get("/sante")
    def sante() -> dict[str, str]:
        return {"statut": "ok"}

    @app.get("/version")
    def route_version() -> dict[str, str]:
        """Version du moteur et empreintes des registres et des données traitées."""
        return version_donnees()

    @app.get("/registres/{nom}")
    def route_registre(nom: str) -> list[dict[str, Any]]:
        contenu = registre(nom)
        if contenu is None:
            raise HTTPException(status_code=404, detail="registre inconnu")
        return contenu

    @app.get("/comptes-apu")
    def route_comptes(sous_secteur: str, indicateur: str) -> dict[str, Any]:
        """Série annuelle d'un indicateur des comptes des APU pour un sous-secteur."""
        serie = serie_comptes(sous_secteur, indicateur)
        if serie is None:
            raise HTTPException(status_code=404, detail="série inconnue")
        return serie

    @app.get("/depenses-par-fonction")
    def route_fonctions(annee: int, sous_secteur: str) -> dict[str, Any]:
        """Dépenses par fonction COFOG d'un sous-secteur pour une année."""
        depenses = depenses_fonctions(annee, sous_secteur)
        if depenses is None:
            raise HTTPException(status_code=404, detail="année ou sous-secteur absent")
        return depenses

    @app.get("/validation")
    def route_validation() -> list[dict[str, Any]]:
        """Comparaisons du modèle aux chiffrages de référence, écarts compris."""
        return resume_validation()

    return app


application = creer_application()
