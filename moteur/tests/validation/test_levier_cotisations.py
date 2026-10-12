"""Validation du levier « cotisations patronales ».

Références (``registres/references/chiffrages.yaml``) :

- valeur d'un point de cotisation déplafonnée du secteur privé publiée par la CCSS pour 2025
  (rapport d'octobre 2025, 7 380 M€) et pour 2017 (rapport de septembre 2018, 5 570 M€) ; le
  modèle part de la valeur de 2026 (rapport d'octobre 2026) tenue constante en part du PIB ;
- coût prévu des allègements généraux : 78,7 Md€ pour 2024 (CCSS d'octobre 2024) et 74,5 Md€
  pour 2025 (CCSS d'octobre 2025), comparés au coût constaté repris par le modèle (CCSS
  d'octobre 2026, hors réductions de taux des travailleurs non salariés).

Tolérance : ±10 % (règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.cotisations import cout_allegements, valeur_point_modele
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
MILLIONS_PAR_MILLIARD = 1000.0


def _verifier(reference: str, modele: float, valeur: float) -> None:
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.3f} Md€, référence {valeur:.3f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )


@pytest.mark.validation
@pytest.mark.parametrize("annee", [2025, 2017])
def test_valeur_d_un_point(annee: int) -> None:
    reference = f"cotisations_point_prive_{annee}"
    _verifier(reference, valeur_point_modele(annee), chiffrage(reference) / MILLIONS_PAR_MILLIARD)


@pytest.mark.validation
@pytest.mark.parametrize("annee", [2024, 2025])
def test_cout_des_allegements(annee: int) -> None:
    reference = f"allegements_generaux_prevision_{annee}"
    _verifier(reference, cout_allegements(annee), chiffrage(reference))
