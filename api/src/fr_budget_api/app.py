"""API FastAPI sans état (lot 1.4 du plan).

Règles (CLAUDE.md) : l'API ne stocke rien et ne journalise aucune donnée saisie par
l'utilisateur ; chaque réponse chiffrée indique sa source (identifiant du registre) et son
unité. Le journal d'accès d'uvicorn (qui contiendrait les paramètres des requêtes) est
désactivé par ``creer_application`` elle-même ; lancer avec ``python -m fr_budget_api.serveur``.

Points d'entrée : ``/sante``, ``/version``, ``/journal``, ``/menages-types``,
``/registres/{nom}``, ``/comptes-apu``, ``/depenses-par-fonction``, ``/validation``,
``/baseline``, ``/depenses-fiscales``, ``/credits-missions``, ``POST /scenario``.
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
from functools import cache
from importlib.metadata import version
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fr_budget import baseline as module_baseline
from fr_budget import croissance as module_croissance
from fr_budget import retraites as module_retraites
from fr_budget import scenario as module_scenario
from fr_budget.agrege import credits_missions as module_credits_missions
from fr_budget.agrege import depenses_fiscales as module_depenses_fiscales
from fr_budget.apu import comptes_apu, depenses_par_fonction, libelles_cofog, ratio_pib
from fr_budget.menages import leviers as module_leviers_menages
from fr_budget.menages import personnalise as module_personnalise
from fr_budget.menages import types as module_menages
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
    "relectures": "relectures",
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


FICHES = RACINE_DEPOT / "docs" / "fiches"
TITRE_FICHE = re.compile(r"^# Fiche : (.+)$", re.MULTILINE)
SECTION_JOURNAL = re.compile(r"^## (?:\d+\. )?Journal$", re.MULTILINE)
LIGNE_JOURNAL = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \| (.+?) \| (.+?) \|$")
LIEN_MARKDOWN = re.compile(r"\[([^\]]+)\]\([^)]+\)")


def _texte_brut(texte: str) -> str:
    """Texte d'une cellule de tableau Markdown sans liens, code ni gras."""
    return LIEN_MARKDOWN.sub(r"\1", texte).replace("`", "").replace("**", "")


def journal() -> list[dict[str, str]]:
    """Journal des modifications : lignes des sections « Journal » de toutes les fiches, des
    plus récentes aux plus anciennes (la fiche reste la seule source du journal)."""
    lignes = []
    for fichier in sorted(FICHES.glob("*.md")):
        if fichier.name.startswith("_"):
            continue
        contenu = fichier.read_text(encoding="utf-8")
        titre = TITRE_FICHE.search(contenu)
        section = SECTION_JOURNAL.search(contenu)
        if titre is None or section is None:
            continue
        for ligne in contenu[section.end() :].splitlines():
            if ligne.startswith("## "):
                break
            m = LIGNE_JOURNAL.match(ligne.strip())
            if m:
                lignes.append(
                    {
                        "date": m.group(1),
                        "fiche": fichier.stem,
                        "titre": titre.group(1),
                        "changement": _texte_brut(m.group(2)),
                        "tests": _texte_brut(m.group(3)),
                    }
                )
    # Tri stable : à date égale, l'ordre des fiches puis celui des lignes est conservé.
    return sorted(lignes, key=lambda x: x["date"], reverse=True)


SOURCES_MENAGES = [
    "insee_premiere_2079",
    "openfisca_france_176_1_2",
    "modele_social_11_1_0",
    "impots_gouv_simulateur_ir_2026",
    "service_public_f2918",
    "drees_retraites_2025_fiche05",
    "dss_instruction_2023_189",
    "dss_instruction_2024_176",
    "service_public_f2971",
    "insee_premiere_2060",
    "decret_2024_688",
    "decret_2025_708",
    "urssaf_reforme_assiette_independants",
    "urssaf_taux_ac_plnr",
]


def _lignes_cascade(c: module_menages.CascadeMenage) -> dict[str, Any]:
    return {
        "cout_employeur": round(c.cout_employeur, 2),
        "salaire_brut": round(c.salaire_brut, 2),
        "net_avant_impot": round(c.net_avant_impot, 2),
        "pension_brute": round(c.pension_brute, 2),
        "pension_nette": round(c.pension_nette, 2),
        "revenu_independant_brut": round(c.revenu_independant_brut, 2),
        "cotisations_independant": round(c.cotisations_independant, 2),
        "csg_crds_independant": round(c.csg_crds_independant, 2),
        "revenu_independant_net": round(c.revenu_independant_net, 2),
        "impot_revenu": round(c.impot_revenu, 2),
        "prestations": {k: round(v, 2) for k, v in c.prestations.items()},
        "net_apres_impot": round(c.net_apres_impot, 2),
    }


class AdulteSaisiEntree(BaseModel):
    statut: Literal["salarie", "retraite", "independant"]
    montant_mensuel: float = Field(ge=0, le=module_personnalise.MONTANT_MENSUEL_MAX)
    """Salaire brut, pension brute ou résultat fiscal, en euros par mois."""
    annee_naissance: int
    cadre: bool = False


