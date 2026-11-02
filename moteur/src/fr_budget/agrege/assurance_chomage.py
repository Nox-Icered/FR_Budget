"""Assurance chômage, première étape : leviers agrégés calés sur les chiffrages de l'Unédic.

Plan validé par le mainteneur le 30 octobre 2026 (``docs/fiches/assurance_chomage.md``). Trois
leviers, tous en « bêta, non validé » :

- **contribution patronale** : hausse (ou baisse) de x points du taux de la contribution
  patronale d'assurance chômage (4,00 % depuis le 1er mai 2025, paramètres utiles de l'Unédic).
  Rendement d'un point : contributions principales de 2026 avant prélèvements de l'État
  (prévisions de l'Unédic d'octobre 2026, tableau 4), rapportées au taux de 2026 ;
- **revalorisation des allocations** : revalorisation au 1er juillet supérieure (ou
  inférieure) de x points à celle décidée. Profil de coût calé sur la revalorisation de 1,9 % du
  1er juillet 2023 (mode d'emploi de l'Unédic, juin 2023, tableau 2), en part des allocations
  brutes de 2023 : six mois l'année d'entrée, l'année suivante, puis les seuls paramètres fixes
  (partie fixe, ARE minimale, plancher de l'AREF), dont bénéficient aussi les nouveaux entrants.
  La revalorisation des salaires de référence ne touche que les allocataires présents et
  « s'atténue au gré des sorties d'indemnisation » (même document, page 4) : elle n'est plus
  comptée au-delà de la deuxième année ;
- **durée d'indemnisation** : variation de x du coefficient appliqué à la durée (0,75 depuis la
  réforme de 2023). Effet proportionnel à l'écart de coefficient, calé sur la réforme de 2023
  (coefficient de 1 à 0,75 : 4,2 Md€ de moindres allocations en régime de croisière, à horizon
  2027), avec la même montée en charge (Unédic, « Effets de l'adaptation des règles d'assurance
  chômage à la conjoncture », page 22).

Retours aux administrations publiques (choix 1 du plan) : les versements de l'Unédic à France
Travail (11 % des contributions, deux ans plus tard) et aux caisses de retraite complémentaire
(environ 7 % des allocations) restent à l'intérieur des administrations publiques et ne changent
pas leur solde : ils ne sont pas comptés. Les allocations supportent la CSG et la CRDS (taux
d'OpenFisca), dont une part revient aux administrations publiques (hypothèse
``chomage_retour_prelevements``).
"""

from __future__ import annotations

from functools import cache
from typing import Any

from fr_budget.baseline import resf
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage, hypothese

CONTRIBUTION = "contribution"
REVALORISATION = "revalorisation"
DUREE = "duree"
HYPOTHESE_RETOUR = "chomage_retour_prelevements"
HYPOTHESE_RAPPORT_DUREE = "chomage_duree_rapport_hypotheses_unedic"
HYPOTHESE_RANG_CROISIERE = "chomage_duree_rang_croisiere"
ANNEE_LEGISLATION = 2026
ANNEE_MONTANTS = 2026
ANNEE_CROISIERE_REFORME_2023 = 2027
MILLIONS_PAR_MILLIARD = 1000.0
POURCENT = 100.0
MOIS_PAR_AN = 12
MOIS_PREMIERE_ANNEE_CALAGE = 6
"""La revalorisation de calage entre en vigueur le 1er juillet : six mois la première année."""
MOIS_REVALORISATION = 7
"""Revalorisation annuelle au 1er juillet (règlement d'assurance chômage, mode d'emploi de
l'Unédic, page 1)."""
CONTRIBUTIONS = {
    2026: ("chomage_contributions_principales_2026", 1.0, "chomage_taux_contribution_2026"),
    2019: (
        "chomage_contributions_principales_2019",
        1 / MILLIONS_PAR_MILLIARD,
        "chomage_taux_contribution_2019",
    ),
}
"""Par année : contributions principales, facteur vers des Md€, taux de l'année (en %)."""
REFERENCES_CONTRIBUTION = {
    2026: "chomage_contribution_baisse_0_05_2026",
    2019: "chomage_contribution_hausse_0_05_2019",
}


