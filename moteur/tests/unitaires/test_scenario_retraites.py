"""Levier « âge effectif moyen de départ » dans le scénario (lot 3.1)."""

from __future__ import annotations

import pytest

from fr_budget import retraites as rt
from fr_budget import scenario as sc

ANNEE = 2027
LEVIER = sc.LEVIER_RETRAITES_AGE


def test_levier_au_registre() -> None:
    assert sc.levier_registre(LEVIER) == "retraites"


def test_hors_bornes_refuse() -> None:
    with pytest.raises(ValueError, match="hors des bornes"):
        sc.scenario([sc.Mesure(LEVIER, 3.5, ANNEE)])


def test_effet_annuel_avec_montee_en_charge() -> None:
    lignes = {a.annee: a for a in sc.scenario([sc.Mesure(LEVIER, 2.0, ANNEE)])}
    for annee in (ANNEE, ANNEE + 1, 2040):
        attendu = rt.effet(2.0, annee, ANNEE, "central")
        assert lignes[annee].ecart_solde_primaire.central == pytest.approx(attendu)
    assert lignes[ANNEE - 1].ecart_solde_primaire.central == 0


def test_reponse_lineaire() -> None:
    x = -0.75
    r = sc.reponse_lineaire(LEVIER, 2030)
    attendu = sc.scenario([sc.Mesure(LEVIER, x, 2030)])
    for i, ligne in enumerate(attendu):
        assert x * r.unite_dette[0][i] == pytest.approx(ligne.ecart_dette.central, abs=1e-9)
        bornes = sorted(x * r.unite_dette[k][i] for k in r.indices_effet[1:])
        assert bornes[0] == pytest.approx(ligne.ecart_dette.bas, abs=1e-9)


def test_sans_multiplicateur_de_demande() -> None:
    mesures = [sc.Mesure(LEVIER, 1.0, ANNEE)]
    assert sc.scenario(mesures, croissance=True)[-1].ecart_dette.central == pytest.approx(
        sc.scenario(mesures)[-1].ecart_dette.central
    )
    assert all(v == 0 for v in sc.reponse_lineaire(LEVIER, ANNEE).croissance_dette[0])
