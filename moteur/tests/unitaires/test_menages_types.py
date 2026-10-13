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
