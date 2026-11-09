"""Assurance maladie, première étape : trois leviers agrégés, calés sur les chiffrages officiels.

Plan validé par le responsable du projet le 6 novembre 2026 (leviers 1, 2 et 3 ; franchises :
option (i) ; ONDAM : bornes tirées de l'exécution), ``docs/fiches/assurance_maladie.md``. Tous
en « bêta, non validé ».

- **Taux de progression de l'ONDAM** (``ondam_progression``, en points ; positif : plus de
  dépenses) : un point vaut 1 % de l'ONDAM 2025 voté en LFSS pour 2025 (annexe 5 du PLFSS pour
  2026). Bornes de l'effet : part des économies effectivement réalisées
  (``realisation_economies``, hypothèse ``ondam_realisation_economies``). Bornes du curseur :
  les mesures d'économies de la construction de 2026 (7,1 Md€) rapportées à l'ONDAM 2026.
- **Franchises et participations forfaitaires** (``franchises_participations``, en % des
  montants unitaires et des plafonds journaliers et annuels, ensemble ; positif : hausse) : un
  pour cent vaut 1 % du rendement 2025 de l'ensemble des régimes de base (Cour des comptes,
  mai 2026). Borne basse : chiffrage du doublement des montants et des plafonds présenté en 2025
  (2,3 Md€) ; borne haute : rendement en année pleine après la réforme de 2024 estimé par la
  CCSS (2 520 M€).
- **Plafond des revenus pris en compte pour les indemnités journalières maladie**
  (``ij_plafond_smic``, en points de Smic au-dessus de 140 % du Smic, de 0 à 40 ; positif :
  plafond relevé)
  : le relèvement à 1,8 Smic coûte l'économie de la baisse de 2025 en année pleine, économie de
  la première année (0,4 Md€ selon la Cour des comptes, 0,6 Md€ selon le PLFSS pour 2025) plus la
  montée en charge de 2026 (0,5 Md€, PLFSS pour 2026). Effet proportionnel à l'écart de
  plafond (hypothèse du lot : la répartition des salaires entre 1,4 et 1,8 Smic n'est pas
  connue). Première année : part de l'économie de 2025 dans l'économie en année pleine.

Les leviers sur les franchises et les indemnités journalières sont des façons d'atteindre
l'ONDAM : leur combinaison avec le levier ONDAM est refusée (double compte).
"""

from __future__ import annotations

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage, hypothese

LEVIER_ONDAM = "ondam_progression"
LEVIER_FRANCHISES = "franchises_participations"
LEVIER_IJ = "ij_plafond_smic"
LEVIERS = (LEVIER_ONDAM, LEVIER_FRANCHISES, LEVIER_IJ)
HYPOTHESE_REALISATION = "ondam_realisation_economies"

POURCENT = 100.0
MILLIONS_PAR_MILLIARD = 1000.0
BORNE_FRANCHISES = 100.0
"""Variation des montants et plafonds, en % : de la suppression au doublement (chiffré en
2025)."""
PLAFOND_ACTUEL_SMIC = 140.0
"""Plafond actuel, en % du Smic (1,4 Smic)."""
ECART_PLAFONDS_SMIC = 40.0
"""Écart entre le plafond antérieur (180 % du Smic) et le plafond actuel (140 %), en points de
Smic : seul domaine chiffré."""


def ondam_reference() -> float:
    """ONDAM 2025 voté en LFSS pour 2025, en Md€ (annexe 5 du PLFSS pour 2026)."""
    return chiffrage("ondam_objectif_initial_2025")


def realisation_economies() -> tuple[float, float]:
    """Part des économies prévues effectivement réalisées, en 2024 et en 2025 : un moins l'écart
    d'exécution à l'objectif initial rapporté aux économies intégrées à la construction (annexes 5
    des PLFSS pour 2026). Hypothèse : l'écart d'exécution tient entièrement aux économies."""
    ecart_2024 = chiffrage("ondam_constat_2024") - chiffrage("ondam_objectif_initial_2024")
    part_2024 = 1 - ecart_2024 / chiffrage("ondam_economies_2024")
    part_2025 = 1 - chiffrage("ondam_ecart_execution_2025") / chiffrage("ondam_economies_2025")
    return min(part_2024, part_2025), max(part_2024, part_2025)


def borne_ondam() -> float:
    """Borne du curseur, en points : mesures d'économies de la construction de l'ONDAM 2026
    rapportées à l'ONDAM 2026 proposé."""
    return round(POURCENT * chiffrage("ondam_economies_2026") / chiffrage("ondam_plfss_2026"), 1)


def rendement_point_ondam() -> Fourchette:
    """Effet sur le solde d'un point de progression de l'ONDAM en plus, en Md€ de 2025
    (négatif : dépenses en plus). Bornes : part des économies réalisées (hypothèse
    ``ondam_realisation_economies``)."""
    point = ondam_reference() / POURCENT
    plage = hypothese(HYPOTHESE_REALISATION).plage
    return encadrer(-point, [-point * plage.basse, -point * plage.haute])


def rendement_pourcent_franchises() -> Fourchette:
    """Rendement d'une hausse de 1 % des montants et des plafonds des franchises et
    participations forfaitaires, en Md€ de 2025."""
    central = chiffrage("franchises_pf_rendement_tous_regimes_2025") / POURCENT
    bas = chiffrage("franchises_pf_doublement_avec_plafonds_2026") / POURCENT
    apres_reforme = (
        chiffrage("franchises_pf_rendement_2022_ccss") + chiffrage("franchises_pf_doublement_ccss")
    ) / MILLIONS_PAR_MILLIARD
    return encadrer(central, [bas, apres_reforme / POURCENT])


def _economies_ij() -> tuple[float, float]:
    """Économie de la baisse du plafond de 1,8 à 1,4 Smic : première année (Cour des comptes,
    PLFSS pour 2025) et montée en charge de 2026 (PLFSS pour 2026), en Md€."""
    return (
        chiffrage("ij_plafond_lfss2025_ccomptes"),
        chiffrage("ij_plafond_1_8_1_4_plfss2025"),
    )


def rendement_smic_plafond_ij() -> Fourchette:
    """Effet sur le solde d'un relèvement du plafond d'un point de Smic (proportionnel, sur 40
    points), en Md€ (négatif : dépenses en plus). Économie en année pleine : économie de la
    première année plus la montée en charge de 2026 ; bornes : les deux chiffrages de la première
    année."""
    montee = chiffrage("ij_plafond_montee_charge_2026")
    totaux = [premiere + montee for premiere in _economies_ij()]
    central = sum(totaux) / len(totaux)
    return encadrer(-central / ECART_PLAFONDS_SMIC, [-t / ECART_PLAFONDS_SMIC for t in totaux])


def part_premiere_annee_ij() -> float:
    """Part de l'économie en année pleine acquise la première année (seuls les arrêts commencés
    après l'entrée en vigueur sont concernés) : moyenne des deux chiffrages de la première
    année."""
    montee = chiffrage("ij_plafond_montee_charge_2026")
    parts = [premiere / (premiere + montee) for premiere in _economies_ij()]
    return sum(parts) / len(parts)
