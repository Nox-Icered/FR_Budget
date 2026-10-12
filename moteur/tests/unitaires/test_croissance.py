"""Tests de l'effet de croissance (fr_budget.croissance), cas construits à la main."""

from __future__ import annotations

import pytest

from fr_budget import croissance as cr
from fr_budget.baseline import AnneeBaseline
from fr_budget.registres.acces import chiffrage, hypothese

ANNEES = [2026, 2027, 2028, 2029]


def _plate() -> list[AnneeBaseline]:
    """Dette de 100 % du PIB, taux et croissance nuls, solde primaire nul."""
    return [AnneeBaseline(a, 100.0, 0.0, 0.0, 0.0, 0.0) for a in ANNEES]


def test_impulsion_d_une_mesure_permanente() -> None:
    effets = {2027: 1.0, 2028: 1.0, 2029: 1.0}
    assert cr.impulsions(effets, ANNEES) == [0.0, -1.0, 0.0, 0.0]


def test_impulsion_d_une_montee_en_charge() -> None:
    effets = {2027: 0.75, 2028: 1.0, 2029: 1.0}
    assert cr.impulsions(effets, ANNEES) == pytest.approx([0.0, -0.75, -0.25, 0.0])


def test_ecart_de_production_decroit() -> None:
    og = cr.ecart_production({2027: 1.0, 2028: 1.0, 2029: 1.0}, ANNEES, 0.5, 0.7)
    assert og == pytest.approx([0.0, -0.5, -0.35, -0.245])


def test_trajectoire_calculee_a_la_main() -> None:
    # 2027 : pb = 1 - 0,5 x 0,5 = 0,75 ; dette = 100 - 0,75 + 100 x 0,5 % = 99,75.
    # 2028 : pb = 1 - 0,5 x 0,35 = 0,825 ; dette = 99,75 - 0,825 + 100 x (-0,15 %) = 98,775.
    effets = {2027: 1.0, 2028: 1.0, 2029: 1.0}
    og = [0.0, -0.5, -0.35, -0.245]
    t = cr.trajectoire_avec_croissance(_plate(), effets, og, 0.5)
    assert [a.solde_primaire for a in t[1:3]] == pytest.approx([0.75, 0.825])
    assert [a.dette for a in t[1:3]] == pytest.approx([99.75, 98.775])


def test_sans_ecart_de_production_on_retrouve_l_effet_seul() -> None:
    effets = {2027: 1.0, 2028: 1.0, 2029: 1.0}
    t = cr.trajectoire_avec_croissance(_plate(), effets, [0.0] * 4, 0.5)
    assert [a.dette for a in t] == pytest.approx([100.0, 99.0, 98.0, 97.0])


def test_l_effet_de_croissance_s_eteint_dans_la_dette_par_le_pib() -> None:
    """Une fois l'écart de production refermé, seul subsiste l'effet cumulé sur le solde."""
    annees = list(range(2026, 2080))
    effets = dict.fromkeys(annees[1:], 1.0)
    og = cr.ecart_production(effets, annees, 0.5, 0.7)
    trajectoire = [AnneeBaseline(a, 100.0, 0.0, 0.0, 0.0, 0.0) for a in annees]
    avec = cr.trajectoire_avec_croissance(trajectoire, effets, og, 0.5)
    sans = cr.trajectoire_avec_croissance(trajectoire, effets, [0.0] * len(annees), 0.5)
    perte_solde = 0.5 * sum(-x for x in og)
    assert avec[-1].dette - sans[-1].dette == pytest.approx(perte_solde, abs=1e-6)


@pytest.mark.parametrize("categorie", cr.CATEGORIES)
def test_multiplicateurs_en_fourchette(categorie: str) -> None:
    m = cr.multiplicateur(categorie)
    assert 0 < m.bas <= m.central <= m.haut <= 1


@pytest.mark.parametrize(
    ("categorie", "mesange", "ofce"),
    [
        (cr.DEPENSES, "mesange_pib_1an_depense_generique", "ofce_multiplicateur_depenses"),
        (cr.TVA, "mesange_pib_1an_tva", "ofce_multiplicateur_recettes"),
        (cr.ACCISES, "mesange_pib_1an_taxe_carbone", "ofce_multiplicateur_recettes"),
        (
            cr.COTISATIONS_EMPLOYEURS,
            "mesange_pib_1an_cotisations_employeurs",
            "ofce_multiplicateur_recettes",
        ),
        (cr.CSG, "mesange_pib_1an_csg", "ofce_multiplicateur_recettes"),
        (cr.IMPOT_REVENU, "mesange_pib_1an_impot_revenu", "ofce_multiplicateur_recettes"),
    ],
)
def test_bornes_reprises_des_deux_sources(categorie: str, mesange: str, ofce: str) -> None:
    """Valeur centrale = variante de Mésange ; plage = Mésange et OFCE."""
    m = cr.multiplicateur(categorie)
    assert m.central == chiffrage(mesange)
    assert {m.bas, m.haut} == {chiffrage(mesange), chiffrage(ofce)}


def test_parametres_de_l_ofce() -> None:
    assert cr.persistance() == chiffrage("ofce_persistance_ecart_production")
    assert cr.effet_sur_le_solde() == chiffrage("ofce_effet_ecart_production_solde")
    assert hypothese(cr.HYPOTHESE_PERSISTANCE).plage.basse == cr.persistance()
