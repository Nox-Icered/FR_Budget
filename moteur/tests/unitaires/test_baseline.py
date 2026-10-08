"""Tests unitaires de la baseline (lot 1.3) : formules et cohérence avec les sources."""

from __future__ import annotations

from itertools import pairwise

import pytest

from fr_budget.baseline import (
    ANNEE_FIN,
    ANNEE_RACCORD,
    VARIANTES_VIEILLISSEMENT,
    ageing_report,
    baseline,
    charge_interets_resf,
    croissance_nominale,
    part_refinancee_etat,
    projection,
    resf,
    solde_primaire_projete,
    trajectoire_resf,
)
from fr_budget.registres.acces import hypothese


def test_croissance_nominale_compose_volume_et_prix() -> None:
    assert croissance_nominale(0.01, 0.02) == pytest.approx(0.0302)
    assert croissance_nominale(0.0, 0.0) == 0.0


def test_charge_d_interets_publiee_jusqu_en_2027() -> None:
    for annee in (2025, 2026, 2027):
        assert charge_interets_resf(annee) == resf()[(annee, "charge_interets")]


def test_charge_d_interets_2028_2030_par_l_ajustement_structurel() -> None:
    """Variation de la charge = ajustement structurel primaire - ajustement structurel."""
    donnees = resf()
    for annee in (2028, 2029, 2030):
        variation = (
            donnees[(annee, "ajustement_structurel_primaire")]
            - donnees[(annee, "ajustement_structurel")]
        )
        attendu = charge_interets_resf(annee - 1) + variation
        assert charge_interets_resf(annee) == pytest.approx(attendu)


def test_trajectoire_resf_reprend_la_dette_publiee() -> None:
    lignes = trajectoire_resf()
    assert [ligne.annee for ligne in lignes] == list(range(2025, ANNEE_RACCORD + 1))
    for ligne in lignes:
        assert ligne.dette == resf()[(ligne.annee, "dette")]


def test_trajectoire_resf_est_coherente_avec_la_formule() -> None:
    """L'ajustement stock-flux implicite referme exactement la formule chaque année."""
    lignes = trajectoire_resf()
    for avant, apres in pairwise(lignes):
        recalcul = (
            avant.dette * (1 + apres.taux_apparent / 100) / (1 + apres.croissance_nominale / 100)
            - apres.solde_primaire
            + apres.ajustement_stock_flux
        )
        assert recalcul == pytest.approx(apres.dette)


def test_part_refinancee_etat_concorde_avec_le_registre() -> None:
    h = hypothese("baseline_part_refinancee")
    assert round(part_refinancee_etat(2027), 3) == h.valeur_centrale
    assert round(part_refinancee_etat(2026), 3) == h.plage.basse


def test_solde_primaire_suit_le_cout_du_vieillissement() -> None:
    """Méthode (a) : solde primaire 2030 moins la variation du coût du vieillissement."""
    ar = ageing_report()
    depart = 1.3
    attendu = depart - (ar[(2040, "cout_vieillissement")] - ar[(2030, "cout_vieillissement")])
    assert solde_primaire_projete(depart, 2040, variante=None) == pytest.approx(attendu)
    # En 2030, aucune variante ne change le solde : le niveau vient du RESF.
    for variante in VARIANTES_VIEILLISSEMENT:
        assert solde_primaire_projete(depart, 2030, variante=variante) == pytest.approx(depart)


def test_projection_part_nulle_garde_le_taux_apparent() -> None:
    lignes = projection(part_refinancee=0.0)
    taux = {round(ligne.taux_apparent, 12) for ligne in lignes}
    assert len(taux) == 1


def test_projection_couvre_jusqu_a_la_derniere_annee() -> None:
    lignes = projection()
    assert lignes[0].annee == ANNEE_RACCORD + 1
    assert lignes[-1].annee == ANNEE_FIN


def test_projection_part_totale_prend_le_taux_de_marche() -> None:
    ar = ageing_report()
    for ligne in projection(part_refinancee=1.0):
        assert ligne.taux_apparent == pytest.approx(ar[(ligne.annee, "taux_nominal")])


def test_baseline_encadre_la_trajectoire_centrale() -> None:
    lignes = baseline()
    assert lignes[0].annee == 2025
    assert lignes[-1].annee == ANNEE_FIN
    for ligne in lignes:
        assert ligne.dette.bas <= ligne.dette.central <= ligne.dette.haut
    # Jusqu'en 2030, la dette est celle du RESF, sans fourchette.
    for ligne in lignes:
        if ligne.annee <= ANNEE_RACCORD:
            assert ligne.dette.bas == ligne.dette.central == ligne.dette.haut
