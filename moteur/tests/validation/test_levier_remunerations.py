"""Validation du levier « rémunérations publiques » : coût d'une hausse du point d'indice.

Références : Sénat, avis n° 134 (2023-2024) sur le PLF 2024, « Fonction publique », tableau
« Coûts des dernières revalorisations du point d'indice », page 8 (réponses du Gouvernement
au questionnaire budgétaire) : coût en année pleine de la hausse de 3,5 % de juillet 2022 (en
2023) et de 1,5 % de juillet 2023 (en 2024), total et par versant.

Le modèle applique la hausse à la masse de la première année pleine (qui la contient déjà),
selon ``fr_budget.agrege.remunerations.cout_brut_point_mesure``. Tolérance : ±10 % (règle de
publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.remunerations import VERSANTS, cout_brut_point_mesure
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
MESURES = {"3_5": (0.035, 2023), "1_5": (0.015, 2024)}


@pytest.mark.validation
@pytest.mark.parametrize("mesure", list(MESURES))
@pytest.mark.parametrize("versant", [*VERSANTS, "total"])
def test_cout_d_une_hausse_du_point(mesure: str, versant: str) -> None:
    taux, annee = MESURES[mesure]
    identifiant = f"remunerations_point_{mesure}_{versant}_{annee}"
    reference = chiffrage(identifiant)
    versants = list(VERSANTS) if versant == "total" else [versant]
    modele = sum(cout_brut_point_mesure(v, taux, annee) for v in versants)
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"{identifiant} : modèle {modele:.2f} Md€, référence {reference:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
