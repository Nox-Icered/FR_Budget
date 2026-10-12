"""Tests du levier « indexation des pensions et prestations » dans le scénario (lot 2.8)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.indexation import cout_brut_un_point, cout_un_point
from fr_budget.scenario import (
    LEVIER_INDEXATION,
    MISSION_SOLIDARITE,
    Mesure,
    bornes_levier,
    effet_brut_unitaire,
    facteur_premiere_annee,
    levier_credits_mission,
    levier_registre,
    rendement_unitaire,
    scenario,
)


def test_effet_d_un_point() -> None:
    net = cout_un_point()
    r = rendement_unitaire(LEVIER_INDEXATION)
    assert r.central == pytest.approx(-net.central)
    assert r.bas == pytest.approx(-net.haut)
    assert r.haut == pytest.approx(-net.bas)
    assert effet_brut_unitaire(LEVIER_INDEXATION) == pytest.approx(-cout_brut_un_point())
    assert effet_brut_unitaire(LEVIER_INDEXATION) < r.bas
    assert bornes_levier(LEVIER_INDEXATION) == (-2.0, 1.0)
    assert levier_registre(LEVIER_INDEXATION) == "indexation_pensions_prestations"


def test_sous_indexation_reduit_la_dette() -> None:
    assert scenario([Mesure(LEVIER_INDEXATION, -1.0, 2027)])[-1].ecart_dette.central < 0


def test_hors_bornes_refuse() -> None:
    with pytest.raises(ValueError, match="bornes"):
        scenario([Mesure(LEVIER_INDEXATION, 1.5, 2027)])


def test_combinaison_avec_la_mission_solidarite_refusee() -> None:
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [
                Mesure(LEVIER_INDEXATION, -1.0, 2027),
                Mesure(levier_credits_mission(MISSION_SOLIDARITE), -5.0, 2027),
            ]
        )


def test_combinaison_avec_une_autre_mission_admise() -> None:
    scenario(
        [
            Mesure(LEVIER_INDEXATION, -1.0, 2027),
            Mesure(levier_credits_mission("justice"), -5.0, 2027),
        ]
    )


def test_premiere_annee_partielle() -> None:
    """Les prestations revalorisées en avril ne comptent que neuf mois la première année."""
    assert 0.9 < facteur_premiere_annee(LEVIER_INDEXATION) < 1.0
    lignes = {a.annee: a for a in scenario([Mesure(LEVIER_INDEXATION, -1.0, 2027)])}
    premiere = lignes[2027].ecart_solde_primaire.central
    suivante = lignes[2028].ecart_solde_primaire.central
    assert 0 < premiere < suivante


def test_mesure_a_zero_ne_bloque_pas() -> None:
    scenario(
        [
            Mesure(LEVIER_INDEXATION, 0.0, 2027),
            Mesure(levier_credits_mission(MISSION_SOLIDARITE), -5.0, 2027),
        ]
    )
