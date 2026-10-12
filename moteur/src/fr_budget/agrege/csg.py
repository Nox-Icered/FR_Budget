"""CSG : rendement d'un point de taux sur trois assiettes (lot 2.9).

Données (``registres/references/chiffrages.yaml``) : rapports à la Commission des comptes de la
sécurité sociale (CCSS) d'octobre 2026 (rendements 2024, 2025 et 2027, taux 2025 et 2027) et de
septembre 2018 (rendements et taux de 2017), fiche 1.3 « La CSG ».

Leviers (décisions du mainteneur du 12 octobre 2026 : options recommandées, signalées dans la
fiche) :

- revenus d'activité : taux de 9,2 % ;
- pensions de retraite au taux plein : taux de 8,3 % (les taux réduit et médian ne bougent
  pas, comme lors de la hausse de 2018) ;
- revenus du capital (patrimoine et placements) : taux de 9,2 % en 2025.

Rendement d'un point : rendement constaté de l'assiette divisé par son taux. Pour les
retraites, seule la part du rendement prélevée au taux plein compte ; elle est calculée avec
OpenFisca sur la distribution des pensions de l'EIR 2020 (DREES), pour une personne seule et un
couple de retraités (``fr_budget.agrege.indexation``).

Rendement brut : la CSG déductible réduit l'impôt sur le revenu, effet non compté (comme dans
les chiffrages de la CCSS).
"""

from __future__ import annotations

import warnings
from functools import cache

import numpy as np
from openfisca_core.simulation_builder import SimulationBuilder

from fr_budget.agrege.indexation import (
    ANNEE_DISTRIBUTION,
    COUPLE,
    FOYERS,
    distribution_pensions,
    facteur_pib,
    situation_retraites,
)
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage

ACTIVITE = "activite"
RETRAITES = "retraites"
CAPITAL = "capital"
ASSIETTES = (ACTIVITE, RETRAITES, CAPITAL)
ANNEE_REFERENCE = 2025
ANNEES_BORNES = (2024, 2027)
ANNEE_TAUX_2018 = 2017
MILLIONS_PAR_MILLIARD = 1000.0
POURCENT = 100.0
TOLERANCE_TAUX = 1e-4
CSG_RETRAITE = ("csg_deductible_retraite", "csg_imposable_retraite")


def rendement(assiette: str, annee: int) -> float:
    """Rendement de la CSG sur l'assiette, tous affectataires, en Md€ courants (CCSS).

    Retraites : tous taux confondus. Capital 2017 : patrimoine et placements.
    """
    if assiette == CAPITAL and annee == ANNEE_TAUX_2018:
        millions = chiffrage("csg_rendement_patrimoine_2017") + chiffrage(
            "csg_rendement_placement_2017"
        )
    else:
        millions = chiffrage(f"csg_rendement_{assiette}_{annee}")
    return millions / MILLIONS_PAR_MILLIARD


def taux(assiette: str, annee: int) -> float:
    """Taux de CSG de l'assiette, en % (taux plein pour les retraites ; pour le capital en 2027,
    taux plein après la LFSS 2026, le taux réduit restant à 9,2 %)."""
    return chiffrage(f"csg_taux_{assiette}_{annee}")


@cache
def part_taux_plein(annee: int, foyer: str) -> float:
    """Part de la CSG sur les pensions prélevée au taux plein, législation de ``annee``.

    Retraités de chaque tranche de l'EIR 2020 (pensions de 2020, sans réindexation), pondérés
    par le nombre de retraités de la tranche (et de personnes du foyer).
    """
    niveaux, parts = distribution_pensions()
    systeme = systeme_socio_fiscal()
    simulation = SimulationBuilder().build_from_entities(
        systeme, situation_retraites(niveaux, foyer, annee)
    )
    periode = str(annee)
    with warnings.catch_warnings():
        # Avertissements numpy neutralisés par OpenFisca lui-même (divisions par zéro).
        warnings.simplefilter("ignore", RuntimeWarning)
        brute = simulation.calculate_add("retraite_brute", periode)
        csg = -sum(simulation.calculate_add(v, periode) for v in CSG_RETRAITE)
    plein = systeme.parameters(
        periode
    ).prelevements_sociaux.contributions_sociales.csg.remplacement.pensions_retraite_invalidite.taux_plein
    personnes = 2 if foyer == COUPLE else 1
    poids = np.repeat(parts, personnes)
    au_plein = np.isclose(csg / brute, plein, atol=TOLERANCE_TAUX)
    return float(np.sum(poids * csg * au_plein) / np.sum(poids * csg))


def _part_centrale(annee: int) -> float:
    return float(np.mean([part_taux_plein(annee, f) for f in FOYERS]))


def rendement_taux_plein(annee: int) -> float:
    """Rendement de la CSG sur les retraites au taux plein, en Md€ (part calculée)."""
    return rendement(RETRAITES, annee) * _part_centrale(annee)


def _un_point(assiette: str, annee: int, part: float = 1.0) -> float:
    """Rendement d'un point sur l'assiette de ``annee``, en Md€ de ``annee``."""
    return rendement(assiette, annee) * part / taux(assiette, annee)


def hausse_mesuree(assiette: str, points: float, annee: int) -> float:
    """Rendement d'une hausse de ``points`` en ``annee``, en Md€ (validation).

    Assiette de l'année précédente, portée à ``annee`` par la croissance du PIB nominal.
    """
    precedente = annee - 1
    part = _part_centrale(precedente) if assiette == RETRAITES else 1.0
    croissance = facteur_pib(annee) / facteur_pib(precedente)
    return points * _un_point(assiette, precedente, part) * croissance


def rendement_un_point(assiette: str) -> Fourchette:
    """Rendement d'une hausse d'un point, en Md€ de 2025.

    Valeur centrale : rendements constatés de 2025. Bornes : rendements de 2024 (constatés) et
    de 2027 (prévus), rapportés au PIB de leur année puis au PIB de 2025, et, pour les
    retraites, part du taux plein d'une personne seule ou d'un couple, avec la législation de
    2020, année des pensions de l'EIR (seuils et pensions de la même année).
    """
    if assiette == RETRAITES:
        parts = [part_taux_plein(ANNEE_DISTRIBUTION, f) for f in FOYERS]
    else:
        parts = [1.0]
    central = _un_point(assiette, ANNEE_REFERENCE, float(np.mean(parts)))
    variantes = [
        _un_point(assiette, a, p) * facteur_pib(ANNEE_REFERENCE) / facteur_pib(a)
        for a in (ANNEE_REFERENCE, *ANNEES_BORNES)
        for p in parts
    ]
    return encadrer(central, variantes)


def valeur_point(assiette: str, annee: int) -> float:
    """Valeur centrale d'un point en ``annee``, en Md€ courants (validation) : rendement d'un
    point de 2025 tenu constant en part du PIB nominal."""
    return rendement_un_point(assiette).central * facteur_pib(annee) / facteur_pib(ANNEE_REFERENCE)
