"""Tests des leviers « dépenses fiscales » dans le scénario (lot 2.4)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.depenses_fiscales import cout_impot_levier, depense
from fr_budget.baseline import resf
from fr_budget.registres.acces import hypothese
from fr_budget.scenario import (
    LEVIER_DEPENSE_FISCALE_UNITE,
    Mesure,
    bornes_levier,
    levier_depense_fiscale,
    levier_depenses_fiscales_impot,
    provenance,
    rendement_unitaire,
    scenario,
)

CODE = "110201"  # Réduction d'impôt au titre des dons (impôt sur le revenu).


def _deflateur_2026() -> float:
    """Coût 2026 ramené en euros de 2025 par la croissance nominale 2026 du RESF 2027."""
    return 1 + resf()[(2026, "croissance_nominale")] / 100


def test_rendement_d_un_pourcent_d_une_depense() -> None:
    """1 % du coût prévu pour 2026, en Md€ de 2025, plage de l'écart de prévision."""
    levier = levier_depense_fiscale(CODE)
    attendu = depense(CODE).cout / 1000 / 100 / _deflateur_2026()
    r = rendement_unitaire(levier)
    plage = hypothese("depenses_fiscales_ecart_depense").plage
    assert r.central == pytest.approx(attendu)
    assert r.bas == pytest.approx(attendu * (1 + plage.basse))
    assert r.haut == pytest.approx(attendu * (1 + plage.haute))
    assert bornes_levier(levier) == (0.0, 100.0)


def test_rendement_d_un_pourcent_par_impot() -> None:
    levier = levier_depenses_fiscales_impot("impot_revenu")
    attendu = cout_impot_levier("impot_revenu") / 1000 / 100 / _deflateur_2026()
    r = rendement_unitaire(levier)
    plage = hypothese("depenses_fiscales_ecart_impot_revenu").plage
    assert r.central == pytest.approx(attendu)
    assert r.haut == pytest.approx(attendu * (1 + plage.haute))
    assert bornes_levier(levier) == (0.0, 100.0)


def test_unite_generique_du_site() -> None:
    """Le site traduit x % d'une dépense en x * rendement Md€ du levier générique."""
    levier = levier_depense_fiscale(CODE)
    md = 50 * rendement_unitaire(levier).central
    a = scenario([Mesure(levier, 50.0, 2027)])
    b = scenario([Mesure(LEVIER_DEPENSE_FISCALE_UNITE, md, 2027)])
    for x, y in zip(a, b, strict=True):
        assert x.ecart_dette.central == pytest.approx(y.ecart_dette.central)
        assert x.ecart_dette.bas == pytest.approx(y.ecart_dette.bas)
        assert x.ecart_dette.haut == pytest.approx(y.ecart_dette.haut)


def test_suppression_reduit_la_dette() -> None:
    lignes = scenario([Mesure(levier_depense_fiscale(CODE), 100.0, 2027)])
    assert lignes[-1].ecart_dette.central < 0


def test_double_compte_refuse() -> None:
    """Une dépense et l'ensemble de son impôt, ou deux fois la même dépense : refusés."""
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [
                Mesure(levier_depense_fiscale(CODE), 10.0, 2027),
                Mesure(levier_depenses_fiscales_impot("impot_revenu"), 10.0, 2027),
            ]
        )
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [
                Mesure(levier_depense_fiscale(CODE), 10.0, 2027),
                Mesure(levier_depense_fiscale(CODE), 10.0, 2028),
            ]
        )


def test_depense_hors_levier_refusee() -> None:
    with pytest.raises(ValueError, match="levier inconnu"):
        scenario([Mesure("depense_fiscale_800221", 10.0, 2027)])
    with pytest.raises(ValueError, match="levier inconnu"):
        scenario([Mesure("depenses_fiscales_tva", 10.0, 2027)])
    with pytest.raises(ValueError, match="bornes"):
        scenario([Mesure(levier_depense_fiscale(CODE), 120.0, 2027)])


def test_provenance() -> None:
    sources, hypotheses = provenance([levier_depense_fiscale(CODE)])
    assert "plf2026_voies_et_moyens_tome2" in sources
    assert "depenses_fiscales_ecart_depense" in hypotheses
    _, hypotheses = provenance([levier_depenses_fiscales_impot("impots_locaux")])
    assert "depenses_fiscales_ecart_impots_locaux" in hypotheses


def test_unite_generique_une_seule_fois_et_sans_depense_choisie() -> None:
    """Le levier générique (une somme de dépenses choisies sur le site) ne peut figurer qu'une
    fois, et pas avec une dépense désignée par son numéro."""
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [
                Mesure(LEVIER_DEPENSE_FISCALE_UNITE, 1.0, 2027),
                Mesure(LEVIER_DEPENSE_FISCALE_UNITE, 1.0, 2028),
            ]
        )
    with pytest.raises(ValueError, match="double compte"):
        scenario(
            [
                Mesure(LEVIER_DEPENSE_FISCALE_UNITE, 1.0, 2027),
                Mesure(levier_depense_fiscale(CODE), 10.0, 2027),
            ]
        )
