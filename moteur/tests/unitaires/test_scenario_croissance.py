"""Interrupteur de croissance dans le scénario (fr_budget.scenario, lot 3.2)."""

from __future__ import annotations

import pytest

from fr_budget import croissance as cr
from fr_budget import scenario as sc
from fr_budget.agrege import depenses_fiscales

ANNEE = 2027


def _tva(croissance: bool) -> list[sc.AnneeScenario]:
    return sc.scenario([sc.Mesure(sc.LEVIER_TVA_NORMAL, 1.0, ANNEE)], croissance=croissance)


def test_desactive_par_defaut() -> None:
    mesures = [sc.Mesure(sc.LEVIER_TVA_NORMAL, 1.0, ANNEE)]
    assert sc.scenario(mesures) == sc.scenario(mesures, croissance=False)


@pytest.mark.parametrize(
    "levier",
    [
        *sc.LEVIERS_REGISTRE,
        sc.levier_depense_fiscale(depenses_fiscales.catalogue()[0].code),
        sc.levier_credits_mission(sc.MISSION_SOLIDARITE),
    ],
)
def test_chaque_levier_a_un_multiplicateur(levier: str) -> None:
    assert sc.categorie_croissance(levier) in cr.CATEGORIES


def test_premiere_annee_le_solde_perd_alpha_fois_m() -> None:
    sans = {a.annee: a for a in _tva(False)}
    avec = {a.annee: a for a in _tva(True)}
    e = sans[ANNEE].ecart_solde_primaire.central
    m = cr.multiplicateur(cr.TVA).central
    attendu = e * (1 - cr.effet_sur_le_solde() * m)
    assert avec[ANNEE].ecart_solde_primaire.central == pytest.approx(attendu)


def test_une_hausse_d_impot_reduit_moins_la_dette_avec_la_croissance() -> None:
    for sans, avec in zip(_tva(False), _tva(True), strict=True):
        if sans.annee >= ANNEE:
            assert avec.ecart_dette.central > sans.ecart_dette.central
            assert avec.ecart_dette.bas <= avec.ecart_dette.central <= avec.ecart_dette.haut


def test_l_effet_sur_le_solde_s_eteint() -> None:
    sans, avec = _tva(False)[-1], _tva(True)[-1]
    ecart = avec.ecart_solde_primaire.central - sans.ecart_solde_primaire.central
    assert abs(ecart) < 0.01 * sans.ecart_solde_primaire.central


def test_le_multiplicateur_haut_elargit_la_fourchette() -> None:
    """Pour la TVA, la borne haute du multiplicateur (OFCE, 0,5) donne la dette la plus haute."""
    avec = {a.annee: a for a in _tva(True)}
    sans = {a.annee: a for a in _tva(False)}
    assert avec[ANNEE].ecart_dette.haut > avec[ANNEE].ecart_dette.central
    assert sans[ANNEE].ecart_dette.haut == pytest.approx(sans[ANNEE].ecart_dette.central)


def test_reponse_lineaire_avec_croissance() -> None:
    """unité + m * supplément redonne le scénario avec croissance, pour x unités."""
    x = -1.5
    r = sc.reponse_lineaire(sc.LEVIER_INDEXATION, ANNEE)
    m = cr.multiplicateur(cr.PRESTATIONS).central
    attendu = sc.scenario([sc.Mesure(sc.LEVIER_INDEXATION, x, ANNEE)], croissance=True)
    for i, ligne in enumerate(attendu):
        ecart = x * (r.unite_dette[0][i] + m * r.croissance_dette[0][i])
        assert ecart == pytest.approx(ligne.ecart_dette.central, abs=1e-9)


def test_depense_choisie_comme_le_levier_generique_du_site() -> None:
    """Le site regroupe les dépenses fiscales choisies une à une dans le levier générique :
    chacune prend donc le même multiplicateur que lui, y compris pour l'impôt sur le revenu
    (le calcul du site et celui du moteur doivent concorder)."""
    generique = sc.categorie_croissance(sc.LEVIER_DEPENSE_FISCALE_UNITE)
    for depense in depenses_fiscales.catalogue():
        assert sc.categorie_croissance(sc.levier_depense_fiscale(depense.code)) == generique
