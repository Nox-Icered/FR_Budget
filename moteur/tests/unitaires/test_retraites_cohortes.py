"""Tests du modèle de retraites par cohortes (fr_budget.retraites_cohortes)."""

from __future__ import annotations

import pytest

from fr_budget import retraites_cohortes as rc
from fr_budget import scenario

ENTREE = 2027


def test_taux_interpole_et_borne() -> None:
    ages, taux = rc.taux_retraites()
    assert rc.taux(ages[0] - 5) == 0
    assert rc.taux(ages[-1] + 10) == pytest.approx(taux[-1])
    milieu = (ages[0] + ages[1]) / 2
    assert rc.taux(milieu) == pytest.approx((taux[0] + taux[1]) / 2)


def test_premiere_generation_atteint_l_age_legal_a_l_entree() -> None:
    g = rc.premiere_generation(ENTREE)
    ouverture = rc.ages_legaux()[g][0]
    assert g + ouverture >= ENTREE
    assert (g - 1) + rc.ages_legaux()[g - 1][0] < ENTREE


def test_decalage_au_rythme_de_la_montee_en_charge() -> None:
    g = rc.premiere_generation(ENTREE)
    assert rc.decalage(1.0, g - 1, ENTREE) == 0
    assert rc.decalage(1.0, g, ENTREE) == pytest.approx(1 / rc.duree_montee_en_charge())
    assert rc.decalage(1.0, g + 10, ENTREE) == pytest.approx(1.0)
    assert rc.decalage(2.0, g, ENTREE) == pytest.approx(2 * rc.decalage(1.0, g, ENTREE))


def test_aucun_effet_avant_l_entree_ni_sans_relevement() -> None:
    assert rc.effet_annee(1.0, ENTREE - 1, ENTREE, "central") == 0
    assert rc.effet_annee(0.0, ENTREE + 5, ENTREE, "central") == 0


def test_relevement_ameliore_le_solde_baisse_le_degrade() -> None:
    hausse = rc.effet(1.0, ENTREE + 9, ENTREE)
    baisse = rc.effet(-1.0, ENTREE + 9, ENTREE)
    assert 0 < hausse.bas <= hausse.central <= hausse.haut
    assert baisse.central < 0


def test_departs_non_decales_reduisent_les_retraites_en_moins() -> None:
    a = rc.retraites_en_moins(1.0, ENTREE + 9, ENTREE, 0.0)
    b = rc.retraites_en_moins(1.0, ENTREE + 9, ENTREE, 0.5)
    assert b == pytest.approx(a / 2)


def test_double_compte_des_deux_leviers_retraites() -> None:
    mesures = [
        scenario.Mesure(scenario.LEVIER_RETRAITES_AGE, 1.0, ENTREE),
        scenario.Mesure(scenario.LEVIER_RETRAITES_AGE_LEGAL, 1.0, ENTREE),
    ]
    with pytest.raises(ValueError, match="double compte"):
        scenario.verifier_double_compte(mesures)


def test_levier_dans_le_scenario() -> None:
    """L'écart de solde du scénario reprend l'effet du modèle, année par année."""
    lignes = scenario.scenario([scenario.Mesure(scenario.LEVIER_RETRAITES_AGE_LEGAL, 1.0, ENTREE)])
    par_annee = {ligne.annee: ligne for ligne in lignes}
    attendu = rc.effet(1.0, ENTREE + 3, ENTREE).central
    assert par_annee[ENTREE + 3].ecart_solde_primaire.central == pytest.approx(attendu, abs=1e-9)
