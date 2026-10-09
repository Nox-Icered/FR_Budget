"""Tests des leviers « dotations aux collectivités » dans le scénario (lot 2.6)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.dotations import COMPENSATIONS, DGF, montant_levier, taux_repercussion
from fr_budget.baseline import resf
from fr_budget.scenario import (
    LEVIER_DOTATIONS_COMPENSATIONS,
    LEVIER_DOTATIONS_DGF,
    Mesure,
    bornes_levier,
    effet_etat_unitaire,
    provenance,
    rendement_unitaire,
    scenario,
)


def _vers_2025(montant: float) -> float:
    return montant / (1 + resf()[(2026, "croissance_nominale")] / 100)


@pytest.mark.parametrize(
    ("levier", "dotation"),
    [(LEVIER_DOTATIONS_DGF, DGF), (LEVIER_DOTATIONS_COMPENSATIONS, COMPENSATIONS)],
)
def test_effet_d_un_pourcent(levier: str, dotation: str) -> None:
    """+1 % : l'État dépense 1 % de plus ; le solde public baisse de la part réinvestie."""
    un_pourcent = _vers_2025(montant_levier(dotation) / 100)
    t = taux_repercussion(dotation)
    r = rendement_unitaire(levier)
    assert r.central == pytest.approx(-t.central * un_pourcent)
    assert r.bas == pytest.approx(-t.haut * un_pourcent)
    assert r.haut == pytest.approx(-t.bas * un_pourcent)
    assert effet_etat_unitaire(levier) == pytest.approx(-un_pourcent)
    assert bornes_levier(levier) == (-10.0, 10.0)


def test_baisse_reduit_la_dette() -> None:
    lignes = scenario([Mesure(LEVIER_DOTATIONS_DGF, -5.0, 2027)])
    assert lignes[-1].ecart_dette.central < 0


def test_provenance() -> None:
    sources, hypotheses = provenance([LEVIER_DOTATIONS_DGF])
    assert {"plf2026_voies_et_moyens_tome1", "cdc_eclairages_8_dotations_investissement"} <= set(
        sources
    )
    assert "dotations_elasticite_investissement_communes" in hypotheses
