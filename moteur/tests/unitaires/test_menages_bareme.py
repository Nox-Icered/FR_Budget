"""Effet d'un barème saisi sur les ménages types (fr_budget.menages.bareme)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.bareme_ir import BAREMES_CONTROLE, bareme_openfisca
from fr_budget.menages import bareme as mb
from fr_budget.menages import types as t


def test_reference_sans_ecart() -> None:
    reference = bareme_openfisca(t.ANNEE)
    for ident in t.PROFILS:
        assert mb.ecart_menage(reference, ident) == 0.0


def test_impot_de_reference_redonne_la_cascade() -> None:
    """Le calcul du site redonne l'impôt d'OpenFisca avec le barème de référence."""
    reference = bareme_openfisca(t.ANNEE)
    for ident in t.PROFILS:
        calcule = sum(mb.impot_foyer(reference, f) for f in mb.foyers(ident))
        assert calcule == pytest.approx(t.cascade_annuelle(ident).impot_revenu, abs=1.0), ident


@pytest.mark.parametrize(("nom", "construire"), BAREMES_CONTROLE)
def test_meme_ecart_qu_openfisca(nom: str, construire: object) -> None:
    """Barèmes de contrôle : même écart d'impôt qu'OpenFisca avec le barème réformé, à 1 € près."""
    bareme = construire(bareme_openfisca(t.ANNEE))  # type: ignore[operator]
    for ident in t.PROFILS:
        assert mb.ecart_menage(bareme, ident) == pytest.approx(
            mb.ecart_openfisca(bareme, ident), abs=1.0
        ), (nom, ident)
