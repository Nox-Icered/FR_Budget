"""Combinaison de mesures sans double compte : termes croisés entre leviers (V2).

Plusieurs mesures s'additionnent, sauf quand l'une change l'assiette de l'autre. Plan validé par
le responsable du projet le 6 novembre 2026 (option A, ``docs/fiches/interactions.md``) :

- **termes croisés chiffrés** : quand une mesure change l'assiette d'un prélèvement qu'une
  autre mesure modifie, le prélèvement supplémentaire sur l'assiette supplémentaire s'ajoute.
  Le terme est proportionnel au produit des deux réglages ; il est nul si l'un d'eux l'est.
  Aucune élasticité ni valeur nouvelle : seulement les assiettes et les taux déjà utilisés par
  les deux leviers ;
- **interactions non chiffrées** : signalées sur le site quand les deux mesures sont réglées ;
  la combinaison n'est pas refusée (``NON_CHIFFREES``).

Termes chiffrés, en Md€ de 2025 pour une unité de chaque levier :

- rémunérations publiques (point d'indice ou effectifs, 1 %) et CSG sur les revenus d'activité
  (1 point) : 1 % du coût brut de chaque versant (``remunerations.cout_brut_un_pourcent``)
  fois l'assiette de CSG ajoutée par euro de coût employeur, fois 1 point. L'assiette ajoutée
  est la CSG ajoutée (OpenFisca, fonctionnaire moyen de la DGAFP) divisée par le taux de CSG
  sur les revenus d'activité de 2025 (CCSS, ``csg.taux``). Valeur centrale : ensemble des
  fonctionnaires ; bornes : catégories A, B et C, comme le coût net du levier ;
- revalorisation des pensions et prestations (1 point) et taux plein de CSG sur les pensions de
  retraite (1 point) : 1 % des pensions du bloc « pensions » du levier d'indexation
  (DREES, ``indexation.montant``) fois la part de la masse des pensions prélevée au taux plein
  (EIR 2020 de la DREES et OpenFisca, comme ``csg.part_taux_plein``), fois 1 point. Valeur
  centrale : législation de 2025, moyenne d'une personne seule et d'un couple ; bornes :
  législations de 2020 et 2025, personne seule ou couple.

Effet d'activité (multiplicateur) : celui de la CSG, catégorie du prélèvement modifié.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from functools import cache

import numpy as np
from openfisca_core.simulation_builder import SimulationBuilder

from fr_budget.agrege import csg, indexation, remunerations
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal

PREFIXE = "interaction__"
SEPARATEUR = "__"
POURCENT = 100.0

POINT_INDICE = "remunerations_point_indice"
EFFECTIFS = "remunerations_effectifs"
CSG_ACTIVITE = "csg_activite"
CSG_RETRAITES = "csg_retraites"
CSG_CAPITAL = "csg_capital"
INDEXATION = "indexation_pensions_prestations"


def identifiant(a: str, b: str) -> str:
    """Identifiant interne du terme croisé de deux leviers (ordre des leviers sans effet)."""
    premier, second = sorted((a, b))
    return f"{PREFIXE}{premier}{SEPARATEUR}{second}"


CHIFFREES: dict[str, tuple[str, str]] = {
    identifiant(a, b): (a, b)
    for a, b in (
        (POINT_INDICE, CSG_ACTIVITE),
        (EFFECTIFS, CSG_ACTIVITE),
        (INDEXATION, CSG_RETRAITES),
    )
}
"""Termes croisés chiffrés : identifiant interne -> paire de leviers."""


def est_interaction(levier: str) -> bool:
    return levier in CHIFFREES


@dataclass(frozen=True)
class NonChiffree:
    """Interaction connue mais non chiffrée : toute mesure de ``leviers_a`` réglée avec toute
    mesure de ``leviers_b`` ; ``mecanisme`` : clé du texte affiché sur le site."""

    mecanisme: str
    leviers_a: tuple[str, ...]
    leviers_b: tuple[str, ...]
    manque: str
    """Donnée ou hypothèse qui manque pour chiffrer le terme."""


NON_CHIFFREES: tuple[NonChiffree, ...] = (
    NonChiffree(
        "accises_tva",
        ("accise_gazole", "accise_essences"),
        ("tva_taux_normal",),
        "part des volumes de carburant achetée sans TVA déductible (ménages)",
    ),
    NonChiffree(
        "csg_impot_revenu",
        (CSG_ACTIVITE, "csg_retraites", CSG_CAPITAL),
        (
            "ir_seuils_bareme",
            "ir_plafond_quotient_familial",
            "ir_bareme",
            "depenses_fiscales_impot_revenu",
        ),
        "revenu imposable par tranche du barème (la CSG déductible le réduit)",
    ),
    NonChiffree(
        "cotisations_impot_societes",
        ("cotisations_patronales_taux", "allegements_generaux", "chomage_contribution_patronale"),
        ("is_taux_normal", "is_surtaxe_grandes_entreprises"),
        "part des cotisations qui réduit le bénéfice imposable (incidence)",
    ),
    NonChiffree(
        "bareme_quotient_familial",
        ("ir_seuils_bareme", "ir_bareme"),
        ("ir_plafond_quotient_familial",),
        "foyers dont l'avantage du quotient familial est plafonné, par tranche",
    ),
    NonChiffree(
        "age_depart_pensions",
        ("retraites_age_depart", "retraites_age_legal"),
        (INDEXATION, CSG_RETRAITES, "chomage_duree_indemnisation", "chomage_revalorisation"),
        "effet de l'âge de départ séparé entre pensions, cotisations et chômage (COR)",
    ),
)


def non_chiffrees(leviers_regles: set[str]) -> list[str]:
    """Mécanismes des interactions non chiffrées entre les leviers réglés (non nuls)."""
    return [
        p.mecanisme
        for p in NON_CHIFFREES
        if leviers_regles & set(p.leviers_a) and leviers_regles & set(p.leviers_b)
    ]


def _assiette_csg_par_cout(versant: str, categorie: str, levier: str) -> float:
    """Assiette de CSG sur les revenus d'activité ajoutée par euro de coût employeur.

    Point d'indice : hausse de 1 % du traitement ; effectifs : agent entier (moyennes).
    """
    tib, primes = remunerations.traitement_et_primes(versant, categorie)
    base = remunerations.agent(versant, tib, primes)
    taux = csg.taux(csg.ACTIVITE, csg.ANNEE_REFERENCE) / POURCENT
    if levier == EFFECTIFS:
        return base.csg / base.cout / taux
    hausse = remunerations.agent(versant, tib * (1 + remunerations.HAUSSE_TEST), primes)
    return (hausse.csg - base.csg) / (hausse.cout - base.cout) / taux


def _remunerations_csg(levier: str) -> Fourchette:
    cle = remunerations.POINT if levier == POINT_INDICE else remunerations.EFFECTIFS
    central = 0.0
    bornes = [0.0, 0.0]
    for versant in remunerations.VERSANTS:
        brut = remunerations.cout_brut_un_pourcent(cle, versant) / POURCENT
        c = _assiette_csg_par_cout(versant, remunerations.ENSEMBLE, levier)
        autres = [_assiette_csg_par_cout(versant, k, levier) for k in remunerations.CATEGORIES]
        central += brut * c
        bornes[0] += brut * min([*autres, c])
        bornes[1] += brut * max([*autres, c])
    return encadrer(central, bornes)


@cache
def part_masse_taux_plein(annee: int, foyer: str) -> float:
    """Part de la masse des pensions de retraite prélevée au taux plein de CSG, législation de
    ``annee`` ; retraités de chaque tranche de l'EIR 2020 (DREES), pondérés par leur nombre."""
    niveaux, parts = indexation.distribution_pensions()
    systeme = systeme_socio_fiscal()
    simulation = SimulationBuilder().build_from_entities(
        systeme, indexation.situation_retraites(niveaux, foyer, annee)
    )
    periode = str(annee)
    with warnings.catch_warnings():
        # Avertissements numpy neutralisés par OpenFisca lui-même (divisions par zéro).
        warnings.simplefilter("ignore", RuntimeWarning)
        brute = simulation.calculate_add("retraite_brute", periode)
        prelevee = -sum(simulation.calculate_add(v, periode) for v in csg.CSG_RETRAITE)
    plein = systeme.parameters(
        periode
    ).prelevements_sociaux.contributions_sociales.csg.remplacement.pensions_retraite_invalidite.taux_plein
    personnes = 2 if foyer == indexation.COUPLE else 1
    poids = np.repeat(parts, personnes)
    au_plein = np.isclose(prelevee / brute, plein, atol=csg.TOLERANCE_TAUX)
    return float(np.sum(poids * brute * au_plein) / np.sum(poids * brute))


