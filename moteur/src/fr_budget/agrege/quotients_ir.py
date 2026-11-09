"""Impôt sur le revenu, structure, troisième étape : effet du quotient familial et du quotient
conjugal (plan validé le 9 novembre 2026, deux leviers ; ``docs/fiches/quotients_ir.md``).

Deux leviers agrégés, en % de l'effet supprimé (0 : législation actuelle ; 100 : suppression) :

- **Quotient familial** (``ir_quotient_familial_effet``) : parts et autres dispositifs liés aux
  personnes à charge. Effet de 16,6 Md€ en 2017 (Insee, André et Sireyjol, 2021 : impôt
  « conjugal » sans les dispositifs familiaux moins impôt réel), et de 19,0 Md€ en 2018 (Insee
  Analyses n° 53) ; recoupé par le moteur du barème (``recoupement_bareme_qf``).
- **Quotient conjugal** (``ir_quotient_conjugal_effet``, imposition individuelle des couples
  mariés ou pacsés) : 11,1 Md€ en 2017 (même source : impôt individuel moins impôt conjugal),
  10,8 Md€ en 2018 (Insee Analyses n° 53) ; source indépendante : 7,2 Md€ en 2016 pour une
  individualisation où les parents répartissent au mieux les parts des enfants (Allègre,
  Périvier et Pucci, OFCE).

Méthode de l'Insee séquentielle : le quotient conjugal est mesuré sans les dispositifs
familiaux, le quotient familial après le quotient conjugal. Les deux leviers réglés à 100 %
redonnent l'écart total (27,7 Md€ en 2017) ; le quotient conjugal seul, dispositifs familiaux
maintenus, n'est pas chiffré par la source (limite de la fiche).

Montants portés en euros de 2025 par le PIB nominal (comme le plafond du quotient familial).
Effet proportionnel au pourcentage : une réduction partielle n'a pas de chiffrage officiel.
"""

from __future__ import annotations

from fr_budget.agrege import bareme_ir
from fr_budget.agrege.indexation import facteur_pib
from fr_budget.agrege.quotient_familial import plafond_general
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage

LEVIER_QF = "ir_quotient_familial_effet"
LEVIER_QC = "ir_quotient_conjugal_effet"
LEVIERS = (LEVIER_QF, LEVIER_QC)
ANNEE_REFERENCE = 2025
ANNEE_INSEE = 2017
ANNEE_INSEE_ANALYSES = 2018
ANNEE_OFCE = 2016
BORNE = 100.0
"""Curseur de 0 à 100 % de l'effet supprimé."""
POURCENT = 100.0
DEMI_PARTS_PAR_PART = 2.0
ADULTES_COUPLE, ADULTES_SEUL = 2.0, 1.0


def vers_2025(montant: float, annee: int) -> float:
    """Montant de ``annee`` porté en euros de 2025 par le PIB nominal."""
    return montant * facteur_pib(ANNEE_REFERENCE) / facteur_pib(annee)


def effet_qf_2017() -> float:
    """Baisse d'impôt due aux dispositifs familiaux en 2017, en Md€ (Insee, tableau 2)."""
    return chiffrage("ir_insee_impot_conjugal_2017") - chiffrage("ir_insee_impot_reel_2017")


def effet_qc_2017() -> float:
    """Baisse d'impôt due aux dispositifs conjugaux en 2017, en Md€ (Insee, tableau 2)."""
    return chiffrage("ir_insee_impot_individuel_2017") - chiffrage("ir_insee_impot_conjugal_2017")


def rendement_point_qf() -> Fourchette:
    """Rendement de la suppression de 1 % de l'effet du quotient familial, en Md€ de 2025.
    Central : Insee 2017 ; autre borne : Insee 2018."""
    central = vers_2025(effet_qf_2017(), ANNEE_INSEE) / POURCENT
    autre = vers_2025(chiffrage("ir_insee_familialisation_2018"), ANNEE_INSEE_ANALYSES) / POURCENT
    return encadrer(central, [autre])


def rendement_point_qc() -> Fourchette:
    """Rendement de la suppression de 1 % de l'effet du quotient conjugal, en Md€ de 2025.
    Central : Insee 2017 ; autres bornes : Insee 2018 et OFCE 2016 (individualisation avec
    répartition des parts des enfants)."""
    central = vers_2025(effet_qc_2017(), ANNEE_INSEE) / POURCENT
    autres = [
        vers_2025(chiffrage("ir_insee_conjugalisation_2018"), ANNEE_INSEE_ANALYSES),
        vers_2025(chiffrage("ir_ofce_individualisation_optimisation_2016"), ANNEE_OFCE),
    ]
    return encadrer(central, [a / POURCENT for a in autres])


def suppression(levier: str, annee: int) -> float:
    """Rendement de la suppression complète, valeur centrale, en Md€ de ``annee`` (validation)."""
    point = rendement_point_qf() if levier == LEVIER_QF else rendement_point_qc()
    return BORNE * point.central * facteur_pib(annee) / facteur_pib(ANNEE_REFERENCE)


def _net(bareme: bareme_ir.Bareme, brut: float, rfr: float, parts: float, couple: bool) -> float:
    """Impôt après décote et réduction sous condition de revenus (mêmes étapes que le moteur du
    barème)."""
    impot = brut
    if bareme.decote is not None:
        impot -= bareme.decote.montant(impot, couple)
    if bareme.reduction is not None:
        impot -= bareme.reduction.montant(impot, rfr, parts, couple)
    return impot


def _ecart_foyer(
    bareme: bareme_ir.Bareme, quotient: float, enfants: float, couple: bool, plafond: float
) -> float:
    """Hausse d'impôt d'un foyer privé des parts au-delà des adultes, en euros : impôt sur les
    seules parts des adultes moins impôt réel (avantage plafonné à ``plafond`` par demi-part)."""
    adultes = ADULTES_COUPLE if couple else ADULTES_SEUL
    parts = adultes + enfants
    rfr = quotient * parts
    sans = adultes * bareme_ir.impot_par_part(bareme, rfr / adultes)
    avec = parts * bareme_ir.impot_par_part(bareme, quotient)
    reel = max(avec, sans - plafond * DEMI_PARTS_PAR_PART * enfants)
    return _net(bareme, sans, rfr, adultes, couple) - _net(bareme, reel, rfr, parts, couple)


def recoupement_bareme_qf(annee: int = bareme_ir.ANNEE_CALAGE) -> float:
    """Suppression des parts au-delà des adultes recalculée par le moteur du barème, en Md€ de
    ``annee`` (revenus 2024 par défaut). Hypothèses : les parts au-delà de un (personne seule) ou
    deux (couple) sont toutes liées aux personnes à charge, en même nombre pour les couples et
    les personnes seules d'un segment ; plafond général pour chaque demi-part ; seuls le barème,
    la décote et la réduction sont recalculés (pas les autres dispositifs familiaux)."""
    bareme = bareme_ir.bareme_openfisca(annee)
    plafond = plafond_general(annee)
    k = bareme_ir.calage()
    n = bareme_ir.nombre_foyers(annee)
    total = 0.0
    for s in bareme_ir.segments(annee):
        c = bareme_ir.part_couples(s)
        enfants = max(0.0, s.parts - (ADULTES_SEUL + c))
        moyen = sum(
            c * _ecart_foyer(bareme, q, enfants, True, plafond)
            + (1 - c) * _ecart_foyer(bareme, q, enfants, False, plafond)
            for q in s.quotients
        ) / len(s.quotients)
        total += n * s.foyers * k[s.nom] * moyen
    return total / bareme_ir.EUROS_PAR_MILLIARD
