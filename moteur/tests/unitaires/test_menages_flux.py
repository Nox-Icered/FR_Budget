"""Décomposition des prélèvements d'un ménage type, étape par étape (fr_budget.menages.flux)."""

from __future__ import annotations

import pytest

from fr_budget.menages import flux, types

TOLERANCE_EUROS = 0.05


@pytest.mark.parametrize("identifiant", list(types.PROFILS))
def test_chaque_etape_est_equilibree(identifiant: str) -> None:
    """Ce qui entre dans une étape en ressort, à quelques centimes près."""
    for etape in flux.flux_type(identifiant):
        assert sum(etape.entrees.values()) == pytest.approx(
            sum(etape.sorties.values()), abs=TOLERANCE_EUROS
        ), etape.id
        assert all(v > 0 for v in (*etape.entrees.values(), *etape.sorties.values())), etape.id


@pytest.mark.parametrize("identifiant", list(types.PROFILS))
def test_etapes_redonnent_la_cascade(identifiant: str) -> None:
    """Les montants de passage d'une étape à l'autre sont ceux de la cascade affichée."""
    c = types.cascade_annuelle(identifiant)
    etapes = {e.id: e for e in flux.flux_type(identifiant)}
    if c.salaire_brut:
        assert etapes["employeur"].entrees["cout_employeur"] == pytest.approx(c.cout_employeur)
        assert etapes["employeur"].sorties["salaire_brut"] == pytest.approx(c.salaire_brut)
        assert etapes["salarie"].entrees["salaire_brut"] == pytest.approx(c.salaire_brut)
        assert etapes["salarie"].sorties["net_avant_impot"] == pytest.approx(c.net_avant_impot)
    if c.pension_brute:
        assert etapes["retraite"].entrees["pension_brute"] == pytest.approx(c.pension_brute)
        assert etapes["retraite"].sorties["pension_nette"] == pytest.approx(c.pension_nette)
    if c.revenu_independant_brut:
        assert etapes["independant"].sorties["revenu_independant_net"] == pytest.approx(
            c.revenu_independant_net
        )
    impot = etapes["impot"]
    assert impot.sorties["net_apres_impot"] == pytest.approx(c.net_apres_impot)
    paye = impot.sorties.get("impot_revenu", 0.0) - impot.entrees.get("restitution_impot", 0.0)
    assert paye == pytest.approx(c.impot_revenu, abs=TOLERANCE_EUROS)


def test_smic_allegements_et_cotisations_brutes() -> None:
    """Au SMIC, l'allègement général couvre la plus grande partie des cotisations patronales :
    coût employeur + allègements = salaire brut + cotisations patronales avant allègements."""
    employeur = {e.id: e for e in flux.flux_type("celibataire_smic")}["employeur"]
    brutes = sum(v for k, v in employeur.sorties.items() if k != "salaire_brut")
    assert employeur.entrees["allegements"] > 0.5 * brutes
    assert set(employeur.sorties) >= {"salaire_brut", "retraite_base", "maladie", "famille"}


def test_cadre_sans_allegement() -> None:
    employeur = {e.id: e for e in flux.flux_type("cadre_p95")}["employeur"]
    assert "allegements" not in employeur.entrees


def test_apprenti_exonerations_salariales() -> None:
    """L'apprenti est exonéré de cotisations salariales jusqu'à 79 % du SMIC : l'exonération
    entre dans l'étape et ressort en cotisations, sans rien retenir sur le net."""
    salarie = {e.id: e for e in flux.flux_type("apprenti_19_ans")}["salarie"]
    assert salarie.entrees["exonerations_salariales"] > 0
    assert salarie.sorties["net_avant_impot"] == pytest.approx(salarie.entrees["salaire_brut"])
