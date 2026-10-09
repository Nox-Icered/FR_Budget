"""Validation du levier « impôt sur les sociétés » : IS brut reconstitué.

Références : DGFiP Statistiques (registres/references/chiffrages.yaml) :
- n° 39 (septembre 2025) : IS brut 2024, 69,05 Md€ ;
- n° 51 (septembre 2026) : IS brut 2025, 70,47 Md€.
Tolérance : ±10 % (règle de publication, CLAUDE.md).

Le modèle applique les taux de l'IS (OpenFisca-France) au bénéfice imposable par taux publié
dans les mêmes notes : la validation contrôle la cohérence des taux et de la base, elle n'est
pas indépendante de la source. Les plus-values et redevances imposées à des taux particuliers
ne sont pas dans la base publiée (note n° 51, graphique 2).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.impot_societes import is_brut
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10


@pytest.mark.validation
@pytest.mark.parametrize("annee", [2024, 2025])
def test_is_brut_reconstitue(annee: int) -> None:
    identifiant = f"is_brut_{annee}_dgfip"
    reference = chiffrage(identifiant)
    modele = is_brut(annee)
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"{identifiant} : modèle {modele:.2f} Md€, référence {reference:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
