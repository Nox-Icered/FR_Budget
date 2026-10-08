"""Comptes des administrations publiques (APU) par sous-secteur (lot 1.1 du plan).

Données : INSEE, comptes nationaux annuels base 2020, édition 2025, extraites par
``pipelines/apu/extraire_comptes_apu.py`` dans ``data/processed/apu/comptes_apu.csv``
(montants en milliards d'euros).

Sous-secteurs (codes du SEC 2010) : S13 ensemble des APU, S1311 administration centrale,
S13111 État, S13112 organismes divers d'administration centrale, S1313 administrations
locales, S1314 administrations de sécurité sociale ; S1 pour le PIB.

Indicateurs : ``depenses``, ``recettes``, ``capacite_financement`` (B9NF), ``interets_verses``
et ``interets_recus`` (D41), ``dette_maastricht``, ``solde_maastricht``, ``pib`` (B1GQ).
"""

from __future__ import annotations

import csv
from collections.abc import Mapping
from dataclasses import dataclass
from functools import cache

from fr_budget.registres.verification import RACINE_DEPOT

FICHIER = RACINE_DEPOT / "data" / "processed" / "apu" / "comptes_apu.csv"
FICHIER_COFOG = RACINE_DEPOT / "data" / "processed" / "apu" / "cofog.csv"
POURCENT = 100


@dataclass(frozen=True)
class ComptesApu:
    valeurs: Mapping[tuple[int, str, str], float]

    def valeur(self, annee: int, sous_secteur: str, indicateur: str) -> float:
        return self.valeurs[(annee, sous_secteur, indicateur)]

    def annees(self, sous_secteur: str, indicateur: str) -> list[int]:
        return sorted(a for a, s, i in self.valeurs if s == sous_secteur and i == indicateur)


@cache
def comptes_apu() -> ComptesApu:
    with FICHIER.open(encoding="utf-8") as f:
        return ComptesApu(
            {
                (int(r["annee"]), r["sous_secteur"], r["indicateur"]): float(r["milliards_euros"])
                for r in csv.DictReader(f)
            }
        )


@cache
def depenses_par_fonction() -> dict[tuple[int, str, str], float]:
    """Dépenses des APU par fonction COFOG, en Md€ : clé (année, sous-secteur, code COFOG).

    Source : Eurostat, gov_10a_exp (``pipelines/apu/extraire_cofog.py``). Codes : ``TOTAL``,
    ``GF01`` à ``GF10`` (divisions) et leurs groupes (``GF0101``…).
    """
    with FICHIER_COFOG.open(encoding="utf-8") as f:
        return {
            (int(r["annee"]), r["sous_secteur"], r["cofog"]): float(r["milliards_euros"])
            for r in csv.DictReader(f)
        }


def solde_primaire(capacite_financement: float, interets_verses: float) -> float:
    """Solde primaire : capacité (+) ou besoin (-) de financement hors intérêts versés (D41).

    Convention retenue par le mainteneur le 8 octobre 2026 : intérêts versés, comme le terme
    ``r * d`` de la dynamique de la dette, qui porte sur la dette brute. L'autre convention,
    intérêts nets des intérêts reçus, est présentée dans docs/fiches/comptes_apu.md.
    """
    return capacite_financement + interets_verses


def ratio_pib(montant: float, pib: float) -> float:
    """Montant en pourcentage du PIB."""
    return montant / pib * POURCENT
