"""Tests de l'effet des leviers sur les ménages types (fr_budget.menages.leviers).

Chaque effet est comparé à une identité calculée sans la réforme, à partir des variables de la
simulation de référence et des paramètres d'OpenFisca.
"""

from __future__ import annotations

import warnings

import pytest

from fr_budget import scenario
from fr_budget.menages import leviers as lv
from fr_budget.menages import types as t
from fr_budget.menages.openfisca import systeme_socio_fiscal

ANNEE = t.ANNEE


def _somme(identifiant: str, variable: str, periodes: list[str]) -> float:
    simulation = t._simulation(identifiant, ANNEE)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(sum(simulation.calculate(variable, p).sum() for p in periodes))


def _mois() -> list[str]:
    return t._mois(ANNEE)


def test_tous_les_leviers_du_simulateur_sont_classes() -> None:
    leviers_simulateur = {
        scenario.LEVIER_TVA_NORMAL,
        *scenario.LEVIERS_ACCISES,
        scenario.LEVIER_IS_TAUX_NORMAL,
        scenario.LEVIER_IS_SURTAXE,
        *scenario.LEVIERS_DOTATIONS,
        *scenario.LEVIERS_REMUNERATIONS,
        *scenario.LEVIERS_CSG,
        scenario.LEVIER_COTISATIONS_TAUX,
        scenario.LEVIER_ALLEGEMENTS,
        scenario.LEVIER_PA_PENTE,
        scenario.LEVIER_IR_SEUILS,
        scenario.LEVIER_INDEXATION,
        scenario.LEVIER_RETRAITES_AGE,
        scenario.LEVIER_DEPENSE_FISCALE_UNITE,
        scenario.LEVIER_CREDITS_UNITE,
    }
    assert set(lv.LEVIERS) | set(lv.SANS_EFFET) == leviers_simulateur
    assert not set(lv.LEVIERS) & set(lv.SANS_EFFET)


@pytest.mark.parametrize("levier", lv.LEVIERS)
def test_mesure_nulle_sans_effet(levier: str) -> None:
    assert lv.cascade_reformee("celibataire_median", levier, 0.0) == t.cascade_annuelle(
        "celibataire_median"
    )


def test_reforme_sans_effet_avant_l_annee() -> None:
    """La législation réformée garde les valeurs d'avant le 1er janvier de l'année."""
    systeme = lv.legislation("csg_activite", 1.0).systeme
    p = systeme.parameters.prelevements_sociaux.contributions_sociales.csg.activite.deductible
    reference = systeme_socio_fiscal().parameters.prelevements_sociaux.contributions_sociales
    assert p(f"{ANNEE - 1}-12-01") == reference.csg.activite.deductible(f"{ANNEE - 1}-12-01")
    assert p(f"{ANNEE}-06-01") == pytest.approx(
        reference.csg.activite.deductible(f"{ANNEE}-06-01") + 0.01
    )


def test_csg_activite_salarie() -> None:
    """Un point de CSG : le net baisse d'un point de l'assiette de la CSG ; la CSG étant
    déductible, l'impôt baisse."""
    avant = t.cascade_annuelle("celibataire_median")
    apres = lv.cascade_reformee("celibataire_median", "csg_activite", 1.0)
    assert apres is not None
    # Assiette « abattue » : avant l'abattement pour frais professionnels (1,75 % sous 4 PSS).
    abattement = (
        systeme_socio_fiscal()
        .parameters(f"{ANNEE}-06-01")
        .prelevements_sociaux.contributions_sociales.csg.activite.abattement.rates[0]
    )
    assiette = _somme("celibataire_median", "assiette_csg_abattue", _mois()) * (
        1 - abattement
    ) + _somme("celibataire_median", "assiette_csg_non_abattue", _mois())
    assert apres.net_avant_impot - avant.net_avant_impot == pytest.approx(-0.01 * assiette, abs=1)
    assert apres.salaire_brut == avant.salaire_brut
    assert apres.cout_employeur == avant.cout_employeur
    assert apres.impot_revenu < avant.impot_revenu


def test_csg_activite_artisan() -> None:
    """Revenu brut inchangé ; la CSG augmente d'un point de l'assiette sociale."""
    avant = t.cascade_annuelle("artisan")
    apres = lv.cascade_reformee("artisan", "csg_activite", 1.0)
    assert apres is not None
    assert apres.revenu_independant_brut == pytest.approx(avant.revenu_independant_brut)
    adulte = t.PROFILS["artisan"].adultes[0]
    assiette = t._cotisations_independant(adulte, ANNEE, 0.0).assiette
    ecart_csg = apres.csg_crds_independant - avant.csg_crds_independant
    assert ecart_csg == pytest.approx(0.01 * assiette, abs=0.5)
    assert apres.impot_revenu <= avant.impot_revenu


