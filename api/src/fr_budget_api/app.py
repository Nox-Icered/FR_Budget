"""API FastAPI sans état (lot 1.4 du plan).

Règles (CLAUDE.md) : l'API ne stocke rien et ne journalise aucune donnée saisie par
l'utilisateur ; chaque réponse chiffrée indique sa source (identifiant du registre) et son
unité. Le journal d'accès d'uvicorn (qui contiendrait les paramètres des requêtes) est
désactivé par ``creer_application`` elle-même ; lancer avec ``python -m fr_budget_api.serveur``.

Points d'entrée : ``/sante``, ``/version``, ``/registres/{nom}``, ``/comptes-apu``,
``/depenses-par-fonction``, ``/validation``, ``/baseline``, ``/depenses-fiscales``,
``/credits-missions``,
``POST /scenario``.
"""

from __future__ import annotations

import hashlib
import logging
from functools import cache
from importlib.metadata import version
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fr_budget import baseline as module_baseline
from fr_budget import scenario as module_scenario
from fr_budget.agrege import credits_missions as module_credits_missions
from fr_budget.agrege import depenses_fiscales as module_depenses_fiscales
from fr_budget.apu import comptes_apu, depenses_par_fonction, libelles_cofog, ratio_pib
from fr_budget.registres.verification import RACINE_DEPOT, Rapport, charger
from fr_budget.validation import comparaisons
from pydantic import BaseModel, Field

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


def _fourchette(f: Any) -> dict[str, float]:
    return {"bas": f.bas, "central": f.central, "haut": f.haut}


@cache
def serie_baseline() -> dict[str, Any]:
    """Baseline 2025-2046 en fourchette (``fr_budget.baseline``), avec sources et hypothèses.

    Le statut reprend celui de la fiche ``docs/fiches/baseline.md`` : non publié tant que la
    porte de la phase 1 (relecture par deux relecteurs) n'est pas franchie.
    """
    raccord = module_baseline.ANNEE_RACCORD
    return {
        "sources": list(module_baseline.SOURCES),
        "unite": "% du PIB",
        "statut": "non_publie",
        "annee_raccord": raccord,
        "hypotheses": list(module_baseline.HYPOTHESES),
        "valeurs": [
            {
                "annee": ligne.annee,
                "segment": "resf" if ligne.annee <= raccord else "projection",
                "dette": _fourchette(ligne.dette),
                "solde_primaire": _fourchette(ligne.solde_primaire),
            }
            for ligne in module_baseline.baseline()
        ],
    }


class MesureEntree(BaseModel):
    levier: str
    valeur: float
    annee: int


class ScenarioEntree(BaseModel):
    mesures: list[MesureEntree] = Field(default_factory=list)


def _statut_levier(levier: str) -> str:
    registre_id = module_scenario.levier_registre(levier)
    statuts = {lv["id"]: lv["statut"] for lv in _registres()["leviers"]}
    return statuts[registre_id] if registre_id else "inconnu"


def calcul_scenario(entree: ScenarioEntree) -> dict[str, Any] | None:
    """Scénario en fourchette (``fr_budget.scenario``) ; ``None`` si une mesure est invalide.

    La réponse reprend les mesures, le statut de chaque levier et la version du modèle et des
    données (un scénario partagé doit reproduire le même résultat). Rien n'est enregistré.
    """
    mesures = [module_scenario.Mesure(m.levier, m.valeur, m.annee) for m in entree.mesures]
    # Les leviers génériques ne servent qu'au calcul du site : par l'API, une dépense fiscale
    # est désignée par son numéro et une mission par son identifiant, ce qui permet de
    # contrôler le double compte.
    generiques = (
        module_scenario.LEVIER_DEPENSE_FISCALE_UNITE,
        module_scenario.LEVIER_CREDITS_UNITE,
    )
    if any(m.levier in generiques for m in mesures):
        return None
    try:
        lignes = module_scenario.scenario(mesures)
        sources, hypotheses = module_scenario.provenance(m.levier for m in mesures)
    except ValueError:
        return None
    return {
        "unite": "% du PIB",
        "sources": sources,
        "hypotheses": hypotheses,
        "version": version_donnees(),
        "mesures": [m.model_dump() for m in entree.mesures],
        "statuts": {m.levier: _statut_levier(m.levier) for m in entree.mesures},
        "valeurs": [
            {
                "annee": ligne.annee,
                "dette": _fourchette(ligne.dette),
                "solde_primaire": _fourchette(ligne.solde_primaire),
                "ecart_dette": _fourchette(ligne.ecart_dette),
                "ecart_solde_primaire": _fourchette(ligne.ecart_solde_primaire),
            }
            for ligne in lignes
        ],
    }


DECIMALES_EXPORT = 9


def _arrondir(series: list[list[float]]) -> list[list[float]]:
    """Arrondi des réponses exportées (fichier plus léger ; écart inférieur à 1e-9 point)."""
    return [[round(v, DECIMALES_EXPORT) for v in s] for s in series]


