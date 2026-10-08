"""Cas analytiques de la dynamique de la dette (lot 1.2 du plan).

Formule (CLAUDE.md) : d(t+1) = d(t) * (1 + r) / (1 + g) - pb + sfa, en ratio de PIB.
"""

import pytest

from fr_budget.dette import (
    ajustement_stock_flux_implicite,
    dette_suivante,
    part_refinancee,
    solde_primaire_stabilisant,
    surcout_choc_taux,
    taux_apparent_suivant,
    trajectoire_dette,
)


def test_dette_stable_quand_r_egale_g_sans_solde_primaire() -> None:
    assert dette_suivante(1.1, 0.03, 0.03, 0.0) == pytest.approx(1.1)


def test_effet_boule_de_neige_quand_r_superieur_a_g() -> None:
    assert dette_suivante(1.0, 0.04, 0.02, 0.0) == pytest.approx(1.04 / 1.02)


def test_excedent_primaire_et_ajustement_stock_flux() -> None:
    # Un excédent primaire de 1 point réduit la dette d'1 point ; un ajustement de 0,5 l'augmente.
    assert dette_suivante(1.0, 0.03, 0.03, 0.01, 0.005) == pytest.approx(0.995)


def test_solde_primaire_stabilisant() -> None:
    d, r, g = 1.15, 0.025, 0.03
    pb = solde_primaire_stabilisant(d, r, g)
    assert pb == pytest.approx(d * (r - g) / (1 + g))
    assert dette_suivante(d, r, g, pb) == pytest.approx(d)


def test_trajectoire_sur_plusieurs_annees() -> None:
    trajectoire = trajectoire_dette(1.0, [0.04] * 3, [0.02] * 3, [0.0] * 3)
    assert trajectoire == pytest.approx(
        [1.0, (1.04 / 1.02), (1.04 / 1.02) ** 2, (1.04 / 1.02) ** 3]
    )


def test_trajectoire_refuse_des_series_de_longueurs_differentes() -> None:
    with pytest.raises(ValueError, match="longueur"):
        trajectoire_dette(1.0, [0.04] * 3, [0.02] * 2, [0.0] * 3)


def test_taux_apparent_cas_limites() -> None:
    # Rien n'est refinancé : le taux apparent ne bouge pas ; tout l'est : il rejoint le marché.
    assert taux_apparent_suivant(0.02, 0.035, 0.0) == pytest.approx(0.02)
    assert taux_apparent_suivant(0.02, 0.035, 1.0) == pytest.approx(0.035)


def test_taux_apparent_converge_geometriquement_vers_le_taux_de_marche() -> None:
    r, i, s = 0.02, 0.035, 0.12
    for _ in range(10):
        r = taux_apparent_suivant(r, i, s)
    assert r == pytest.approx(i + (0.02 - i) * (1 - s) ** 10)


def test_part_refinancee_hors_bornes_refusee() -> None:
    with pytest.raises(ValueError, match="part"):
        taux_apparent_suivant(0.02, 0.035, 1.2)


def test_ajustement_stock_flux_implicite_referme_la_formule() -> None:
    d0, r, g, pb = 1.1, 0.025, 0.03, -0.02
    sfa = ajustement_stock_flux_implicite(d0, 1.14, r, g, pb)
    assert dette_suivante(d0, r, g, pb, sfa) == pytest.approx(1.14)


def test_part_refinancee() -> None:
    # 300 émis à moyen et long terme, 200 de titres courts renouvelés, +10 de titres courts,
    # sur un encours de 2 550.
    assert part_refinancee(300.0, 200.0, 10.0, 2550.0) == pytest.approx(0.2)


def test_surcout_d_un_choc_de_taux() -> None:
    # Choc de 1 point, 20 % refinancés par an, encours 1 000.
    assert surcout_choc_taux(1000.0, 0.2, 0.01, 1, 1.0) == pytest.approx(2.0)
    assert surcout_choc_taux(1000.0, 0.2, 0.01, 1, 0.5) == pytest.approx(10 * (1 - 0.8**0.5))
    assert surcout_choc_taux(1000.0, 0.2, 0.01, 5, 1.0) == pytest.approx(10 * (1 - 0.8**5))
