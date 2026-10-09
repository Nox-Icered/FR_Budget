"""Tests des dotations aux collectivités (lot 2.6) : extraction, répartition, répercussion."""

from __future__ import annotations

import pytest

from fr_budget.agrege.dotations import (
    COMPENSATIONS,
    DGF,
    NIVEAUX,
    execution,
    montant_levier,
    montant_psr,
    parts,
    ratio_investissement,
    taux_repercussion,
    total_publie,
)
from fr_budget.registres.acces import chiffrage

ARRONDI_MD = 3e-6  # 3 k€ : écart d'arrondi entre la somme des lignes et le total publié.
COLONNES = ("execution", "lfi", "revise", "plf")


@pytest.mark.parametrize("plf", [2024, 2025, 2026])
def test_somme_des_lignes_egale_au_total_publie(plf: int) -> None:
    from fr_budget.agrege.dotations import _psr

    codes = tuple({r["code"] for r in _psr() if r["code"] != "total"})
    for colonne in COLONNES:
        assert montant_psr(plf, colonne, codes) == pytest.approx(
            total_publie(plf, colonne), abs=ARRONDI_MD
        )


def test_montants_2026_du_levier() -> None:
    """DGF 2026 = DGF répartie en 2025 plus les fractions de TVA des régions réintégrées."""
    assert montant_levier(DGF) == pytest.approx(32.578368)
    reintegre = chiffrage("dotations_dgf_regions_reintegree_2026") / 1000
    assert montant_levier(DGF) - montant_psr(2026, "lfi", ("3101",)) == pytest.approx(
        reintegre, abs=0.02
    )
    assert 0 < montant_levier(COMPENSATIONS) < montant_levier(DGF)


def test_parts_et_ratios() -> None:
    for dotation in (DGF, COMPENSATIONS):
        assert sum(parts(dotation).values()) == pytest.approx(1.0)
    for n in NIVEAUX:
        assert ratio_investissement(n) > 0


def test_taux_de_repercussion_ordonne_et_borne() -> None:
    for dotation in (DGF, COMPENSATIONS):
        t = taux_repercussion(dotation)
        assert 0 < t.bas <= t.central <= t.haut <= 1


@pytest.mark.parametrize(
    ("dotation", "annee", "identifiant"),
    [
        (DGF, 2023, "dotations_dgf_execution_2023"),
        (DGF, 2024, "dotations_dgf_execution_2024"),
        (COMPENSATIONS, 2023, "dotations_compensations_execution_2023"),
        (COMPENSATIONS, 2024, "dotations_compensations_execution_2024"),
    ],
)
def test_executions_saisies_egales_aux_donnees(dotation: str, annee: int, identifiant: str) -> None:
    assert chiffrage(identifiant) / 1000 == pytest.approx(
        execution(dotation, annee).execution, abs=1e-6
    )
