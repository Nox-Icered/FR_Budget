"""Tests du levier « cotisations patronales » (fr_budget.agrege.cotisations et scénario)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import cotisations
from fr_budget.scenario import (
    LEVIER_ALLEGEMENTS,
    LEVIER_COTISATIONS_TAUX,
    Mesure,
    bornes_levier,
    levier_registre,
    rendement_unitaire,
    scenario,
)


def test_cout_des_allegements_hors_independants() -> None:
    total = 77.554
    assert cotisations.cout_allegements(2025) == pytest.approx(total - 0.811 - 1.100)


def test_hausse_du_taux_ameliore_le_solde() -> None:
    assert rendement_unitaire(LEVIER_COTISATIONS_TAUX).bas > 0
    assert bornes_levier(LEVIER_COTISATIONS_TAUX) == (-2.0, 2.0)
    assert scenario([Mesure(LEVIER_COTISATIONS_TAUX, 1.0, 2027)])[-1].ecart_dette.central < 0


def test_baisse_des_allegements_ameliore_le_solde() -> None:
    r = rendement_unitaire(LEVIER_ALLEGEMENTS)
    assert r.haut < 0
    assert r.central == pytest.approx(-cotisations.cout_allegements(2025) / 100)
    assert bornes_levier(LEVIER_ALLEGEMENTS) == (-20.0, 20.0)
    assert scenario([Mesure(LEVIER_ALLEGEMENTS, -10.0, 2027)])[-1].ecart_dette.central < 0


@pytest.mark.parametrize("levier", [LEVIER_COTISATIONS_TAUX, LEVIER_ALLEGEMENTS])
def test_registre(levier: str) -> None:
    assert levier_registre(levier) == "cotisations_patronales"
