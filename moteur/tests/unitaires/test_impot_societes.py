"""Tests unitaires du module de l'impôt sur les sociétés (lot 2.3)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.impot_societes import (
    assiette_surtaxe,
    benefice_imposable,
    is_brut,
    rendement_point_taux_normal,
    taux_is,
)
from fr_budget.registres.acces import chiffrage


def test_taux_openfisca() -> None:
    assert taux_is(2025) == {"normal": 0.25, "reduit": 0.15}


def test_is_brut_somme_des_taux_par_la_base() -> None:
    b = benefice_imposable(2025)
    assert is_brut(2025) == pytest.approx(
        0.25 * b["benefice_imposable_25"] + 0.15 * b["benefice_imposable_15"]
    )


def test_un_point_de_taux_normal() -> None:
    assert rendement_point_taux_normal(2025) == pytest.approx(
        benefice_imposable(2025)["benefice_imposable_25"] / 100
    )


def test_assiette_surtaxe_2025() -> None:
    assert assiette_surtaxe(2025) == pytest.approx(20.4)


def test_chiffrage_officiel_compris_entre_les_deux_taux_de_la_contribution() -> None:
    """Cohérence : 8 Md€ (PLF 2025) et 7,5 Md€ (réalisé) entre 20,6 % et 41,2 % de l'assiette
    2025 publiée par la DGFiP. La répartition entre les deux tranches n'est pas publiée."""
    assiette = assiette_surtaxe(2025)
    basse = chiffrage("is_taux_contribution_exceptionnelle_basse") / 100
    haute = chiffrage("is_taux_contribution_exceptionnelle_haute") / 100
    for reference in (
        "is_contribution_exceptionnelle_2025_plf",
        "is_contribution_exceptionnelle_2025_fipeco",
    ):
        assert basse * assiette <= chiffrage(reference) <= haute * assiette