def _croissance_nominale(annee: int) -> float:
    return resf()[(annee, "croissance_nominale")] / POURCENT


def vers_euros_2025(montant: float, annee: int) -> float:
    """Montant de l'année ``annee`` (2026 ou 2027) ramené en euros de 2025 par la croissance
    nominale du RESF 2027, comme les autres leviers exprimés en montants futurs."""
    for a in range(2026, annee + 1):
        montant /= 1 + _croissance_nominale(a)
    return montant


# --- Contribution patronale ------------------------------------------------------------------


def valeur_point_contribution(annee: int) -> float:
    """Rendement d'un point de contribution l'année ``annee`` (2019 ou 2026), en Md€ courants :
    contributions principales de l'année divisées par le taux de l'année."""
    cle, facteur, taux = CONTRIBUTIONS[annee]
    return chiffrage(cle) * facteur / chiffrage(taux)


def effet_contribution(points: float, annee: int) -> float:
    """Recettes d'une variation de ``points`` du taux l'année ``annee``, en Md€ (validation)."""
    return points * valeur_point_contribution(annee)


def rendement_point_contribution() -> Fourchette:
    """Rendement d'un point de contribution, en Md€ de 2025 (levier).

    Valeur centrale : celle de 2026 ramenée en euros de 2025. Bornes : la même, multipliée par
    le rapport entre le chiffrage de l'Unédic et le modèle pour chacune des deux mesures de
    0,05 point (2019 et 2026), en valeur absolue (choix 3 du plan)."""
    central = vers_euros_2025(valeur_point_contribution(ANNEE_MONTANTS), ANNEE_MONTANTS)
    points = chiffrage("chomage_contribution_points_0_05")
    rapports = [
        chiffrage(ref) / MILLIONS_PAR_MILLIARD / effet_contribution(points, annee)
        for annee, ref in REFERENCES_CONTRIBUTION.items()
    ]
    return encadrer(central, [central * r for r in rapports])


# --- Retour de CSG et de CRDS ------------------------------------------------------------------


@cache
def taux_prelevements_allocations() -> float:
    """CSG et CRDS sur une allocation chômage, en part de l'allocation brute (OpenFisca,
    législation de 2026) : (taux global de CSG + CRDS) * (1 - abattement de la première
    tranche)."""
    parametres: Any = systeme_socio_fiscal().parameters(f"{ANNEE_LEGISLATION}-01-01")
    sociaux = parametres.prelevements_sociaux.contributions_sociales
    chomage = sociaux.csg.remplacement.allocations_chomage
    abattement = float(chomage.abattement.rates[0])
    return (float(chomage.taux_global) + float(sociaux.crds)) * (1 - abattement)


def parts_retour() -> list[float]:
    """Part de l'allocation qui revient aux APU : valeur centrale puis bornes."""
    t = taux_prelevements_allocations()
    plage = hypothese(HYPOTHESE_RETOUR)
    return [t * plage.valeur_centrale, t * plage.plage.basse, t * plage.plage.haute]


# --- Revalorisation des allocations ------------------------------------------------------------


def parts_revalorisation() -> tuple[float, float, float]:
    """Coût d'un point de revalorisation, en part des allocations brutes de l'année de calage
    (2023) : première année (six mois), deuxième année, années suivantes (paramètres fixes)."""
    taux = chiffrage("chomage_revalorisation_juillet_2023_taux")
    allocations = chiffrage("chomage_allocations_brutes_2023") * MILLIONS_PAR_MILLIARD
    fixes = sum(
        chiffrage(f"chomage_revalorisation_juillet_2023_{element}_2024")
        for element in ("partie_fixe", "minimale", "plancher_aref")
    )
    premiere = chiffrage("chomage_revalorisation_juillet_2023_total_2023")
    deuxieme = chiffrage("chomage_revalorisation_juillet_2023_total_2024")
    return (
        premiere / taux / allocations,
        deuxieme / taux / allocations,
        fixes / taux / allocations,
    )


