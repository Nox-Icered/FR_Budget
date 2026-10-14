"""Validation du module « entreprises » : les données de l'Urssaf qui répartissent les effets
des leviers sur les cotisations patronales, confrontées aux comptes de la sécurité sociale.

Références (``registres/references/chiffrages.yaml``) :

- valeur d'un point de cotisation déplafonnée du secteur privé, CCSS : 7 380 M€ pour 2025
  (rapport d'octobre 2025) et 5 570 M€ pour 2017 (rapport de septembre 2018) ; comparée à 1 % de
  la masse salariale du secteur privé de l'Urssaf de la même année ;
- coût des allègements généraux des salariés, CCSS d'octobre 2026 (2024 et 2025, hors
  réductions de taux des travailleurs non salariés) ; comparé à la somme des catégories 11, 15
  et 16 des exonérations de l'Urssaf.

Tolérance : ±10 % (règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.cotisations import cout_allegements
from fr_budget.entreprises import repartition as r
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
MILLIONS_PAR_MILLIARD = 1000.0


def _verifier(reference: str, modele: float, valeur: float) -> None:
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : Urssaf {modele:.3f} Md€, référence {valeur:.3f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )


@pytest.mark.validation
@pytest.mark.parametrize("annee", [2025, 2017])
def test_point_de_cotisation_sur_la_masse_salariale(annee: int) -> None:
    reference = f"cotisations_point_prive_{annee}"
    _verifier(
        reference, r.point_masse_salariale(annee), chiffrage(reference) / MILLIONS_PAR_MILLIARD
    )


@pytest.mark.validation
def test_allegements_de_l_urssaf() -> None:
    _verifier("allegements_generaux_total_2024", r.allegements_urssaf(), cout_allegements(2024))
