"""Réponses exactes par cran du levier non linéaire (âge légal de départ)."""

from __future__ import annotations

import pytest
from fr_budget import scenario

from fr_budget_api.app import _grille


def test_grille_coherente_avec_la_reponse_a_un_an() -> None:
    levier = scenario.LEVIER_RETRAITES_AGE_LEGAL
    grille = _grille(levier)
    assert set(grille) == {f"{v:g}" for v in scenario.grille_levier(levier)}
    un_an = scenario.reponse_lineaire(levier, scenario.ANNEE_PREMIERE_MESURE)
    cran = grille["1"][str(scenario.ANNEE_PREMIERE_MESURE)]
    assert cran["unite_solde"][0] == pytest.approx(un_an.unite_solde[0], abs=1e-6)
