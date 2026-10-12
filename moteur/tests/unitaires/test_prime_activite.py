"""Tests du levier « prime d'activité » : pente (lot 2.12)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import prime_activite as pa
from fr_budget.scenario import (
    LEVIER_PA_PENTE,
    MISSION_SOLIDARITE,
    Mesure,
    bornes_levier,
    levier_credits_mission,
    levier_registre,
    rendement_unitaire,
    scenario,
)


def test_pente_et_date_d_openfisca() -> None:
    assert pa.pente_actuelle() == pytest.approx(59.85)
    assert pa.mois_derniere_modification() == 4


def test_calage_sur_le_chiffrage_officiel() -> None:
    assert pa.rendement_un_point_officiel() == pytest.approx(0.5 / 1.15)
    f = pa.cout_un_point()
    assert f.bas < f.central == f.haut


def test_levier_dans_le_scenario() -> None:
    r = rendement_unitaire(LEVIER_PA_PENTE)
    assert r.bas < r.haut < 0
    assert bornes_levier(LEVIER_PA_PENTE) == (-5.0, 5.0)
    assert levier_registre(LEVIER_PA_PENTE) == "minima_prime_activite"
    assert scenario([Mesure(LEVIER_PA_PENTE, -1.0, 2027)])[-1].ecart_dette.central < 0


def test_combinaison_avec_la_mission_solidarite_refusee() -> None:
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [
                Mesure(LEVIER_PA_PENTE, -1.0, 2027),
                Mesure(levier_credits_mission(MISSION_SOLIDARITE), -5.0, 2027),
            ]
        )
