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

Deuxième étape (plan validé le 9 novembre 2026, option (a)) : deux leviers sur le ticket
modérateur, en points (positif : hausse de la part non remboursée), de -10 à +10 points, seul
domaine chiffré.

- **Consultations des médecins et des sages-femmes** (``ticket_moderateur_consultations``) : la
  hausse de 30 % à 40 % prévue pour 2025 devait rapporter 1,0 Md€ en ville et 0,1 Md€ dans les
  établissements (annexe 5 du PLFSS pour 2025 ; 1,1 Md€ selon le Sénat), effet proportionnel
  aux points. Estimation avant la mesure, qui n'a pas été appliquée : bornes de la part des
  économies prévues effectivement réalisées (hypothèse ``ondam_realisation_economies``).
- **Soins dentaires** (``ticket_moderateur_dentaire``) : la hausse de 30 % à 40 % appliquée le
  15 octobre 2023 a économisé 525 M€ jusqu'à décembre 2024 (constat de la Cour des comptes, mai
  2026), ramené à un an. Borne basse : hausse de deux points de la part des organismes
  complémentaires dans le financement des soins dentaires de 2024, même source.

Montants en euros de l'année du chiffrage, sans conversion (comme les franchises).

Les leviers sur les franchises, les indemnités journalières et le ticket modérateur sont des
façons d'atteindre l'ONDAM : leur combinaison avec le levier ONDAM est refusée (double compte).
"""

from __future__ import annotations

from datetime import date

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage, hypothese

LEVIER_ONDAM = "ondam_progression"
LEVIER_FRANCHISES = "franchises_participations"
LEVIER_IJ = "ij_plafond_smic"
LEVIER_TM_CONSULTATIONS = "ticket_moderateur_consultations"
LEVIER_TM_DENTAIRE = "ticket_moderateur_dentaire"
LEVIERS_TICKET_MODERATEUR = (LEVIER_TM_CONSULTATIONS, LEVIER_TM_DENTAIRE)
LEVIERS = (LEVIER_ONDAM, LEVIER_FRANCHISES, LEVIER_IJ, *LEVIERS_TICKET_MODERATEUR)
LEVIERS_DANS_ONDAM = (LEVIER_FRANCHISES, LEVIER_IJ, *LEVIERS_TICKET_MODERATEUR)
"""Mesures qui sont des façons d'atteindre l'ONDAM : refusées avec le levier ONDAM."""
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
DEBUT_CONSTAT_DENTAIRE = date(2023, 10, 15)
FIN_CONSTAT_DENTAIRE = date(2025, 1, 1)
"""Période du constat de la Cour des comptes (mai 2026, page 216) : hausse appliquée le 15 octobre
2023, économie mesurée jusqu'à fin décembre 2024 (borne exclue)."""
JOURS_PAR_AN = 365.25


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


def ecart_tm_consultations() -> float:
    """Hausse chiffrée du ticket modérateur des consultations, en points (de 30 % à 40 %)."""
    return chiffrage("tm_consultations_taux_projet_2025") - chiffrage("tm_consultations_taux_2024")


def ecart_tm_dentaire() -> float:
    """Hausse du ticket modérateur des soins dentaires de 2023, en points (de 30 % à 40 %)."""
    return chiffrage("tm_dentaire_taux_apres_2023") - chiffrage("tm_dentaire_taux_avant_2023")


def economie_tm_consultations() -> float:
    """Économie attendue de la hausse prévue pour 2025, en Md€ : soins de ville et établissements
    (annexe 5 du PLFSS pour 2025, pages 8 et 9)."""
    return chiffrage("tm_consultations_economie_ville_plfss2025") + chiffrage(
        "tm_consultations_economie_etablissements_plfss2025"
    )


def rendement_point_tm_consultations() -> Fourchette:
    """Rendement d'un point de ticket modérateur en plus sur les consultations des médecins et des
    sages-femmes, en Md€ (positif : économie). Central : chiffrage du PLFSS pour 2025 rapporté aux
    points ; bornes : part des économies prévues réalisées (``ondam_realisation_economies``)."""
    point = economie_tm_consultations() / ecart_tm_consultations()
    plage = hypothese(HYPOTHESE_REALISATION).plage
    return encadrer(point, [point * plage.basse, point * plage.haute])


def annees_constat_dentaire() -> float:
    """Durée de la période du constat de la Cour des comptes, en années."""
    return (FIN_CONSTAT_DENTAIRE - DEBUT_CONSTAT_DENTAIRE).days / JOURS_PAR_AN


def economie_annuelle_tm_dentaire() -> float:
    """Économie constatée de la hausse de 2023, ramenée à un an, en Md€ (Cour des comptes)."""
    constat = chiffrage("tm_dentaire_economie_oct2023_dec2024") / MILLIONS_PAR_MILLIARD
    return constat / annees_constat_dentaire()


def economie_part_complementaires_dentaire() -> float:
    """Économie de 2024 lue dans la hausse de la part des organismes complémentaires, en Md€ :
    points de part gagnés fois les dépenses de soins dentaires de 2024 (dépenses des
    complémentaires divisées par leur part ; Cour des comptes, d'après la DREES)."""
    total = chiffrage("dentaire_depenses_complementaires_2024") / (
        chiffrage("dentaire_part_complementaires_2024") / POURCENT
    )
    return chiffrage("tm_dentaire_hausse_part_complementaires") / POURCENT * total


def rendement_point_tm_dentaire() -> Fourchette:
    """Rendement d'un point de ticket modérateur en plus sur les soins dentaires, en Md€ (positif :
    économie). Central : constat ramené à un an ; borne basse : hausse de la part des
    complémentaires ; pas de borne haute sourcée au-delà du constat."""
    ecart = ecart_tm_dentaire()
    return encadrer(
        economie_annuelle_tm_dentaire() / ecart, [economie_part_complementaires_dentaire() / ecart]
    )
