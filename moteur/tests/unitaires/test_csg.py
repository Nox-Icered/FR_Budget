"""Tests du levier « CSG » (fr_budget.agrege.csg et scénario)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import csg
from fr_budget.scenario import (
    LEVIERS_CSG,
    Mesure,
    bornes_levier,
    levier_registre,
    rendement_unitaire,
    scenario,
    taux_reference,
)


@pytest.mark.parametrize("foyer", ["personne_seule", "couple"])
def test_part_du_taux_plein_entre_0_et_1(foyer: str) -> None:
    assert 0 < csg.part_taux_plein(2020, foyer) < 1


def test_un_point_d_activite_est_le_rendement_divise_par_le_taux() -> None:
    f = csg.rendement_un_point(csg.ACTIVITE)
    attendu = csg.rendement(csg.ACTIVITE, 2025) / csg.taux(csg.ACTIVITE, 2025)
    assert f.central == pytest.approx(attendu)
    assert f.bas <= f.central <= f.haut


@pytest.mark.parametrize("levier", list(LEVIERS_CSG))
def test_leviers_csg_dans_le_scenario(levier: str) -> None:
    assert rendement_unitaire(levier).bas > 0
    assert bornes_levier(levier) == (-2.0, 2.0)
    assert levier_registre(levier) == "csg"
    assert taux_reference(levier) > 0
    assert scenario([Mesure(levier, 1.0, 2027)])[-1].ecart_dette.central < 0


def test_hausse_d_un_point_d_activite_ordre_de_grandeur() -> None:
    """Un point de CSG d'activité rapporte plus que les deux autres assiettes réunies."""
    activite = rendement_unitaire("csg_activite").central
    autres = rendement_unitaire("csg_retraites").central + rendement_unitaire("csg_capital").central
    assert activite > autres
