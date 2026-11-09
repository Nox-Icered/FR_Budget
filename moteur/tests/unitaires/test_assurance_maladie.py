"""Assurance maladie, première étape (fr_budget.agrege.assurance_maladie)."""

from __future__ import annotations

import pytest

from fr_budget import scenario as sc
from fr_budget.agrege import assurance_maladie as am
from fr_budget.registres.acces import chiffrage, hypothese

ENTREE = 2027


def test_point_d_ondam_vaut_un_pour_cent_de_l_ondam() -> None:
    f = am.rendement_point_ondam()
    attendu = chiffrage("ondam_objectif_initial_2025") / 100
    assert f.central == pytest.approx(-attendu)
    assert f.bas <= f.central <= f.haut < 0


def test_realisation_des_economies_tiree_des_annexes() -> None:
    """Part des économies réalisées : 1 - écart d'exécution / économies prévues (2024, 2025)."""
    basse, haute = am.realisation_economies()
    ecart_2024 = chiffrage("ondam_constat_2024") - chiffrage("ondam_objectif_initial_2024")
    assert basse == pytest.approx(1 - ecart_2024 / chiffrage("ondam_economies_2024"))
    assert haute == pytest.approx(
        1 - chiffrage("ondam_ecart_execution_2025") / chiffrage("ondam_economies_2025")
    )
    assert basse < 1 < haute
    plage = hypothese(am.HYPOTHESE_REALISATION).plage
    assert plage.basse == pytest.approx(basse, abs=5e-4)
    assert plage.haute == pytest.approx(haute, abs=5e-4)


def test_franchises_un_pour_cent_du_rendement() -> None:
    f = am.rendement_pourcent_franchises()
    assert f.central == pytest.approx(chiffrage("franchises_pf_rendement_tous_regimes_2025") / 100)
    assert f.bas == pytest.approx(chiffrage("franchises_pf_doublement_avec_plafonds_2026") / 100)
    assert 0 < f.bas <= f.central <= f.haut


def test_plafond_ij_cout_d_un_retour_vers_1_8_smic() -> None:
    """Relever le plafond de 40 points de Smic (retour à 180 %) coûte l'économie de 2025 en année
    pleine."""
    f = am.rendement_smic_plafond_ij()
    total = -am.ECART_PLAFONDS_SMIC * f.central
    assert 0.9 - 1e-9 <= total <= 1.1 + 1e-9
    assert f.bas <= f.central <= f.haut < 0
    assert 0 < am.part_premiere_annee_ij() < 1


def test_leviers_dans_le_scenario() -> None:
    for levier in am.LEVIERS:
        assert sc.levier_registre(levier) == "assurance_maladie"
        basse, haute = sc.bornes_levier(levier)
        assert basse <= 0 <= haute
    assert sc.bornes_levier(am.LEVIER_IJ) == (0.0, am.ECART_PLAFONDS_SMIC)
    effet = sc.effet_solde(sc.Mesure(am.LEVIER_ONDAM, -1.0, ENTREE))
    assert effet.central > 0


def test_ondam_ne_se_cumule_pas_avec_les_mesures_qu_il_contient() -> None:
    for autre in (am.LEVIER_FRANCHISES, am.LEVIER_IJ):
        with pytest.raises(ValueError, match="double compte"):
            sc.verifier_double_compte(
                [sc.Mesure(am.LEVIER_ONDAM, -0.5, ENTREE), sc.Mesure(autre, 10.0, ENTREE)]
            )
    sc.verifier_double_compte(
        [sc.Mesure(am.LEVIER_FRANCHISES, 10.0, ENTREE), sc.Mesure(am.LEVIER_IJ, 10.0, ENTREE)]
    )


def test_premiere_annee_du_plafond_ij() -> None:
    """La première année ne compte qu'une partie de l'économie en année pleine (arrêts en cours)."""
    e = sc.scenario([sc.Mesure(am.LEVIER_IJ, 40.0, ENTREE)])
    par_annee = {a.annee: a.ecart_solde_primaire.central for a in e}
    assert 0 > par_annee[ENTREE] > par_annee[ENTREE + 1]


def test_ticket_moderateur_consultations_dix_points_valent_le_chiffrage_du_plfss() -> None:
    f = am.rendement_point_tm_consultations()
    assert am.ecart_tm_consultations() == pytest.approx(10.0)
    attendu = chiffrage("tm_consultations_economie_ville_plfss2025") + chiffrage(
        "tm_consultations_economie_etablissements_plfss2025"
    )
    assert 10 * f.central == pytest.approx(attendu)
    plage = hypothese(am.HYPOTHESE_REALISATION).plage
    assert f.bas == pytest.approx(f.central * plage.basse)
    assert f.haut == pytest.approx(f.central * plage.haute)


def test_ticket_moderateur_dentaire_constat_ramene_a_un_an() -> None:
    f = am.rendement_point_tm_dentaire()
    assert am.ecart_tm_dentaire() == pytest.approx(10.0)
    # Du 15 octobre 2023 au 31 décembre 2024 : 14,5 mois environ.
    assert 12 * am.annees_constat_dentaire() == pytest.approx(14.5, abs=0.1)
    constat = chiffrage("tm_dentaire_economie_oct2023_dec2024") / 1000
    assert 10 * f.central * am.annees_constat_dentaire() == pytest.approx(constat)
    # Borne basse : deux points de part des complémentaires sur 7,4 / 0,47 Md€ de dépenses.
    assert 10 * f.bas == pytest.approx(0.02 * 7.4 / 0.47)
    assert 0 < f.bas < f.central == f.haut


def test_ticket_moderateur_dans_le_scenario() -> None:
    for levier in am.LEVIERS_TICKET_MODERATEUR:
        assert sc.bornes_levier(levier) == (-10.0, 10.0)
        assert sc.taux_reference(levier) == pytest.approx(
            30.0 if levier == am.LEVIER_TM_CONSULTATIONS else 40.0
        )
        effet = sc.effet_solde(sc.Mesure(levier, 1.0, ENTREE))
        assert effet.central > 0
        with pytest.raises(ValueError, match="double compte"):
            sc.verifier_double_compte(
                [sc.Mesure(am.LEVIER_ONDAM, -0.5, ENTREE), sc.Mesure(levier, 5.0, ENTREE)]
            )
    sc.verifier_double_compte(
        [
            sc.Mesure(am.LEVIER_TM_CONSULTATIONS, 5.0, ENTREE),
            sc.Mesure(am.LEVIER_TM_DENTAIRE, 5.0, ENTREE),
            sc.Mesure(am.LEVIER_FRANCHISES, 10.0, ENTREE),
        ]
    )
