"""Moteur de barème de l'impôt sur le revenu (fr_budget.agrege.bareme_ir)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import bareme_ir as b
from fr_budget.registres.acces import chiffrage


def test_impot_par_part_barème_simple() -> None:
    bareme = b.Bareme((0.0, 10_000.0, 20_000.0), (0.0, 0.1, 0.3))
    assert b.impot_par_part(bareme, 5_000.0) == 0.0
    assert b.impot_par_part(bareme, 15_000.0) == pytest.approx(500.0)
    assert b.impot_par_part(bareme, 30_000.0) == pytest.approx(1_000.0 + 3_000.0)


def test_bareme_valide() -> None:
    with pytest.raises(ValueError, match="croissants"):
        b.Bareme((0.0, 20_000.0, 10_000.0), (0.0, 0.1, 0.2))
    with pytest.raises(ValueError, match="taux"):
        b.Bareme((0.0, 10_000.0), (0.0, 1.5))
    with pytest.raises(ValueError, match="premier seuil"):
        b.Bareme((5_000.0, 10_000.0), (0.0, 0.1))


def test_bareme_openfisca_2024() -> None:
    bareme = b.bareme_openfisca(2024)
    assert bareme.seuils[1] == 11_497.0
    assert bareme.taux[-1] == pytest.approx(0.45)


def test_reforme_nulle_sans_effet() -> None:
    bareme = b.bareme_openfisca(2024)
    f = b.effet(bareme, bareme, 2024)
    assert (f.bas, f.central, f.haut) == (0.0, 0.0, 0.0)


def test_calage_redonne_l_impot_au_bareme_2024() -> None:
    """Le barème de 2024 redonne l'impôt au barème publié par la DGFiP, sauf dans les dixièmes
    où le barème ne prélève rien (premier et deuxième dixièmes, non calés : la DGFiP y publie
    10 € par part, arrondis)."""
    non_cales = b.impot_publie_non_cale_2024()
    assert 0 < non_cales < 0.5
    assert b.impot_modele(b.bareme_openfisca(2024), 2024) == pytest.approx(
        b.impot_bareme_publie_2024() - non_cales, rel=1e-6
    )


def test_hausse_des_taux_augmente_l_impot() -> None:
    reference = b.bareme_openfisca(2024)
    hausse = b.Bareme(
        reference.seuils, tuple(t + 0.01 * (t > 0) for t in reference.taux), reference.decote
    )
    f = b.effet(reference, hausse, 2024)
    assert 0 < f.bas <= f.central <= f.haut or 0 < f.bas <= f.haut


def test_tranches_ajoutees_et_retirees() -> None:
    """Ajouter une tranche au taux de la précédente ne change rien ; la retirer non plus."""
    reference = b.bareme_openfisca(2024)
    seuils = (*reference.seuils, 500_000.0)
    taux = (*reference.taux, reference.taux[-1])
    f = b.effet(reference, b.Bareme(seuils, taux, reference.decote), 2024)
    assert f.central == pytest.approx(0.0, abs=1e-9)


def test_decote_depuis_2014() -> None:
    """Décote célibataire 2024 (OpenFisca) : seuil - taux x impôt, plafonnée à l'impôt."""
    d = b.bareme_openfisca(2024).decote
    assert d is not None
    assert d.montant(1_500.0, couple=False) == pytest.approx(d.seuil_celibataire - d.taux * 1_500.0)
    assert d.montant(100.0, couple=False) == pytest.approx(100.0)
    assert d.montant(10_000.0, couple=True) == 0.0


def test_correction_haut_redonne_les_foyers_a_45_pour_cent() -> None:
    bareme = b.bareme_openfisca(2024)
    foyers = b._foyers_au_dessus(b.segments(2024), bareme.seuils[-1], 2024)
    assert foyers == pytest.approx(chiffrage("ir_foyers_tranche_45_2024") * 1000, rel=0.01)


def test_part_des_couples_par_rang() -> None:
    segs = {s.nom: s for s in b.segments(2024)}
    assert b.part_couples(segs["1"]) == pytest.approx(chiffrage("ir_couples_quartile_1_2022") / 100)
    assert b.part_couples(segs["5"], b.UNIFORME) == pytest.approx(0.32)


def test_hypothese_ecart_concorde_avec_la_validation() -> None:
    """Le registre recopie la plage tirée des quatre réformes de validation : elle doit rester
    exacte au millième."""
    from fr_budget.registres.acces import hypothese

    basse, haute = b.plage_ecart_validation()
    plage = hypothese("ir_bareme_ecart").plage
    assert plage.basse == pytest.approx(basse, abs=5e-4)
    assert plage.haute == pytest.approx(haute, abs=5e-4)


def test_effet_site_nul_pour_le_bareme_de_2025() -> None:
    f = b.effet_site(b.bareme_openfisca(b.ANNEE_SITE))
    assert (f.bas, f.central, f.haut) == (0.0, 0.0, 0.0)


def test_levier_generique_et_double_compte() -> None:
    from fr_budget import scenario as sc

    assert sc.rendement_unitaire(sc.LEVIER_IR_BAREME).central == 1.0
    with pytest.raises(ValueError, match="double compte"):
        sc.verifier_double_compte(
            [sc.Mesure(sc.LEVIER_IR_BAREME, 2.0, 2027), sc.Mesure(sc.LEVIER_IR_SEUILS, 1.0, 2027)]
        )