def reponses_unitaires() -> dict[str, Any]:
    """Réponses linéaires de chaque levier, pour chaque année d'entrée (site statique)."""
    leviers: dict[str, Any] = {}
    for levier in module_scenario.LEVIERS_REGISTRE:
        basse, haute = module_scenario.bornes_levier(levier)
        reponses = {}
        for annee in range(module_scenario.ANNEE_PREMIERE_MESURE, module_baseline.ANNEE_FIN + 1):
            r = module_scenario.reponse_lineaire(levier, annee)
            reponses[str(annee)] = {
                "unite_dette": _arrondir(r.unite_dette),
                "unite_solde": _arrondir(r.unite_solde),
            }
        effet = module_scenario.effet_solde(
            module_scenario.Mesure(levier, 1.0, module_scenario.ANNEE_PREMIERE_MESURE)
        )
        sources, hypotheses = module_scenario.provenance([levier])
        leviers[levier] = {
            "sources": sources,
            "hypotheses": hypotheses,
            "statut": _statut_levier(levier),
            "rendement_unitaire": module_scenario.rendement_unitaire(levier).central,
            "effet_unitaire": effet.central,
            "taux_reference": module_scenario.taux_reference(levier),
            # Dotations : effet d'un pour cent sur le solde du seul État (affiché à part).
            **(
                {"effet_etat_unitaire": module_scenario.effet_etat_unitaire(levier)}
                if levier in module_scenario.LEVIERS_DOTATIONS
                else {}
            ),
            "bornes": [basse, haute],
            "reponses": reponses,
        }
    r = module_scenario.reponse_lineaire(
        next(iter(module_scenario.LEVIERS_REGISTRE)), module_scenario.ANNEE_PREMIERE_MESURE
    )
    return {
        "unite": "% du PIB",
        "annee_reference": module_scenario.ANNEE_REFERENCE,
        "annees": r.annees,
        "base_dette": r.base_dette,
        "base_solde": r.base_solde,
        "indices_effet": r.indices_effet,
        "leviers": leviers,
    }


def catalogue_depenses_fiscales() -> dict[str, Any]:
    """Dépenses fiscales proposées au levier, avec leur coût et le rendement d'un pour cent.

    ``rendement_pourcent`` : Md€ de l'année de référence, valeur du levier générique
    ``depense_fiscale`` pour une réduction de 1 % de la dépense (le site multiplie par x %).
    """
    df = module_depenses_fiscales
    return {
        "source": "plf2026_voies_et_moyens_tome2",
        "annee_cout": df.ANNEE_COUT_LEVIER,
        "unite_cout": "Md€",
        "impots": {
            i: {
                "levier": module_scenario.levier_depenses_fiscales_impot(i),
                "cout": df.cout_impot_levier(i) / module_scenario.MILLIONS_PAR_MILLIARD,
            }
            for i in df.IMPOTS_LEVIER
        },
        # Ordre des parties du tome II (l'export trie les clés des objets).
        "ordre_impots": list(df.IMPOTS_LEVIER),
        "impots_exclus": list(df.IMPOTS_EXCLUS),
        "depenses": [
            {
                "code": d.code,
                "impot": d.impot,
                "libelle": d.libelle,
                "cout": d.cout / module_scenario.MILLIONS_PAR_MILLIARD,
                "annee_chiffrage": d.annee_chiffrage,
                "fiabilite": d.fiabilite,
                "rendement_pourcent": module_scenario.rendement_unitaire(
                    module_scenario.levier_depense_fiscale(d.code)
                ).central,
            }
            for d in df.catalogue()
        ],
    }


def catalogue_credits_missions() -> dict[str, Any]:
    """Missions du levier, avec leurs crédits 2026 et l'effet d'une hausse d'un pour cent.

    ``rendement_pourcent`` : Md€ de l'année de référence (négatif : une hausse dégrade le
    solde) ; le site traduit x % d'une mission en une valeur du levier générique
    ``credits_missions`` égale à -x * rendement_pourcent.
    """
    return {
        "source": "db_budget_vert_plf2026",
        "annee_credits": module_credits_missions.ANNEE_CREDITS,
        "unite_credits": "Md€",
        "bornes": [-module_scenario.BORNE_CREDITS, module_scenario.BORNE_CREDITS],
        "missions": [
            {
                "identifiant": m.identifiant,
                "libelle": m.libelle,
                "credits": m.credits / module_scenario.EUROS_PAR_MILLIARD,
                "rendement_pourcent": module_scenario.rendement_unitaire(
                    module_scenario.levier_credits_mission(m.identifiant)
                ).central,
            }
            for m in module_credits_missions.missions()
        ],
    }


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

    @app.get("/baseline")
    def route_baseline() -> dict[str, Any]:
        """Dette et solde primaire de 2025 à 2046, sans réforme, en fourchette."""
        return serie_baseline()

    @app.get("/depenses-fiscales")
    def route_depenses_fiscales() -> dict[str, Any]:
        """Dépenses fiscales proposées au levier : coût prévu pour 2026 et rendement d'1 %."""
        return catalogue_depenses_fiscales()

    @app.get("/credits-missions")
    def route_credits_missions() -> dict[str, Any]:
        """Missions du levier : crédits demandés au PLF 2026 et effet d'une hausse d'1 %."""
        return catalogue_credits_missions()

    @app.post("/scenario")
    def route_scenario(entree: ScenarioEntree) -> dict[str, Any]:
        """Effet de mesures sur le solde primaire et la dette, 2025-2046, en fourchette."""
        resultat = calcul_scenario(entree)
        if resultat is None:
            raise HTTPException(status_code=422, detail="mesure invalide")
        return resultat

    return app


application = creer_application()
