"""Impôt sur le revenu : revalorisation des seuils du barème (lot 2.11).

Levier : revalorisation des limites des tranches du barème, et des seuils et limites qui lui sont
associés (décote, plafonds du quotient familial), supérieure ou inférieure de x % à
l'indexation sur l'inflation. Un gel du barème quand l'inflation est de 1 % vaut x = -1.

Rendement d'un point (choix fait en autonomie, à relire, ``docs/fiches/impot_revenu.md``) :

- valeur centrale : sensibilité officielle de l'évaluation préalable de l'article 2 du PLF 2025
  (3,7 Md€ pour une absence d'indexation de 2 %, revenus 2024), tenue constante en part du PIB ;
- borne basse : calcul structurel sur les déciles de RFR par part de la DGFiP (revenus 2024,
  DGFiP Statistiques n° 41) et le barème d'OpenFisca. Pour un foyer dont le quotient familial
  q est dans la tranche k, revaloriser les seuils de i réduit l'impôt par part de
  i * (q * t_k - tau(q)), où tau est l'impôt d'une part ; rapporté à tau(q), le rapport
  s'applique à l'impôt au barème du décile, avec le RFR par part moyen comme quotient. Ce
  calcul ignore la décote, les plafonds du quotient familial et l'hétérogénéité au sein des
  déciles : il sous-estime l'effet (écart publié dans la fiche).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cache

from fr_budget.agrege.indexation import facteur_pib
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage

ANNEE_REVENUS = 2024
ANNEE_REFERENCE = 2025
DECILES = tuple(str(d) for d in range(2, 10))
"""Déciles 2 à 9 ; le premier n'a pas de RFR par part significatif, son impôt est négligeable."""
EUROS_PAR_MILLIARD = 1e9
POURCENT = 100.0


@dataclass(frozen=True)
class Segment:
    quotient: float
    """RFR par part moyen, en euros, pris comme quotient familial."""
    impot: float
    """Impôt au barème du segment, en euros."""


@cache
def _bareme() -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Seuils et taux du barème des revenus de 2024 (OpenFisca)."""
    b = (
        systeme_socio_fiscal()
        .parameters(f"{ANNEE_REVENUS}-01-01")
        .impot_revenu.bareme_ir_depuis_1945.bareme
    )
    return tuple(float(s) for s in b.thresholds), tuple(float(t) for t in b.rates)


def impot_par_part(quotient: float) -> float:
    """Impôt d'une part au barème, sans décote ni plafonnement."""
    seuils, taux = _bareme()
    hauts = (*seuils[1:], float("inf"))
    return sum(
        t * max(0.0, min(quotient, h) - s) for s, h, t in zip(seuils, hauts, taux, strict=True)
    )


def sensibilite_aux_seuils(quotient: float) -> float:
    """Baisse relative de l'impôt d'une part pour une revalorisation unitaire des seuils.

    q * t_k - tau(q), rapporté à tau(q) ; 0 si la part n'est pas imposée.
    """
    seuils, taux = _bareme()
    impot = impot_par_part(quotient)
    if impot <= 0:
        return 0.0
    marginal = max(t for s, t in zip(seuils, taux, strict=True) if quotient > s)
    return (quotient * marginal - impot) / impot


def _total(nom: str) -> float:
    return chiffrage(f"ir_{nom}_{ANNEE_REVENUS}") * EUROS_PAR_MILLIARD


def segments() -> list[Segment]:
    """Déciles 2 à 9, puis le dernier dixième découpé en trois (hors centième, centième hors
    millième, millième), d'après le tableau 2 de DGFiP Statistiques n° 41."""
    # Nombre de foyers d'un dixième : impôt total du dernier dixième divisé par son impôt moyen.
    par_decile = _total("impot_total_10") / chiffrage(f"ir_impot_bareme_moyen_10_{ANNEE_REVENUS}")
    resultat = [
        Segment(
            chiffrage(f"ir_rfr_part_moyen_{d}_{ANNEE_REVENUS}"),
            chiffrage(f"ir_impot_bareme_moyen_{d}_{ANNEE_REVENUS}") * par_decile,
        )
        for d in DECILES
    ]
    parts = {
        k: _total(f"rfr_total_{k}") / chiffrage(f"ir_rfr_part_moyen_{k}_{ANNEE_REVENUS}")
        for k in ("10", "c1", "m1")
    }
    rfr = {k: _total(f"rfr_total_{k}") for k in ("10", "c1", "m1")}
    impot = {k: _total(f"impot_total_{k}") for k in ("10", "c1", "m1")}
    resultat += [
        Segment((rfr["10"] - rfr["c1"]) / (parts["10"] - parts["c1"]), impot["10"] - impot["c1"]),
        Segment((rfr["c1"] - rfr["m1"]) / (parts["c1"] - parts["m1"]), impot["c1"] - impot["m1"]),
        Segment(rfr["m1"] / parts["m1"], impot["m1"]),
    ]
    return resultat


def rendement_structurel_un_pourcent() -> float:
    """Calcul par décile : hausse d'impôt d'une revalorisation inférieure de 1 % (revenus
    2024), en Md€."""
    return sum(s.impot * sensibilite_aux_seuils(s.quotient) for s in segments()) / (
        POURCENT * EUROS_PAR_MILLIARD
    )


def rendement_officiel_un_pourcent() -> float:
    """Sensibilité de l'évaluation préalable du PLF 2025 : rendement d'une revalorisation
    inférieure de 1 % (revenus 2024), en Md€."""
    return chiffrage("ir_non_indexation_2025") / chiffrage("ir_indexation_plf2025")


def rendement_un_pourcent() -> Fourchette:
    """Rendement d'une revalorisation des seuils inférieure de 1 %, en Md€ de 2025.

    Montants des revenus 2024, tenus constants en part du PIB nominal. Valeur centrale :
    sensibilité officielle ; borne basse : calcul par décile.
    """
    vers_2025 = facteur_pib(ANNEE_REFERENCE) / facteur_pib(ANNEE_REVENUS)
    return encadrer(
        rendement_officiel_un_pourcent() * vers_2025,
        [rendement_structurel_un_pourcent() * vers_2025],
    )


def rendement_gel(inflation: float, annee: int) -> float:
    """Rendement en ``annee`` d'un gel du barème quand l'inflation retenue vaut ``inflation``
    (en %), en Md€ (validation). Revenus de ``annee - 1``, tenus constants en part du PIB."""
    revenus = annee - 1
    return (
        inflation
        * rendement_officiel_un_pourcent()
        * facteur_pib(revenus)
        / facteur_pib(ANNEE_REVENUS)
    )
