"""Tests du levier « impôt sur le revenu » (fr_budget.agrege.impot_revenu et scénario)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import impot_revenu as ir
from fr_budget.registres.acces import chiffrage
from fr_budget.scenario import (
    LEVIER_IR_SEUILS,
    Mesure,
    bornes_levier,
    levier_registre,
    rendement_unitaire,
    scenario,
)


def test_bareme_des_revenus_2024() -> None:
    seuils, taux = ir._bareme()
    assert seuils[1] == 11497
    assert taux[-1] == pytest.approx(0.45)


def test_impot_par_part_et_sensibilite() -> None:
    # Une part à 20 000 € : 11 % de 20 000 - 11 497.
    assert ir.impot_par_part(20000) == pytest.approx(0.11 * (20000 - 11497))
    # q t_k - tau = 0,11 * 11 497 ; rapporté à tau.
    assert ir.sensibilite_aux_seuils(20000) == pytest.approx(11497 / (20000 - 11497))
    assert ir.sensibilite_aux_seuils(10000) == 0.0


def test_segments_couvrent_l_impot_au_bareme() -> None:
    total = sum(s.impot for s in ir.segments()) / 1e9
    assert total == pytest.approx(chiffrage("ir_impot_total_total_2024"), rel=0.01)


def test_levier_dans_le_scenario() -> None:
    r = rendement_unitaire(LEVIER_IR_SEUILS)
    assert r.bas < r.haut < 0
    assert bornes_levier(LEVIER_IR_SEUILS) == (-3.0, 3.0)
    assert levier_registre(LEVIER_IR_SEUILS) == "impot_revenu"
    assert scenario([Mesure(LEVIER_IR_SEUILS, -1.0, 2027)])[-1].ecart_dette.central < 0