def cout_revalorisation_annee(points: float, rang: int, mois: int, allocations: float) -> float:
    """Coût brut de ``points`` de revalorisation entrée en vigueur le mois ``mois``, l'année de
    rang ``rang`` (1 = année d'entrée), pour des allocations annuelles ``allocations`` (Md€).
    La première année compte les mois qui suivent l'entrée en vigueur."""
    premiere, deuxieme, suivantes = parts_revalorisation()
    if rang == 1:
        part = premiere * (MOIS_PAR_AN + 1 - mois) / MOIS_PREMIERE_ANNEE_CALAGE
    elif rang == 2:  # noqa: PLR2004
        part = deuxieme
    else:
        part = suivantes
    return points * part * allocations


def cout_revalorisation_cumule(points: float, mois: int, allocations: float) -> float:
    """Coût brut cumulé sur l'année d'entrée et la suivante, en Md€ (validation)."""
    return sum(cout_revalorisation_annee(points, r, mois, allocations) for r in (1, 2))


def allocations_reference() -> float:
    """Allocations brutes et aides de 2026, en Md€ de 2025."""
    return vers_euros_2025(chiffrage("chomage_allocations_brutes_2026"), ANNEE_MONTANTS)


def effet_revalorisation(rang: int) -> Fourchette:
    """Effet d'un point de revalorisation au 1er juillet sur le solde des APU, l'année de rang
    ``rang``, en Md€ de 2025 : moins le coût brut, net de la CSG et de la CRDS qui reviennent."""
    brut = cout_revalorisation_annee(1.0, rang, MOIS_REVALORISATION, allocations_reference())
    valeurs = [-brut * (1 - r) for r in parts_retour()]
    return encadrer(valeurs[0], valeurs[1:])


# --- Durée d'indemnisation ----------------------------------------------------------------------


def economie_reforme_2023() -> tuple[float, float]:
    """Réforme de 2023 : moindres allocations en régime de croisière (Md€ de 2027) et baisse du
    coefficient appliqué à la durée (de 1 au coefficient actuel)."""
    baisse = 1 - chiffrage("chomage_coefficient_duree_2026")
    return chiffrage("chomage_reforme_2023_allocations_croisiere"), baisse


def montee_en_charge_duree(rang: int, rang_croisiere: float) -> float:
    """Part de l'effet de croisière atteinte l'année de rang ``rang`` (1 = année d'entrée), selon
    le profil de la réforme de 2023 : 0 la première année, puis 2024, 2025, et le plein effet à
    partir de ``rang_croisiere`` (la quatrième année restant au niveau de la troisième si le plein
    effet n'arrive que la cinquième)."""
    croisiere = chiffrage("chomage_reforme_2023_moindres_depenses_croisiere")
    if rang >= rang_croisiere:
        return 1.0
    if rang <= 1:
        return 0.0
    cle = "2024" if rang == 2 else "2025"  # noqa: PLR2004
    return chiffrage(f"chomage_reforme_2023_moindres_depenses_{cle}") / croisiere


def effet_duree(rang: int) -> Fourchette:
    """Effet d'une hausse de 1 du coefficient appliqué à la durée (durées plus longues) sur le
    solde des APU, l'année de rang ``rang``, en Md€ de 2025 : moins le surcoût d'allocations, net
    de la CSG et de la CRDS qui reviennent. Bornes : hypothèses de l'Unédic sur le prolongement
    des droits des seniors, retour de prélèvements et rang de l'année de plein effet."""
    economie, baisse = economie_reforme_2023()
    par_unite = vers_euros_2025(economie, ANNEE_CROISIERE_REFORME_2023) / baisse
    rapport = hypothese(HYPOTHESE_RAPPORT_DUREE)
    rang_croisiere = hypothese(HYPOTHESE_RANG_CROISIERE)
    retour_central, *retours = parts_retour()
    central = (
        -par_unite
        * montee_en_charge_duree(rang, rang_croisiere.valeur_centrale)
        * (1 - retour_central)
        * rapport.valeur_centrale
    )
    extremes = [
        -par_unite * montee_en_charge_duree(rang, rc) * (1 - r) * k
        for rc in (rang_croisiere.plage.basse, rang_croisiere.plage.haute)
        for r in retours
        for k in (rapport.plage.basse, rapport.plage.haute)
    ]
    return encadrer(central, extremes)
