"""Validation du levier « crédits par mission » : crédits votés face aux dépenses constatées.

Le rendement du levier est une part des crédits demandés. Sa validation compare ce que le
modèle aurait pris pour assiette avec une loi de finances initiale (crédits votés en LFI) aux
dépenses constatées dans le projet de loi relatif aux résultats de la gestion (PLRG) de la même
année, pour l'ensemble des missions du levier : exercices 2023, 2024 et 2025.
Tolérance : ±10 % (règle de publication, CLAUDE.md). Ce n'est pas une source indépendante.
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.credits_missions import total_execution
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
EUROS_PAR_MILLIARD = 1e9


@pytest.mark.validation
@pytest.mark.parametrize("exercice", [2023, 2024, 2025])
def test_credits_votes_face_aux_depenses_constatees(exercice: int) -> None:
    identifiant = f"credits_missions_depenses_constatees_{exercice}"
    reference = chiffrage(identifiant)
    modele = total_execution(exercice)[0] / EUROS_PAR_MILLIARD
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"{identifiant} : crédits votés {modele:.1f} Md€, dépenses constatées "
        f"{reference:.1f} Md€, écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
