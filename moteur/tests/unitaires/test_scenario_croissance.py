"""Interrupteur de croissance dans le scénario (fr_budget.scenario, lot 3.2)."""

from __future__ import annotations

import pytest

from fr_budget import croissance as cr
from fr_budget import scenario as sc
from fr_budget.agrege import depenses_fiscales
from fr_budget.baseline import trajectoires

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
    """Seuls les relèvements de l'âge de départ, effectif ou légal (effet d'offre), n'ont pas
    de multiplicateur de demande (fiche retraites, § 5 et § 8)."""
    attendu = (cr.AUCUN,) if levier in sc.LEVIERS_RETRAITES else cr.CATEGORIES
    assert sc.categorie_croissance(levier) in attendu


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


def test_fourchette_avec_mesures_de_signes_opposes_couvre_chaque_multiplicateur() -> None:
    """Quand des mesures ont des effets de signes opposés, chaque multiplicateur varie dans sa
    plage indépendamment des autres : l'écart à la baseline couvre les quatre combinaisons des
    bornes (revue de code du 28 octobre 2026 ; un multiplicateur commun la rétrécissait)."""
    mesures = [
        sc.Mesure(sc.LEVIER_TVA_NORMAL, 2.0, ANNEE),
        sc.Mesure(sc.LEVIER_DOTATIONS_DGF, 5.0, ANNEE),
    ]
    centrale, _ = trajectoires()
    resultat = sc.scenario(mesures, croissance=True)
    for effet in sc.BORNES_EFFET:
        for b1 in sc.BORNES_EFFET:
            for b2 in sc.BORNES_EFFET:
                t = sc._trajectoire_mesures(centrale, mesures, effet, [b1, b2])
                for ligne, a, ref in zip(resultat, t, centrale, strict=True):
                    ecart = a.dette - ref.dette
                    assert ligne.ecart_dette.bas - 1e-9 <= ecart <= ligne.ecart_dette.haut + 1e-9


def test_fourchette_d_une_mesure_seule_inchangee() -> None:
    """Une mesure seule : les extrêmes de l'écart sont ceux des bornes de son multiplicateur."""
    mesure = [sc.Mesure(sc.LEVIER_TVA_NORMAL, 2.0, ANNEE)]
    centrale, _ = trajectoires()
    resultat = sc.scenario(mesure, croissance=True)
    traj = [
        sc._trajectoire_mesures(centrale, mesure, e, b)
        for e in sc.BORNES_EFFET
        for b in (*sc.BORNES_EFFET, sc.CENTRAL)
    ]
    for i, (ligne, ref) in enumerate(zip(resultat, centrale, strict=True)):
        ecarts = [t[i].dette - ref.dette for t in traj]
        assert ligne.ecart_dette.bas == pytest.approx(min(*ecarts, ligne.ecart_dette.central))
        assert ligne.ecart_dette.haut == pytest.approx(max(*ecarts, ligne.ecart_dette.central))
