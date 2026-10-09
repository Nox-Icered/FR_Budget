"""Validation du levier « accises sur les carburants » : recette brute de l'ex-TICPE.

Références : Évaluation des voies et moyens, tome I, ligne 1501 (registres/references/
chiffrages.yaml) :
- PLF 2025 : recette brute totale 2023 (exécution), 31,7 Md€ ;
- PLF 2026 : recette brute totale 2024 (exécution), 31,6 Md€.
Tolérance : ±10 % (règle de publication, CLAUDE.md).

Le modèle multiplie les ventes de produits pétroliers du SDES (métropole) par les tarifs
d'accise ; la recette brute est avant remboursements, comme la référence.
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.accises import recette_brute
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10


@pytest.mark.validation
@pytest.mark.parametrize("annee", [2023, 2024])
def test_recette_brute_ticpe(annee: int) -> None:
    identifiant = f"accises_ticpe_brute_totale_{annee}"
    reference = chiffrage(identifiant)
    modele = recette_brute(annee)
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"{identifiant} : modèle {modele:.2f} Md€, référence {reference:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
