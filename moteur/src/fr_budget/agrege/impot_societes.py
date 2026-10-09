"""Impôt sur les sociétés : IS brut et assiette des leviers (lot 2.3 du plan).

Données : DGFiP Statistiques n° 51, bénéfice imposable par taux et assiette de la
contribution exceptionnelle sur les bénéfices des grandes entreprises (CEBGE), années 2022 à
2025 (``data/processed/impot_societes/benefice_imposable.csv``). Taux : paramètres
OpenFisca-France (``taxation_societes.impot_societe``).

- IS brut = taux normal * bénéfice imposable à 25 % + taux réduit * bénéfice imposable à 15 %.
  Les plus-values et redevances imposées à des taux particuliers ne figurent pas dans la base
  publiée.
- Levier « taux normal » (décision du mainteneur du 9 octobre 2026, option (c)) : un point
  rapporte 1 % du bénéfice imposable au taux normal.
- Levier « surtaxe sur l'IS des grandes entreprises » : un point de surtaxe rapporte 1 % de
  l'assiette de la CEBGE (IS dû par les sociétés au chiffre d'affaires d'au moins 1 Md€).
- Calendrier (option (i)) : l'effet est compté en entier l'année d'entrée en vigueur ; en
  réalité, l'IS d'un exercice est versé par acomptes dans l'année et pour le solde l'année
  suivante.
"""

from __future__ import annotations

import csv
from functools import cache

from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.verification import RACINE_DEPOT

FICHIER = RACINE_DEPOT / "data" / "processed" / "impot_societes" / "benefice_imposable.csv"
POURCENT = 100.0


@cache
def _donnees() -> dict[tuple[int, str], float]:
    with FICHIER.open(encoding="utf-8") as f:
        return {(int(r["annee"]), r["indicateur"]): float(r["md_euros"]) for r in csv.DictReader(f)}


def benefice_imposable(annee: int) -> dict[str, float]:
    """Bénéfice imposable par taux, assiette de la CEBGE et déficits de l'année, en Md€."""
    return {i: v for (a, i), v in _donnees().items() if a == annee}


@cache
def taux_is(annee: int) -> dict[str, float]:
    """Taux normal et taux réduit (PME) de l'IS au 1er janvier, OpenFisca-France."""
    p = systeme_socio_fiscal().parameters.taxation_societes.impot_societe
    date = f"{annee}-01-01"
    return {"normal": float(p.taux_normal(date)), "reduit": float(p.taux_reduit(date))}


def is_brut(annee: int) -> float:
    """IS brut reconstitué, en Md€ (avant réductions et crédits d'impôt)."""
    b, t = benefice_imposable(annee), taux_is(annee)
    return t["normal"] * b["benefice_imposable_25"] + t["reduit"] * b["benefice_imposable_15"]


def rendement_point_taux_normal(annee: int) -> float:
    """Rendement statique d'un point de taux normal, en Md€."""
    return benefice_imposable(annee)["benefice_imposable_25"] / POURCENT


def assiette_surtaxe(annee: int) -> float:
    """Assiette d'une surtaxe sur l'IS des grandes entreprises (assiette de la CEBGE), en Md€."""
    return benefice_imposable(annee)["assiette_cebge"]