def _indexation_csg() -> Fourchette:
    un_point = indexation.montant(indexation.PENSIONS, indexation.ANNEE_REFERENCE) / POURCENT
    centrale = [part_masse_taux_plein(csg.ANNEE_REFERENCE, f) for f in indexation.FOYERS]
    autres = [
        part_masse_taux_plein(a, f)
        for a in (indexation.ANNEE_DISTRIBUTION, csg.ANNEE_REFERENCE)
        for f in indexation.FOYERS
    ]
    k = un_point / POURCENT
    return encadrer(k * float(np.mean(centrale)), [k * p for p in autres])


@cache
def rendement_unitaire(interaction: str) -> Fourchette:
    """Terme croisé pour une unité de chaque levier, en Md€ de 2025 (positif : recettes en
    plus ou dépenses en moins)."""
    if interaction not in CHIFFREES:
        msg = f"interaction inconnue : {interaction}"
        raise ValueError(msg)
    a, b = CHIFFREES[interaction]
    autre = a if b in (CSG_ACTIVITE, CSG_RETRAITES) else b
    if autre in (POINT_INDICE, EFFECTIFS):
        return _remunerations_csg(autre)
    return _indexation_csg()


def part_premiere_annee(interaction: str) -> float:
    """Part de l'effet en année pleine acquise l'année d'entrée : pensions revalorisées au mois
    de leur bloc (indexation) ; 1 pour les autres."""
    if INDEXATION in CHIFFREES[interaction]:
        return indexation.part_premiere_annee(indexation.PENSIONS)
    return 1.0