def test_csg_retraites_taux_reduit_sans_effet() -> None:
    """Le retraité type paie le taux réduit : le taux plein ne le concerne pas."""
    pension = _somme("retraite_seul", "retraite_brute", _mois())
    csg = -_somme("retraite_seul", "csg_deductible_retraite", _mois()) - _somme(
        "retraite_seul", "csg_imposable_retraite", _mois()
    )
    contributions = systeme_socio_fiscal().parameters.prelevements_sociaux.contributions_sociales
    pensions = contributions.csg.remplacement.pensions_retraite_invalidite
    assert csg / pension < pensions.taux_plein(f"{ANNEE}-06-01")
    assert lv.cascade_reformee("retraite_seul", "csg_retraites", 1.0) == t.cascade_annuelle(
        "retraite_seul"
    )


def test_csg_retraites_taux_plein() -> None:
    """Pension saisie élevée (taux plein) : la pension nette baisse d'un point de la pension
    brute."""
    profil = t.Profil("Retraité", (t.Adulte("1955-01-01", t.RETRAITE, montant_mensuel=3000.0),))
    avant = t.cascade_profil(profil)
    apres = lv.cascade_profil_reformee(profil, "csg_retraites", 1.0)
    assert apres is not None
    assert apres.pension_nette - avant.pension_nette == pytest.approx(
        -0.01 * avant.pension_brute, abs=1
    )


def test_cotisation_patronale_incidence_comptable() -> None:
    avant = t.cascade_annuelle("celibataire_median")
    apres = lv.cascade_reformee("celibataire_median", scenario.LEVIER_COTISATIONS_TAUX, 1.0)
    assert apres is not None
    assiette = _somme("celibataire_median", "assiette_cotisations_sociales", _mois())
    assert apres.cout_employeur - avant.cout_employeur == pytest.approx(0.01 * assiette, abs=1)
    assert apres.net_apres_impot == pytest.approx(avant.net_apres_impot)


def test_allegements() -> None:
    """Allègements augmentés de 10 % : le coût du SMIC baisse de 10 % des allègements ; le cadre
    au-dessus des seuils n'en a pas et n'est pas touché."""
    allegements = sum(_somme("celibataire_smic", v, _mois()) for v in lv.ALLEGEMENTS)
    assert allegements > 0
    avant = t.cascade_annuelle("celibataire_smic")
    apres = lv.cascade_reformee("celibataire_smic", scenario.LEVIER_ALLEGEMENTS, 10.0)
    assert apres is not None
    assert apres.cout_employeur - avant.cout_employeur == pytest.approx(-0.1 * allegements, abs=1)
    assert apres.net_apres_impot == pytest.approx(avant.net_apres_impot)
    assert sum(_somme("cadre_p95", v, _mois()) for v in lv.ALLEGEMENTS) == 0
    assert lv.cascade_reformee(
        "cadre_p95", scenario.LEVIER_ALLEGEMENTS, 10.0
    ) == t.cascade_annuelle("cadre_p95")


def _impot_bareme(quotient: float, facteur: float) -> float:
    bareme = (
        systeme_socio_fiscal()
        .parameters(f"{ANNEE}-01-01")
        .impot_revenu.bareme_ir_depuis_1945.bareme
    )
    seuils = [float(s) * facteur for s in bareme.thresholds]
    hauts = [*seuils[1:], float("inf")]
    return sum(
        float(taux) * max(0.0, min(quotient, h) - s)
        for s, h, taux in zip(seuils, hauts, bareme.rates, strict=True)
    )


def test_seuils_ir_cadre() -> None:
    """Cadre célibataire (une part, sans décote ni plafonnement) : l'impôt baisse comme le
    barème appliqué au revenu net imposable avec des seuils relevés de 1 %."""
    rni = _somme("cadre_p95", "rni", [str(ANNEE)])
    attendu = _impot_bareme(rni, 1.01) - _impot_bareme(rni, 1.0)
    avant = t.cascade_annuelle("cadre_p95")
    apres = lv.cascade_reformee("cadre_p95", scenario.LEVIER_IR_SEUILS, 1.0)
    assert apres is not None
    assert attendu < 0
    assert apres.impot_revenu - avant.impot_revenu == pytest.approx(attendu, abs=1)


