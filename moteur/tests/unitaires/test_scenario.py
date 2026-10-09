"""Tests du scénario (lot 2.1) : un levier modifie le solde primaire, la dette suit la formule."""

from __future__ import annotations

import pytest

from fr_budget.agrege.tva import estimer_point_tva
from fr_budget.apu import comptes_apu
from fr_budget.baseline import ANNEE_FIN, baseline, trajectoires
from fr_budget.scenario import (
    LEVIER_TVA_NORMAL,
    Mesure,
    bornes_levier,
    effet_solde,
    reponse_unitaire,
    scenario,
    trajectoire_avec_effet,
)


def test_sans_mesure_le_scenario_redonne_la_baseline() -> None:
    resultat = scenario([])
    for s, b in zip(resultat, baseline(), strict=True):
        assert s.annee == b.annee
        assert s.dette == b.dette
        assert s.ecart_dette.central == 0.0


def test_zero_point_redonne_la_baseline() -> None:
    resultat = scenario([Mesure(LEVIER_TVA_NORMAL, 0.0, 2027)])
    for s, b in zip(resultat, baseline(), strict=True):
        assert s.dette.central == pytest.approx(b.dette.central)


def test_effet_sur_le_solde_un_point_de_tva() -> None:
    """Un point du taux normal : point net 2025 (DG Trésor, modèle) rapporté au PIB 2025."""
    point = estimer_point_tva(annee_comptes=2022, annee_cible=2025).net["taux_20"]
    pib = comptes_apu().valeur(2025, "S1", "pib")
    assert effet_solde(Mesure(LEVIER_TVA_NORMAL, 1.0, 2027)).central == pytest.approx(
        point / pib * 100
    )


def test_effet_proportionnel_au_nombre_de_points() -> None:
    un = scenario([Mesure(LEVIER_TVA_NORMAL, 1.0, 2027)])
    deux = scenario([Mesure(LEVIER_TVA_NORMAL, 2.0, 2027)])
    for a, b in zip(un, deux, strict=True):
        assert b.ecart_dette.central == pytest.approx(2 * a.ecart_dette.central)


def test_aucun_effet_avant_l_entree_en_vigueur() -> None:
    for ligne in scenario([Mesure(LEVIER_TVA_NORMAL, 1.0, 2028)]):
        if ligne.annee < 2028:
            assert ligne.ecart_solde_primaire.central == 0.0
            assert ligne.ecart_dette.central == 0.0
        else:
            assert ligne.ecart_solde_primaire.central > 0.0
            assert ligne.ecart_dette.central < 0.0


def test_dette_recalculee_a_la_main_premiere_annee() -> None:
    """d(2027) = d(2026) * (1 + r) / (1 + g) - (pb + effet) + sfa, entrées de la baseline."""
    centrale, _ = trajectoires()
    effet = 0.25
    lignes = trajectoire_avec_effet(centrale, {2027: effet})
    avant = next(a for a in centrale if a.annee == 2026)
    annee = next(a for a in centrale if a.annee == 2027)
    attendu = (
        avant.dette * (1 + annee.taux_apparent / 100) / (1 + annee.croissance_nominale / 100)
        - (annee.solde_primaire + effet)
        + annee.ajustement_stock_flux
    )
    assert next(a for a in lignes if a.annee == 2027).dette == pytest.approx(attendu)


def test_reponse_unitaire_lineaire() -> None:
    """La réponse à +1 point, multipliée par x, redonne l'écart de dette du scénario."""
    unite = reponse_unitaire(LEVIER_TVA_NORMAL, 2027)
    resultat = scenario([Mesure(LEVIER_TVA_NORMAL, -1.5, 2027)])
    for ligne, r in zip(resultat, unite, strict=True):
        assert ligne.ecart_dette.central == pytest.approx(-1.5 * r.ecart_dette.central)


def test_fourchettes_ordonnees_et_horizon() -> None:
    resultat = scenario([Mesure(LEVIER_TVA_NORMAL, 1.0, 2027)])
    assert resultat[-1].annee == ANNEE_FIN
    for ligne in resultat:
        for f in (ligne.dette, ligne.ecart_dette, ligne.ecart_solde_primaire):
            assert f.bas <= f.central <= f.haut


def test_levier_inconnu_refuse() -> None:
    with pytest.raises(ValueError, match="levier inconnu"):
        scenario([Mesure("inexistant", 1.0, 2027)])


def test_annee_hors_horizon_refusee() -> None:
    with pytest.raises(ValueError, match="année"):
        scenario([Mesure(LEVIER_TVA_NORMAL, 1.0, 2025)])


def test_bornes_tva_jusqu_au_taux_intermediaire() -> None:
    basse, haute = bornes_levier(LEVIER_TVA_NORMAL)
    assert basse == pytest.approx(-10.0)
    assert haute == pytest.approx(10.0)
    with pytest.raises(ValueError, match="bornes"):
        scenario([Mesure(LEVIER_TVA_NORMAL, 10.5, 2027)])


def test_reponse_lineaire_redonne_le_scenario() -> None:
    """Le calcul du site (niveau = base + x * unité, bornes = extrêmes) égale ``scenario``."""
    from fr_budget.scenario import reponse_lineaire

    x = -1.5
    r = reponse_lineaire(LEVIER_TVA_NORMAL, 2029)
    attendu = scenario([Mesure(LEVIER_TVA_NORMAL, x, 2029)])
    for i, ligne in enumerate(attendu):
        niveaux = [b[i] + x * u[i] for b, u in zip(r.base_dette, r.unite_dette, strict=True)]
        assert min(niveaux) == pytest.approx(ligne.dette.bas)
        assert niveaux[0] == pytest.approx(ligne.dette.central)
        assert max(niveaux) == pytest.approx(ligne.dette.haut)
        ecarts = [x * r.unite_dette[k][i] for k in r.indices_effet]
        assert min(ecarts) == pytest.approx(ligne.ecart_dette.bas)
        assert max(ecarts) == pytest.approx(ligne.ecart_dette.haut)
        soldes = [b[i] + x * u[i] for b, u in zip(r.base_solde, r.unite_solde, strict=True)]
        assert min(soldes) == pytest.approx(ligne.solde_primaire.bas)
        assert max(soldes) == pytest.approx(ligne.solde_primaire.haut)
