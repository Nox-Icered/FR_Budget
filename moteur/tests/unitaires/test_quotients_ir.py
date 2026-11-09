"""Impôt sur le revenu, structure : effet du quotient familial et du quotient conjugal
(fr_budget.agrege.quotients_ir)."""

from __future__ import annotations

import pytest

from fr_budget import scenario as sc
from fr_budget.agrege import quotients_ir as q
from fr_budget.agrege.indexation import facteur_pib
from fr_budget.registres.acces import chiffrage

ENTREE = 2027


def test_effets_de_2017_lus_dans_le_tableau_de_l_insee() -> None:
    assert q.effet_qf_2017() == pytest.approx(16.6)
    assert q.effet_qc_2017() == pytest.approx(11.1)
    total = chiffrage("ir_insee_impot_individuel_2017") - chiffrage("ir_insee_impot_reel_2017")
    assert q.effet_qf_2017() + q.effet_qc_2017() == pytest.approx(total)


def test_un_pour_cent_vaut_un_centieme_de_l_effet_porte_en_2025() -> None:
    f = q.rendement_point_qf()
    k = facteur_pib(2025) / facteur_pib(2017)
    assert f.central == pytest.approx(q.effet_qf_2017() * k / 100)
    assert 0 < f.bas <= f.central <= f.haut
    g = q.rendement_point_qc()
    assert g.central == pytest.approx(q.effet_qc_2017() * k / 100)
    ofce = chiffrage("ir_ofce_individualisation_optimisation_2016")
    assert g.bas == pytest.approx(ofce * facteur_pib(2025) / facteur_pib(2016) / 100)
    assert 0 < g.bas <= g.central <= g.haut


def test_leviers_dans_le_scenario() -> None:
    for levier in q.LEVIERS:
        assert sc.levier_registre(levier) == "impot_revenu_structure"
        assert sc.bornes_levier(levier) == (0.0, 100.0)
        assert sc.effet_solde(sc.Mesure(levier, 1.0, ENTREE)).central > 0
        assert sc.taux_reference(levier) == pytest.approx(
            100 * sc.rendement_unitaire(levier).central
        )


def test_plafond_et_effet_du_quotient_familial_refuses_ensemble() -> None:
    with pytest.raises(ValueError, match="double compte"):
        sc.verifier_double_compte(
            [sc.Mesure(sc.LEVIER_IR_QF, -10.0, ENTREE), sc.Mesure(q.LEVIER_QF, 50.0, ENTREE)]
        )
    sc.verifier_double_compte(
        [sc.Mesure(q.LEVIER_QF, 100.0, ENTREE), sc.Mesure(q.LEVIER_QC, 100.0, ENTREE)]
    )


def test_recoupement_par_le_moteur_du_bareme_positif() -> None:
    """Le recoupement est calculé (écart publié dans la fiche, pas une référence)."""
    assert q.recoupement_bareme_qf() > 0
