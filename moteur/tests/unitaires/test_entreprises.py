"""Tests de la répartition des effets des leviers entre entreprises (fr_budget.entreprises)."""

from __future__ import annotations

import pytest

from fr_budget import scenario
from fr_budget.entreprises import repartition as r
from fr_budget.fourchette import Fourchette


@pytest.mark.parametrize("levier", r.LEVIERS_ENTREPRISES)
@pytest.mark.parametrize("nomenclature", [r.TAILLE, r.SECTEUR])
def test_parts_et_total_national(levier: str, nomenclature: str) -> None:
    """Les parts centrales somment à un et les effets centraux redonnent l'effet national."""
    effets = r.effet_unitaire(levier, nomenclature)
    if not effets:
        assert levier == scenario.LEVIER_IS_SURTAXE
        assert nomenclature == r.SECTEUR
        return
    assert sum(c.part.central for c, _ in effets) == pytest.approx(1.0)
    national = scenario.rendement_unitaire(levier).central
    assert sum(f.central for _, f in effets) == pytest.approx(national)
    for classe, f in effets:
        assert classe.part.bas <= classe.part.central <= classe.part.haut
        assert f.bas <= f.central <= f.haut


def test_surtaxe_aux_grandes_entreprises() -> None:
    effets = {c.id: f for c, f in r.effet_unitaire(scenario.LEVIER_IS_SURTAXE, r.TAILLE)}
    assert effets[r.GRANDES].central == pytest.approx(
        scenario.rendement_unitaire(scenario.LEVIER_IS_SURTAXE).central
    )
    assert all(f.central == 0 for k, f in effets.items() if k != r.GRANDES)


def test_allegements_baissent_la_charge() -> None:
    """Allègements accrus : la charge des entreprises baisse dans chaque classe."""
    assert all(f.haut < 0 for _, f in r.effet_unitaire(scenario.LEVIER_ALLEGEMENTS, r.TAILLE))


def test_produit_de_fourchettes() -> None:
    assert r.produit(Fourchette(-2, -1, 1), Fourchette(0.1, 0.2, 0.3)) == Fourchette(
        -0.6, -0.2, 0.3
    )


def test_levier_sans_repartition() -> None:
    with pytest.raises(ValueError, match="pas de répartition"):
        r.classes(scenario.LEVIER_TVA_NORMAL, r.TAILLE)


def test_memes_secteurs_les_deux_annees() -> None:
    """Les parts de l'impôt par secteur combinent 2025 et 2024 : mêmes secteurs les deux années."""
    classes = r.classes(scenario.LEVIER_IS_TAUX_NORMAL, r.SECTEUR)
    assert len(classes) == 10