class MenageSaisiEntree(BaseModel):
    adultes: list[AdulteSaisiEntree] = Field(
        min_length=1, max_length=module_personnalise.ADULTES_MAX
    )
    annees_naissance_enfants: list[int] = Field(
        default_factory=list, max_length=module_personnalise.ENFANTS_MAX
    )


def mon_menage(entree: MenageSaisiEntree) -> dict[str, Any] | None:
    """Cascade du ménage saisi ; ``None`` si la saisie est hors des bornes du moteur.

    Règle 5 : rien n'est gardé ni journalisé (le moteur ne met rien en cache).
    """
    saisi = module_personnalise.MenageSaisi(
        tuple(
            module_personnalise.AdulteSaisi(
                a.statut, a.montant_mensuel, a.annee_naissance, cadre=a.cadre
            )
            for a in entree.adultes
        ),
        tuple(entree.annees_naissance_enfants),
    )
    try:
        cascade = module_personnalise.calculer(saisi)
    except module_personnalise.SaisieInvalideError:
        return None
    return {
        "unite": "euros par an",
        "annee_revenus": module_menages.ANNEE,
        "sources": SOURCES_MENAGES,
        **_lignes_cascade(cascade),
    }


def menages_types() -> dict[str, Any]:
    """Cascade annuelle de chaque ménage type (revenus de l'année des ménages types), en euros
    par an, avec ses sources et hypothèses.

    Profils publics de la spécification : aucune donnée saisie par un utilisateur.
    """
    resultat = []
    for identifiant, profil in module_menages.PROFILS.items():
        c = module_menages.cascade_annuelle(identifiant)
        resultat.append(
            {
                "id": identifiant,
                "libelle": profil.libelle,
                "annee": module_menages.ANNEE,
                **_lignes_cascade(c),
            }
        )
    return {
        "unite": "euros par an",
        "annee_revenus": module_menages.ANNEE,
        "sources": SOURCES_MENAGES,
        "hypotheses": [
            module_menages.HYPOTHESE_EVOLUTION,
            module_menages.HYPOTHESE_PENSION,
            module_menages.HYPOTHESE_INDEPENDANT,
        ],
        "menages": resultat,
        "saisie": bornes_saisie(),
    }


def _lignes_ou_rien(c: module_menages.CascadeMenage | None) -> dict[str, Any] | None:
    return None if c is None else _lignes_cascade(c)


def _description_leviers_menages() -> dict[str, Any]:
    leviers = module_leviers_menages.LEVIERS
    return {
        "unite": "euros par an",
        "annee_revenus": module_menages.ANNEE,
        "sources": SOURCES_MENAGES,
        "leviers": [
            {"id": i, "unite": d.unite, "sources": list(d.sources)} for i, d in leviers.items()
        ],
        "sans_effet": module_leviers_menages.SANS_EFFET,
        "leviers_incidence": list(module_leviers_menages.LEVIERS_INCIDENCE),
        "incidence_par_defaut": module_leviers_menages.COMPTABLE,
    }


def effets_leviers_menages(processus: int | None = None) -> dict[str, Any]:
    """Cascade de chaque ménage type après une hausse et une baisse d'une unité de chaque
    levier qui change directement sa législation (``fr_budget.menages.leviers``) ; ``null``
    quand l'effet n'est pas chiffré."""
    effets = module_leviers_menages.effets_unitaires(processus)

    def lecture(incidence: str) -> dict[str, Any]:
        return {
            levier: {
                ("hausse" if valeur > 0 else "baisse"): {
                    i: _lignes_ou_rien(c) for i, c in cascades.items()
                }
                for valeur, cascades in par_incidence[incidence].items()
            }
            for levier, par_incidence in effets.items()
            if incidence in par_incidence
        }

    return {
        **_description_leviers_menages(),
        "effets": lecture(module_leviers_menages.COMPTABLE),
        # Cotisations patronales : même mesure, salaire brut ajusté pour garder le coût employeur.
        "effets_salaire": lecture(module_leviers_menages.SALAIRE),
    }


def effet_levier_menages(
    levier: str, valeur: float, incidence: str = module_leviers_menages.COMPTABLE
) -> dict[str, Any]:
    """Cascade de chaque ménage type sous ``valeur`` (unité du levier), dans la lecture
    ``incidence`` des cotisations patronales."""
    return {
        **_description_leviers_menages(),
        "levier": levier,
        "valeur": valeur,
        "incidence": incidence,
        "menages": {
            i: _lignes_ou_rien(
                module_leviers_menages.cascade_reformee(
                    i, levier, valeur, module_menages.ANNEE, incidence
                )
            )
            for i in module_menages.PROFILS
        },
    }


