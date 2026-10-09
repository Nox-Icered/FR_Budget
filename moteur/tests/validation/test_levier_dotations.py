"""Validation du levier « dotations aux collectivités » : montants votés face aux montants exécutés.

L'assiette du levier est un montant voté (prélèvement sur recettes). Sa validation compare le
montant inscrit en loi de finances initiale (évaluation initiale, tome I du PLF suivant) à
l'exécution (tome I du PLF de N+2), pour 2023 et 2024 :

- dotation globale de fonctionnement (ligne 3101) ;
- compensations du levier (lignes listées dans ``fr_budget.agrege.dotations``).

Tolérance : ±10 % (règle de publication, CLAUDE.md). La répercussion sur l'investissement local
(Caisse des Dépôts) n'est pas validée ici : aucune référence ne l'a encore confrontée.
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.dotations import COMPENSATIONS, DGF, execution
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
MILLIONS_PAR_MILLIARD = 1000.0


@pytest.mark.validation
@pytest.mark.parametrize("dotation", [DGF, COMPENSATIONS])
@pytest.mark.parametrize("annee", [2023, 2024])
def test_montant_vote_face_a_l_execution(dotation: str, annee: int) -> None:
    identifiant = f"dotations_{dotation}_execution_{annee}"
    reference = chiffrage(identifiant) / MILLIONS_PAR_MILLIARD
    modele = execution(dotation, annee).lfi
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"{identifiant} : voté {modele:.3f} Md€, exécuté {reference:.3f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
