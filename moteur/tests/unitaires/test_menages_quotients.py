"""Effet sur les ménages types de la suppression des quotients familial et conjugal
(``fr_budget.menages.leviers``, ``fr_budget.menages.types.impot_individuel``), contrôlé contre
OpenFisca lancé sur des situations équivalentes."""

from __future__ import annotations

from dataclasses import replace

import pytest

from fr_budget import scenario as sc
from fr_budget.menages import leviers as lv
from fr_budget.menages import types as t

COUPLE = "couple_2_enfants"
COUPLE_INEGAL = t.Profil(
    "Couple marié, cadre au 95e centile et salarié au SMIC, sans enfant",
    (t.Adulte("1980-01-01", t.P95, cadre=True), t.Adulte("1985-01-01", t.SMIC)),
)


def test_quotient_familial_supprime_egale_le_couple_sans_enfant_a_charge() -> None:
    """À 100 %, l'impôt du couple avec deux enfants est celui du même couple sans enfant à
    charge (aucun autre dispositif lié aux enfants ne joue pour ce ménage)."""
    apres = lv.cascade_reformee(COUPLE, sc.LEVIER_IR_QF_EFFET, 100.0)
    sans = t.cascade_profil(replace(t.PROFILS[COUPLE], enfants=()))
    assert apres is not None
    assert apres.impot_revenu == pytest.approx(sans.impot_revenu, abs=1.0)
    assert apres.impot_revenu > t.cascade_annuelle(COUPLE).impot_revenu
    # Les prestations ne changent pas : seul l'impôt est recalculé.
    assert apres.prestations == t.cascade_annuelle(COUPLE).prestations


def test_quotient_conjugal_supprime_egale_deux_declarations_separees() -> None:
    seuls = sum(
        t.cascade_profil(t.Profil("seul", (a,))).impot_revenu for a in COUPLE_INEGAL.adultes
    )
    commun = t.cascade_profil(COUPLE_INEGAL).impot_revenu
    entier = lv.cascade_profil_reformee(COUPLE_INEGAL, sc.LEVIER_IR_QC_EFFET, 100.0)
    moitie = lv.cascade_profil_reformee(COUPLE_INEGAL, sc.LEVIER_IR_QC_EFFET, 50.0)
    assert entier is not None and moitie is not None
    assert entier.impot_revenu == pytest.approx(seuls, abs=1.0)
    assert seuls > commun
    assert moitie.impot_revenu == pytest.approx((commun + seuls) / 2, abs=1.0)


def test_personne_seule_sans_enfant_inchangee() -> None:
    ref = t.cascade_annuelle("celibataire_median").impot_revenu
    for levier in sc.LEVIERS_IR_QUOTIENTS:
        c = lv.cascade_reformee("celibataire_median", levier, 100.0)
        assert c is not None and c.impot_revenu == pytest.approx(ref)


def test_enfants_rattaches_au_revenu_le_plus_eleve() -> None:
    profil = t.PROFILS[COUPLE]
    simulation = t._construire(profil, t.ANNEE, None)
    assert t.rang_revenu_le_plus_eleve(simulation, profil, t.ANNEE) == 0


def test_grille_sans_baisse() -> None:
    for levier in sc.LEVIERS_IR_QUOTIENTS:
        g = lv.grille(levier)
        assert min(g) == 1.0 and max(g) == 100.0
        assert all(v > 0 for v in g)
