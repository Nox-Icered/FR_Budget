"""Tests des leviers « crédits par mission » dans le scénario (lot 2.5)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.credits_missions import mission
from fr_budget.baseline import resf
from fr_budget.registres.acces import hypothese
from fr_budget.scenario import (
    LEVIER_CREDITS_UNITE,
    Mesure,
    bornes_levier,
    levier_credits_mission,
    provenance,
    rendement_unitaire,
    scenario,
)

IDENT = "justice"


def _deflateur_2026() -> float:
    return 1 + resf()[(2026, "croissance_nominale")] / 100


def test_un_pourcent_de_hausse_degrade_le_solde() -> None:
    """+1 % des crédits : -1 % des crédits du PLF 2026, en Md€ de 2025, plage d'exécution."""
    attendu = -mission(IDENT).credits / 1e9 / 100 / _deflateur_2026()
    r = rendement_unitaire(levier_credits_mission(IDENT))
    plage = hypothese("credits_missions_ecart_execution").plage
    assert r.central == pytest.approx(attendu)
    assert r.bas == pytest.approx(attendu * (1 + plage.haute))
    assert r.haut == pytest.approx(attendu * (1 + plage.basse))


def test_baisse_reduit_la_dette() -> None:
    lignes = scenario([Mesure(levier_credits_mission(IDENT), -10.0, 2027)])
    assert lignes[-1].ecart_dette.central < 0


def test_bornes() -> None:
    assert bornes_levier(levier_credits_mission(IDENT)) == (-20.0, 20.0)
    with pytest.raises(ValueError, match="bornes"):
        scenario([Mesure(levier_credits_mission(IDENT), -25.0, 2027)])


def test_mission_hors_levier_refusee() -> None:
    with pytest.raises(ValueError, match="levier inconnu"):
        scenario(
            [Mesure("credits_mission_relations_avec_les_collectivites_territoriales", 1.0, 2027)]
        )


def test_unite_generique_du_site() -> None:
    """x % d'une mission = x * (crédits / 100) Md€ de 2025 sur le levier générique."""
    levier = levier_credits_mission(IDENT)
    md = -5.0 * rendement_unitaire(levier).central
    a = scenario([Mesure(levier, -5.0, 2028)])
    b = scenario([Mesure(LEVIER_CREDITS_UNITE, -md, 2028)])
    for x, y in zip(a, b, strict=True):
        assert x.ecart_dette.central == pytest.approx(y.ecart_dette.central)
        assert x.ecart_dette.bas == pytest.approx(y.ecart_dette.bas)
        assert x.ecart_dette.haut == pytest.approx(y.ecart_dette.haut)


def test_double_compte_refuse() -> None:
    levier = levier_credits_mission(IDENT)
    with pytest.raises(ValueError, match="double compte"):
        scenario([Mesure(levier, -5.0, 2027), Mesure(levier, -5.0, 2028)])
    with pytest.raises(ValueError, match="double compte"):
        scenario([Mesure(LEVIER_CREDITS_UNITE, -1.0, 2027), Mesure(levier, -5.0, 2027)])
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [Mesure(LEVIER_CREDITS_UNITE, -1.0, 2027), Mesure(LEVIER_CREDITS_UNITE, -2.0, 2027)]
        )
    # Une hausse et une baisse (deux missions) passent par deux mesures génériques de signes
    # opposés : admis.
    scenario([Mesure(LEVIER_CREDITS_UNITE, -1.0, 2027), Mesure(LEVIER_CREDITS_UNITE, 2.0, 2027)])


def test_provenance() -> None:
    sources, hypotheses = provenance([levier_credits_mission(IDENT)])
    assert {"db_budget_vert_plf2026", "dgfip_plrg_2025"} <= set(sources)
    assert "credits_missions_ecart_execution" in hypotheses
