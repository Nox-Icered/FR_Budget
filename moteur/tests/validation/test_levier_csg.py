"""Validation du levier « CSG ».

Références (``registres/references/chiffrages.yaml``) :

- rapport à la Commission des comptes de la sécurité sociale (CCSS) de septembre 2018, fiche
  1.3 : supplément de rendement en 2018 de la hausse de 1,7 point de la CSG (LFSS 2018) sur
  les revenus d'activité (16 052 M€), sur les retraites au taux plein (4 181 M€) et sur les
  revenus du capital (2,1 Md€) ; rendement de la CSG sur les retraites au taux plein en 2017
  (15 780 M€), qui contrôle la part du taux plein calculée avec OpenFisca ;
- rapport du Sénat n° 131 (2025-2026), tome I, page 112 : passage de 9,2 % à 10,6 % du taux de
  la CSG sur les revenus du patrimoine et des placements, 2,8 Md€ en 2026.

Le modèle applique la hausse à l'assiette de l'année précédente (rendement constaté divisé par
le taux), portée à l'année de la mesure par la croissance du PIB nominal. Tolérance : ±10 %
(règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.csg import ACTIVITE, CAPITAL, RETRAITES, hausse_mesuree, rendement_taux_plein
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
MILLIONS_PAR_MILLIARD = 1000.0

# Référence : (assiette, hausse en points, année de la mesure, unité de la référence)
MESURES = {
    "csg_hausse_1_7_2018_activite": (ACTIVITE, 1.7, 2018, "M€"),
    "csg_hausse_1_7_2018_retraites": (RETRAITES, 1.7, 2018, "M€"),
    "csg_hausse_1_7_2018_capital": (CAPITAL, 1.7, 2018, "Md€"),
    "csg_hausse_capital_1_4_2026": (CAPITAL, 1.4, 2026, "Md€"),
}


def _en_milliards(valeur: float, unite: str) -> float:
    return valeur / MILLIONS_PAR_MILLIARD if unite == "M€" else valeur


def _verifier(reference: str, modele: float, valeur: float) -> None:
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.3f} Md€, référence {valeur:.3f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )


@pytest.mark.validation
@pytest.mark.parametrize("reference", list(MESURES))
def test_rendement_d_une_hausse(reference: str) -> None:
    assiette, points, annee, unite = MESURES[reference]
    modele = hausse_mesuree(assiette, points, annee)
    _verifier(reference, modele, _en_milliards(chiffrage(reference), unite))


@pytest.mark.validation
def test_part_du_taux_plein_sur_les_retraites_2017() -> None:
    reference = "csg_rendement_retraites_taux_plein_2017"
    modele = rendement_taux_plein(2017)
    _verifier(reference, modele, chiffrage(reference) / MILLIONS_PAR_MILLIARD)