def test_pente_prime_activite() -> None:
    """Un point de pente : la prime d'activité augmente d'un point des revenus d'activité
    pris en compte."""
    avant = t.cascade_annuelle("celibataire_smic")
    apres = lv.cascade_reformee("celibataire_smic", scenario.LEVIER_PA_PENTE, 1.0)
    assert apres is not None
    revenus = _somme("celibataire_smic", "ppa_revenu_activite", _mois())
    ecart = apres.prestations["ppa"] - avant.prestations["ppa"]
    assert ecart == pytest.approx(0.01 * revenus, rel=0.02)


def test_indexation_prestations_familiales() -> None:
    """Un point de revalorisation : les allocations familiales augmentent de 1 %."""
    avant = t.cascade_annuelle("couple_2_enfants")
    apres = lv.cascade_reformee("couple_2_enfants", scenario.LEVIER_INDEXATION, 1.0)
    assert apres is not None
    assert apres.prestations["af"] == pytest.approx(avant.prestations["af"] * 1.01, abs=1)


def test_indexation_pension_non_chiffree() -> None:
    assert lv.cascade_reformee("retraite_seul", scenario.LEVIER_INDEXATION, 1.0) is None


def test_levier_sans_effet_refuse() -> None:
    with pytest.raises(ValueError, match="pas d'effet direct"):
        lv.legislation(scenario.LEVIER_TVA_NORMAL, 1.0)


# Incidence des cotisations patronales : lecture répercutée sur le salaire.


def test_incidence_salaire_garde_le_cout_employeur() -> None:
    """Hausse d'un point répercutée : le coût employeur ne change pas, le brut et le net
    baissent."""
    avant = t.cascade_annuelle("celibataire_median")
    apres = lv.cascade_reformee(
        "celibataire_median", scenario.LEVIER_COTISATIONS_TAUX, 1.0, ANNEE, lv.SALAIRE
    )
    assert apres is not None
    assert apres.cout_employeur == pytest.approx(avant.cout_employeur, abs=lv.PRECISION_COUT)
    assert apres.salaire_brut < avant.salaire_brut
    assert apres.net_apres_impot < avant.net_apres_impot


def test_incidence_salaire_plancher_du_smic() -> None:
    """Au SMIC, le salaire ne peut pas baisser : la hausse reste au coût employeur, comme en
    lecture comptable."""
    comptable = lv.cascade_reformee("celibataire_smic", scenario.LEVIER_COTISATIONS_TAUX, 1.0)
    salaire = lv.cascade_reformee(
        "celibataire_smic", scenario.LEVIER_COTISATIONS_TAUX, 1.0, ANNEE, lv.SALAIRE
    )
    assert salaire is not None
    assert comptable is not None
    assert salaire.salaire_brut == pytest.approx(
        t.cascade_annuelle("celibataire_smic").salaire_brut
    )
    assert salaire.cout_employeur == pytest.approx(comptable.cout_employeur, abs=1)


def test_incidence_salaire_allegements() -> None:
    """Allègements augmentés et répercutés : au SMIC, le coût employeur revient à celui de
    référence et le salaire brut augmente."""
    avant = t.cascade_annuelle("celibataire_smic")
    apres = lv.cascade_reformee(
        "celibataire_smic", scenario.LEVIER_ALLEGEMENTS, 10.0, ANNEE, lv.SALAIRE
    )
    assert apres is not None
    assert apres.cout_employeur == pytest.approx(avant.cout_employeur, abs=lv.PRECISION_COUT)
    assert apres.salaire_brut > avant.salaire_brut


def test_incidence_salaire_apprenti_inchange() -> None:
    """Apprenti payé au minimum légal : son salaire ne s'ajuste pas."""
    comptable = lv.cascade_reformee("apprenti_19_ans", scenario.LEVIER_COTISATIONS_TAUX, 1.0)
    salaire = lv.cascade_reformee(
        "apprenti_19_ans", scenario.LEVIER_COTISATIONS_TAUX, 1.0, ANNEE, lv.SALAIRE
    )
    assert salaire == comptable


def test_incidence_mesure_nulle() -> None:
    assert lv.cascade_reformee(
        "couple_2_enfants", scenario.LEVIER_ALLEGEMENTS, 0.0, ANNEE, lv.SALAIRE
    ) == pytest.approx(t.cascade_annuelle("couple_2_enfants"))


def test_incidence_salaire_refusee_hors_cotisations() -> None:
    with pytest.raises(ValueError, match="pas de lecture répercutée"):
        lv.cascade_reformee("celibataire_median", "csg_activite", 1.0, ANNEE, lv.SALAIRE)
