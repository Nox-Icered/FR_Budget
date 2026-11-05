"""Plafond du quotient familial (fr_budget.agrege.quotient_familial)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import quotient_familial as qf
from fr_budget.agrege.indexation import facteur_pib
from fr_budget.registres.acces import chiffrage


def test_baisses_historiques_en_pourcentage() -> None:
    """De 2 336 à 2 000 € (-14,4 %), puis de 2 000 à 1 500 € (-25 %)."""
    assert qf.baisse_historique(2013) == pytest.approx(100 * 336 / 2336)
    assert qf.baisse_historique(2014) == pytest.approx(25.0)


def test_valeur_centrale_igf_igas_tenue_en_part_du_pib() -> None:
    """580 M€ pour 10 % en législation 2026, ramenés en Md€ de 2025 par le PIB nominal."""
    attendu = 0.580 / 10 * facteur_pib(2025) / facteur_pib(2026)
    assert qf.rendement_un_pourcent().central == pytest.approx(attendu)


def test_fourchette_encadre_les_chiffrages_transposes() -> None:
    f = qf.rendement_un_pourcent()
    assert f.bas <= f.central <= f.haut
    for annee in (2013, 2014):
        assert f.bas <= qf.rendement_transpose(annee) <= f.haut


def test_hausse_maximale_sous_le_cout_du_deplafonnement() -> None:
    """Relever les plafonds de la borne haute coûte moins que les supprimer (Cour des comptes,
    4,9 Md€ sur les revenus de 2020) : contrôle de vraisemblance de la linéarité."""
    cout_2020 = qf.rendement_un_pourcent().haut * qf.BORNE * facteur_pib(2020) / facteur_pib(2025)
    assert cout_2020 < chiffrage("qf_deplafonnement_ccomptes_2020")


def test_rendement_mesure_proportionnel() -> None:
    a = qf.rendement_baisse(10.0, 2026)
    b = qf.rendement_baisse(20.0, 2026)
    assert b == pytest.approx(2 * a)
    assert qf.rendement_baisse(10.0, 2026) == pytest.approx(0.580)
