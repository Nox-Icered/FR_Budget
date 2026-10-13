"""Tests des ménages types (fr_budget.menages.types)."""

from __future__ import annotations

import pytest

from fr_budget.menages import types as t
from fr_budget.menages.openfisca import smic_mensuel_brut
from fr_budget.registres.acces import chiffrage


def test_smic_au_smic_brut() -> None:
    assert t.brut_mensuel(t.SMIC) == pytest.approx(smic_mensuel_brut("2025-06"))


def test_brut_redonne_le_net_vise() -> None:
    net = 2000.0
    brut = t.brut_pour_net(net, "2025-06")
    assert t._salaire_net_mensuel(brut, "2025-06") == pytest.approx(net, abs=0.01)


def test_niveaux_ordonnes_et_rapport_a_l_insee() -> None:
    smic, median, p95 = (t.brut_mensuel(n) for n in (t.SMIC, t.MEDIAN, t.P95))
    assert smic < median < p95
    # Le rapport médiane / 95e centile de l'Insee se retrouve à peu près en brut.
    attendu = chiffrage("insee_salaire_net_p95_2024") / chiffrage("insee_salaire_net_median_2024")
    assert p95 / median == pytest.approx(attendu, rel=0.05)


@pytest.mark.parametrize("identifiant", t.PROFILS)
def test_cascade_ordonnee(identifiant: str) -> None:
    c = t.cascade_annuelle(identifiant)
    if t.PROFILS[identifiant].adultes[0].independant:
        # Indépendant : pas de salaire, revenu brut puis net de cotisations et contributions.
        assert c.salaire_brut == 0
        assert c.revenu_independant_brut > c.revenu_independant_net > 0
        assert c.impot_revenu >= 0
        return
    if t.PROFILS[identifiant].adultes[0].retraite:
        # Retraité : pas de salaire, pension brute puis nette.
        assert c.salaire_brut == 0
        assert c.pension_brute >= c.pension_nette > 0
        assert c.impot_revenu >= 0
        return
    # Égalité possible du brut et du net : apprenti exonéré de cotisations, de CSG et de CRDS.
    assert c.cout_employeur >= c.salaire_brut >= c.net_avant_impot > 0
    assert c.impot_revenu >= 0
    assert c.net_apres_impot == pytest.approx(
        c.net_avant_impot - c.impot_revenu + sum(c.prestations.values())
    )


def test_apprenti_exonere() -> None:
    """Contrat conclu avant le 1er mars 2025, salaire sous 79 % du SMIC : net égal au brut,
    salaire entièrement exonéré d'impôt (fiche F2918 de service-public.gouv.fr)."""
    c = t.cascade_annuelle("apprenti_19_ans")
    assert c.net_avant_impot == pytest.approx(c.salaire_brut)
    assert c.net_imposable == 0
    assert t.declaration("apprenti_19_ans")["1AJ"] == 0


def test_salaire_apprenti_par_annee_de_contrat() -> None:
    contrat = t.PROFILS["apprenti_19_ans"].adultes[0].apprentissage
    assert contrat is not None
    assert t.salaire_apprenti(contrat, "2024-08") == 0
    premiere = t.salaire_apprenti(contrat, "2025-08") / smic_mensuel_brut("2025-08")
    deuxieme = t.salaire_apprenti(contrat, "2025-09") / smic_mensuel_brut("2025-09")
    assert premiere == pytest.approx(0.43)
    assert deuxieme == pytest.approx(0.51)
    troisieme = t.salaire_apprenti(contrat, "2026-09") / smic_mensuel_brut("2026-09")
    assert troisieme == pytest.approx(0.67)
    with pytest.raises(ValueError):
        t.salaire_apprenti(contrat, "2027-09")


def test_declaration_du_couple() -> None:
    d = t.declaration("couple_2_enfants")
    assert d["situation"] == "M"
    assert d["0CF"] == 2
    assert d["1AJ"] > d["1BJ"] > 0


def test_case_t_du_parent_isole() -> None:
    assert t.declaration("parent_isole_1_enfant")["0BT"] is True
    assert "0BT" not in t.declaration("celibataire_smic")


def test_pension_revalorisee_comme_les_pensions_de_base() -> None:
    attendu = 1666 * 1.053 * 1.022
    assert t.pension_brute_mensuelle(2025) == pytest.approx(attendu)
    assert t.pension_brute_mensuelle(2023) == pytest.approx(1666)
    with pytest.raises(ValueError):
        t.pension_brute_mensuelle(2022)
    with pytest.raises(ValueError):
        t.pension_brute_mensuelle(2026)


def test_csg_du_retraite_independante_de_l_ordre_des_calculs() -> None:
    variables = [("retraite_nette", "2025-06"), ("csg_deductible_retraite", "2025-06")]
    variables += [("retraite_imposable", "2025-06"), ("rfr", "2025")]
    resultats = []
    for ordre in (variables, list(reversed(variables))):
        simulation = t._simulation("retraite_seul", 2025)
        resultats.append({v + p: float(simulation.calculate(v, p)[0]) for v, p in ordre})
    assert resultats[0] == resultats[1]
    r = resultats[0]
    assert r["retraite_imposable2025-06"] == pytest.approx(
        t.pension_brute_mensuelle(2025) + r["csg_deductible_retraite2025-06"]
    )
    assert r["csg_deductible_retraite2025-06"] < 0
