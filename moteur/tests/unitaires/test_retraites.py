"""Tests du module retraites, première étape (fr_budget.retraites)."""

from __future__ import annotations

import pytest

from fr_budget import retraites as rt

ENTREE = 2027


def test_reference_du_cor_reprise() -> None:
    """Repères du texte du rapport (page 124) : écarts d'âge de 0,3 an en 2030, 1,2 an en 2045
    et 3,0 ans en 2070 par rapport à la trajectoire à législation inchangée."""
    ref = rt.reference()
    for annee, ecart in ((2030, 0.3), (2045, 1.2), (2070, 3.0)):
        assert ref[annee].age_equilibre - ref[annee].age_ref == pytest.approx(ecart, abs=0.05)


def test_deux_voies_de_calcul_proches() -> None:
    """À partir de 2032, les voies « pension » et « prélèvement » diffèrent de moins de 15 %.
    Avant, l'écart d'âge d'équilibre est petit (moins de 0,3 an) et les arrondis du COR
    le rapport des deux voies est instable (jusqu'à 1,72 en 2026)."""
    for annee in range(2032, 2071):
        f = rt.effet_un_an(annee)
        assert f.bas > 0
        assert f.haut / f.bas < 1.15


def test_effet_un_an_entre_les_deux_voies() -> None:
    f = rt.effet_un_an(2040)
    assert f.bas <= f.central <= f.haut


def test_montee_en_charge_lineaire() -> None:
    d = rt.duree_montee_en_charge()
    assert rt.part_montee(ENTREE, ENTREE) == pytest.approx(1 / d)
    assert rt.part_montee(ENTREE + int(d) - 1, ENTREE) == pytest.approx(1.0)
    assert rt.part_montee(ENTREE + 10, ENTREE) == 1.0
    assert rt.part_montee(ENTREE - 1, ENTREE) == 0.0


@pytest.mark.parametrize("valeur", [1.0, -0.5, 2.5])
def test_effet_lineaire_et_borne(valeur: float) -> None:
    a = 2035
    centre = rt.effet(valeur, a, ENTREE, "central")
    assert centre == pytest.approx(valeur * rt.effet(1.0, a, ENTREE, "central"))
    assert rt.effet(valeur, a, ENTREE, "bas") <= centre <= rt.effet(valeur, a, ENTREE, "haut")


def test_relevement_ameliore_le_solde() -> None:
    assert rt.effet(1.0, 2035, ENTREE, "central") > 0
