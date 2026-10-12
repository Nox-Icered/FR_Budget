"""Tests des leviers « rémunérations publiques » dans le scénario (lot 2.7)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.remunerations import (
    EFFECTIFS,
    POINT,
    cout_brut_un_pourcent,
    cout_net_un_pourcent,
)
from fr_budget.scenario import (
    LEVIER_EFFECTIFS,
    LEVIER_POINT_INDICE,
    Mesure,
    bornes_levier,
    effet_brut_unitaire,
    levier_credits_mission,
    rendement_unitaire,
    scenario,
)


@pytest.mark.parametrize(
    ("levier", "assiette"), [(LEVIER_POINT_INDICE, POINT), (LEVIER_EFFECTIFS, EFFECTIFS)]
)
def test_effet_d_un_pourcent(levier: str, assiette: str) -> None:
    net = cout_net_un_pourcent(assiette)
    r = rendement_unitaire(levier)
    assert r.central == pytest.approx(-net.central)
    assert r.bas == pytest.approx(-net.haut)
    assert r.haut == pytest.approx(-net.bas)
    assert effet_brut_unitaire(levier) == pytest.approx(-cout_brut_un_pourcent(assiette))
    assert effet_brut_unitaire(levier) < r.bas
    assert bornes_levier(levier) == (-5.0, 5.0)


def test_baisse_reduit_la_dette() -> None:
    assert scenario([Mesure(LEVIER_EFFECTIFS, -2.0, 2027)])[-1].ecart_dette.central < 0


def test_combinaison_avec_les_missions_refusee() -> None:
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [
                Mesure(LEVIER_POINT_INDICE, 1.0, 2027),
                Mesure(levier_credits_mission("justice"), -5.0, 2027),
            ]
        )