def bornes_saisie() -> dict[str, Any]:
    """Bornes de la saisie d'un ménage (``fr_budget.menages.personnalise``), pour le formulaire."""
    p = module_personnalise
    return {
        "annee": module_menages.ANNEE,
        "adultes_max": p.ADULTES_MAX,
        "enfants_max": p.ENFANTS_MAX,
        "montant_mensuel_max": p.MONTANT_MENSUEL_MAX,
        "annee_naissance_adulte_min": module_menages.ANNEE - p.AGE_MAX,
        "annee_naissance_adulte_max": module_menages.ANNEE - p.AGE_MIN_ADULTE,
        "annee_naissance_enfant_min": module_menages.ANNEE - p.AGE_MAX_ENFANT,
        "annee_naissance_enfant_max": module_menages.ANNEE,
    }


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
    croissance: bool = False
    """Effet de croissance (multiplicateur), désactivé par défaut (``fr_budget.croissance``)."""


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
        lignes = module_scenario.scenario(mesures, croissance=entree.croissance)
        sources, hypotheses = module_scenario.provenance(m.levier for m in mesures)
        if entree.croissance:
            s_cr, h_cr = module_croissance.provenance(
                module_scenario.categorie_croissance(m.levier) for m in mesures
            )
            sources += [x for x in s_cr if x not in sources]
            hypotheses += [x for x in h_cr if x not in hypotheses]
    except ValueError:
        return None
    return {
        "unite": "% du PIB",
        "sources": sources,
        "hypotheses": hypotheses,
        "version": version_donnees(),
        "mesures": [m.model_dump() for m in entree.mesures],
        "croissance": entree.croissance,
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
                "croissance_dette": _arrondir(r.croissance_dette),
                "croissance_solde": _arrondir(r.croissance_solde),
            }
        effet = module_scenario.effet_solde(
            module_scenario.Mesure(levier, 1.0, module_scenario.ANNEE_PREMIERE_MESURE)
        )
        sources, hypotheses = module_scenario.provenance([levier])
        categorie = module_scenario.categorie_croissance(levier)
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
            # Rémunérations et indexation : effet brut d'une unité, avant les retours aux APU.
            **(
                {"effet_brut_unitaire": module_scenario.effet_brut_unitaire(levier)}
                if levier in module_scenario.LEVIERS_EFFET_BRUT
                else {}
            ),
            **(
                {
                    "effet_plein": module_scenario.effet_plein_retraites(),
                    "duree_montee": module_retraites.duree_montee_en_charge(),
                }
                if levier == module_scenario.LEVIER_RETRAITES_AGE
                else {}
            ),
            "bornes": [basse, haute],
            "multiplicateur": _fourchette(module_croissance.multiplicateur(categorie)),
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
        "croissance": {
            **dict(
                zip(
                    ("sources", "hypotheses"),
                    module_croissance.provenance(module_croissance.CATEGORIES),
                    strict=True,
                )
            ),
            "persistance": module_croissance.persistance(),
            "effet_solde": module_croissance.effet_sur_le_solde(),
        },
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
    # Le site statique appelle POST /mon-menage depuis son propre domaine : origines permises
    # lues dans FR_BUDGET_ORIGINES (séparées par des virgules), aucune par défaut.
    origines = [o for o in os.environ.get("FR_BUDGET_ORIGINES", "").split(",") if o]
    if origines:
        app.add_middleware(
            CORSMiddleware, allow_origins=origines, allow_methods=["POST"], allow_headers=["*"]
        )

    @app.get("/sante")
    def sante() -> dict[str, str]:
        return {"statut": "ok"}

    @app.get("/menages-types")
    def lire_menages_types() -> dict[str, Any]:
        """Cascade annuelle des ménages types (avant réforme)."""
        return menages_types()

    @app.get("/menages-types/effet")
    def route_effet_levier_menages(
        levier: str, valeur: float, incidence: Literal["comptable", "salaire"] = "comptable"
    ) -> dict[str, Any]:
        """Cascade des ménages types sous un levier (unité du simulateur), dans ses bornes ;
        ``incidence`` : lecture des cotisations patronales (comptable par défaut)."""
        if levier not in module_leviers_menages.LEVIERS:
            raise HTTPException(status_code=404, detail="levier sans effet direct sur les ménages")
        basse, haute = module_scenario.bornes_levier(levier)
        if not basse <= valeur <= haute:
            raise HTTPException(status_code=422, detail="valeur hors des bornes du levier")
        if (
            incidence == module_leviers_menages.SALAIRE
            and levier not in module_leviers_menages.LEVIERS_INCIDENCE
        ):
            raise HTTPException(
                status_code=422, detail="lecture répercutée sans objet pour ce levier"
            )
        return effet_levier_menages(levier, valeur, incidence)

    @app.post("/mon-menage")
    def route_mon_menage(entree: MenageSaisiEntree) -> dict[str, Any]:
        """Cascade d'un ménage saisi par l'utilisateur, sans stockage ni journal."""
        resultat = mon_menage(entree)
        if resultat is None:
            raise HTTPException(status_code=422, detail="saisie hors des bornes acceptées")
        return resultat

    @app.get("/journal")
    def lire_journal() -> list[dict[str, str]]:
        """Journal des modifications du modèle et des données."""
        return journal()

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
