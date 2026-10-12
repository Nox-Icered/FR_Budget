"""Prime d'activité : fraction des revenus professionnels prise en compte (« pente », lot 2.12).

Levier (décision du mainteneur du 12 octobre 2026 : « levier calé ») : variation de x points de
la fraction des revenus professionnels prise en compte dans le calcul de la prime d'activité
(59,85 % depuis le 1er avril 2025, paramètre d'OpenFisca). Une hausse augmente la prime.

Rendement d'un point, calé sur un chiffrage officiel faute de données sur les revenus des
allocataires (micro-données non publiables) :

- valeur centrale : le rendement en année pleine annoncé par l'administration pour la baisse de
  1,15 point de 2025 (500 M€), divisé par 1,15 ;
- borne basse : la même, multipliée par le rapport entre les crédits de prime d'activité prévus
  pour 2026 (9,3 Md€) et la dépense de 2024 (10,5 Md€), pour tenir compte d'une prime plus
  réduite après les mesures de 2025 et 2026.
"""

from __future__ import annotations

from functools import cache
from typing import Any

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage

MILLIONS_PAR_MILLIARD = 1000.0
MOIS_PAR_AN = 12
PARAMETRE_PENTE = (
    "prestations_sociales.solidarite_insertion.minima_sociaux.ppa.pa_m."
    "majoration_ressources_revenus_activite"
)


@cache
def _parametre() -> Any:
    noeud: Any = systeme_socio_fiscal().parameters
    for nom in PARAMETRE_PENTE.split("."):
        noeud = noeud.children[nom]
    return noeud


def pente_actuelle() -> float:
    """Fraction des revenus professionnels prise en compte, en % (dernière valeur d'OpenFisca)."""
    return float(_parametre().values_list[0].value) * 100


def mois_derniere_modification() -> int:
    """Mois d'entrée en vigueur de la dernière modification de la pente (OpenFisca)."""
    return int(_parametre().values_list[0].instant_str[5:7])


def rendement_un_point_officiel() -> float:
    """Économie en année pleine d'une baisse d'un point de la pente, en Md€ (calage)."""
    return (
        chiffrage("pa_pente_rendement_annee_pleine")
        / chiffrage("pa_pente_baisse_2025_points")
        / MILLIONS_PAR_MILLIARD
    )


def cout_un_point() -> Fourchette:
    """Coût en année pleine d'une hausse d'un point de la pente, en Md€ de 2025."""
    central = rendement_un_point_officiel()
    reduite = central * chiffrage("pa_credits_plf2026") / chiffrage("pa_depense_2024")
    return encadrer(central, [reduite])


def economie_baisse_2025() -> float:
    """Économie en 2025 de la baisse de 1,15 point du 1er avril 2025, en Md€ (validation) :
    le rendement en année pleine, pour les mois qui suivent l'entrée en vigueur."""
    part = (MOIS_PAR_AN + 1 - mois_derniere_modification()) / MOIS_PAR_AN
    return chiffrage("pa_pente_baisse_2025_points") * rendement_un_point_officiel() * part
