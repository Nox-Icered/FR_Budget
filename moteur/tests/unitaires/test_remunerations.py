"""Tests des rémunérations publiques (lot 2.7) : assiette, part indiciaire, part nette."""

from __future__ import annotations

import pytest

from fr_budget.agrege.remunerations import (
    CATEGORIES,
    EFFECTIFS,
    ENSEMBLE,
    POINT,
    VERSANTS,
    cout_brut_point,
    cout_brut_un_pourcent,
    cout_net_un_pourcent,
    masse,
    part_indiciaire,
    part_restant_a_l_agent,
    traitement_et_primes,
)
from fr_budget.apu import comptes_apu


def test_masse_hors_cotisations_imputees() -> None:
    c = comptes_apu()
    for versant, secteur in VERSANTS.items():
        d1 = c.valeur(2025, secteur, "remuneration_salaries")
        d122 = c.valeur(2025, secteur, "cotisations_sociales_imputees")
        assert masse(versant) == pytest.approx(d1 - d122)
        assert 0 < d122 < d1


def test_part_indiciaire_figure_9() -> None:
    """FPE : 2 894 euros de traitement sur 3 845 euros de salaire brut (DGAFP, figure 9)."""
    assert part_indiciaire("fpe") == pytest.approx(2894 / 3845)
    for versant in VERSANTS:
        assert 0.5 < part_indiciaire(versant) < 1


def test_cout_brut_proportionnel() -> None:
    for versant in VERSANTS:
        assert cout_brut_point(versant, 0.02) == pytest.approx(2 * cout_brut_point(versant, 0.01))
    assert cout_brut_un_pourcent(POINT) == pytest.approx(
        sum(cout_brut_point(v, 0.01) for v in VERSANTS)
    )


def test_part_restant_a_l_agent_entre_zero_et_un() -> None:
    for versant in VERSANTS:
        for categorie in (ENSEMBLE, *CATEGORIES):
            traitement_et_primes(versant, categorie)
            for assiette in (POINT, EFFECTIFS):
                assert 0 < part_restant_a_l_agent(versant, categorie, assiette) < 1


def test_cout_net_inferieur_au_brut() -> None:
    for levier in (POINT, EFFECTIFS):
        net = cout_net_un_pourcent(levier)
        assert 0 < net.bas <= net.central <= net.haut < cout_brut_un_pourcent(levier)
