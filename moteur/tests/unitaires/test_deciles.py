"""Répartition par décile de niveau de vie (fr_budget.menages.deciles)."""

from __future__ import annotations

import numpy as np
import pytest

from fr_budget import scenario as sc
from fr_budget.menages import deciles as dc

ANNEE = 2027


def test_parts_somment_a_un() -> None:
    for levier in dc.CLES:
        for p in dc.variantes_parts(levier):
            assert p.shape == (dc.NOMBRE,)
            assert p.sum() == pytest.approx(1.0)


def test_chaque_levier_est_reparti_ou_signale() -> None:
    """Aucun levier du simulateur n'est oublié : il a une clé ou figure parmi les non répartis."""
    for levier in sc.LEVIERS_REGISTRE:
        assert (levier in dc.CLES) != (levier in dc.NON_REPARTIS), levier


def test_somme_des_deciles_egale_l_effet_national() -> None:
    mesures = [sc.Mesure("tva_taux_normal", 1.0, ANNEE), sc.Mesure("csg_activite", -0.5, ANNEE)]
    r = dc.repartition(mesures)
    attendu = sum(-m.valeur * sc.rendement_unitaire(m.levier).central for m in mesures)
    assert sum(f.central for f in r.milliards) == pytest.approx(attendu)
    assert r.non_repartis == []


def test_hausse_de_tva_baisse_le_revenu_de_chaque_decile() -> None:
    r = dc.repartition([sc.Mesure("tva_taux_normal", 1.0, ANNEE)])
    for f in r.euros_par_uc:
        assert f.bas <= f.central <= f.haut < 0


def test_fourchette_contient_la_variante_budget_de_famille() -> None:
    """TVA : la part du Budget de famille 2017 entre dans la fourchette."""
    bdf = dc.parts_budget_de_famille("tva_taux_normal")
    r = dc.repartition([sc.Mesure("tva_taux_normal", 1.0, ANNEE)])
    e = -sc.rendement_unitaire("tva_taux_normal").central
    for d, f in enumerate(r.milliards):
        assert f.bas - 1e-12 <= e * bdf[d] <= f.haut + 1e-12


def test_euros_par_unite_de_consommation() -> None:
    r = dc.repartition([sc.Mesure("csg_retraites", 1.0, ANNEE)])
    uc = dc.unites_consommation()
    for d in range(dc.NOMBRE):
        assert r.euros_par_uc[d].central == pytest.approx(
            r.milliards[d].central * 1e9 / (uc[d] * 1e6)
        )


def test_impot_sur_le_revenu_porte_surtout_sur_le_dernier_decile() -> None:
    p = dc.part_centrale("ir_seuils_bareme")
    assert int(np.argmax(p)) == dc.NOMBRE - 1


def test_mesures_non_reparties_signalees() -> None:
    r = dc.repartition(
        [
            sc.Mesure("remunerations_point_indice", 1.0, ANNEE),
            sc.Mesure("is_taux_normal", 1.0, ANNEE),
        ]
    )
    assert r.non_repartis == ["remunerations_point_indice"]
    attendu = -sc.rendement_unitaire("is_taux_normal").central
    assert sum(f.central for f in r.milliards) == pytest.approx(attendu)


def test_terme_croise_reparti_avec_la_cle_de_la_csg() -> None:
    seul = dc.repartition([sc.Mesure("indexation_pensions_prestations", 1.0, ANNEE)])
    deux = dc.repartition(
        [
            sc.Mesure("indexation_pensions_prestations", 1.0, ANNEE),
            sc.Mesure("csg_retraites", 1.0, ANNEE),
        ]
    )
    csg = dc.repartition([sc.Mesure("csg_retraites", 1.0, ANNEE)])
    croise = sc.rendement_unitaire(
        next(i for i, p in sc.interactions.CHIFFREES.items() if "csg_retraites" in p)
    ).central
    total = sum(f.central for f in deux.milliards)
    assert total == pytest.approx(
        sum(f.central for f in seul.milliards) + sum(f.central for f in csg.milliards) - croise
    )


def test_pourcentage_du_revenu_disponible() -> None:
    r = dc.repartition([sc.Mesure("tva_taux_normal", 1.0, ANNEE)])
    rdn = dc.revenu_disponible()
    for d in range(dc.NOMBRE):
        assert r.pourcent_revenu[d].central == pytest.approx(100 * r.milliards[d].central / rdn[d])
