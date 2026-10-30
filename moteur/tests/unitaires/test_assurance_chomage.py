"""Assurance chômage, première étape (fr_budget.agrege.assurance_chomage)."""

from __future__ import annotations

import pytest

from fr_budget import scenario as sc
from fr_budget.agrege import assurance_chomage as ac
from fr_budget.registres.acces import chiffrage, hypothese

ANNEE = 2027


def test_point_de_contribution_2026() -> None:
    """Contributions principales de 2026 (30,3 Md€) divisées par le taux de 4,00 %."""
    assert ac.valeur_point_contribution(2026) == pytest.approx(30.3 / 4.00)


def test_fourchette_de_la_contribution_entoure_la_valeur_centrale() -> None:
    f = ac.rendement_point_contribution()
    assert f.bas < f.central < f.haut


def test_prelevements_sur_les_allocations() -> None:
    """CSG 6,2 % et CRDS 0,5 %, après l'abattement de 1,75 % (OpenFisca, 2026)."""
    assert ac.taux_prelevements_allocations() == pytest.approx((0.062 + 0.005) * (1 - 0.0175))


def test_parts_de_revalorisation_reproduisent_le_calage() -> None:
    """La revalorisation de 1,9 % au 1er juillet 2023 redonne le tableau 2 de l'Unédic."""
    allocations = chiffrage("chomage_allocations_brutes_2023")
    for rang, cle in ((1, "total_2023"), (2, "total_2024")):
        cout = ac.cout_revalorisation_annee(1.9, rang, 7, allocations)
        attendu = chiffrage(f"chomage_revalorisation_juillet_2023_{cle}") / 1000
        assert cout == pytest.approx(attendu)


def test_revalorisation_en_avril_compte_neuf_mois() -> None:
    juillet = ac.cout_revalorisation_annee(1.0, 1, 7, 10.0)
    avril = ac.cout_revalorisation_annee(1.0, 1, 4, 10.0)
    assert avril == pytest.approx(juillet * 9 / 6)


def test_au_dela_de_la_deuxieme_annee_seuls_les_parametres_fixes_restent() -> None:
    premiere, deuxieme, suivantes = ac.parts_revalorisation()
    assert 0 < suivantes < premiere < deuxieme


def test_rapport_des_hypotheses_de_l_unedic() -> None:
    """La plage de l'hypothèse redonne les deux chiffrages de l'avenant de 2026."""
    haut = chiffrage("chomage_avenant_rci_croisiere_sans_prolongement")
    bas = chiffrage("chomage_avenant_rci_croisiere_prolongement_total")
    milieu = (haut + bas) / 2
    plage = hypothese(ac.HYPOTHESE_RAPPORT_DUREE).plage
    assert plage.basse == pytest.approx(bas / milieu, abs=1e-3)
    assert plage.haute == pytest.approx(haut / milieu, abs=1e-3)


def test_montee_en_charge_de_la_duree() -> None:
    """Profil de la réforme de 2023 : 0 ; 0,7 ; 3,0 puis 4,5 Md€ (plein effet)."""
    parts = [ac.montee_en_charge_duree(r, 4) for r in range(1, 6)]
    assert parts == pytest.approx([0.0, 0.7 / 4.5, 3.0 / 4.5, 1.0, 1.0])
    assert ac.montee_en_charge_duree(4, 5) == pytest.approx(3.0 / 4.5)


def test_reforme_2023_reproduite_avant_retours() -> None:
    """Sans retour de prélèvements, -0,25 de coefficient redonne 4,2 Md€ de 2027 en croisière."""
    economie, baisse = ac.economie_reforme_2023()
    assert baisse == pytest.approx(0.25)
    assert economie == pytest.approx(4.2)


@pytest.mark.parametrize("levier", sc.LEVIERS_CHOMAGE)
def test_lineaire_dans_la_valeur(levier: str) -> None:
    """Le site multiplie la réponse d'une unité : l'écart doit être linéaire."""
    basse, haute = sc.bornes_levier(levier)
    un = sc.scenario([sc.Mesure(levier, haute / 2, ANNEE)])
    deux = sc.scenario([sc.Mesure(levier, haute, ANNEE)])
    for a, b in zip(un, deux, strict=True):
        assert 2 * a.ecart_dette.central == pytest.approx(b.ecart_dette.central, abs=1e-12)


def test_sens_des_effets() -> None:
    """Hausse du taux : solde amélioré ; revalorisation et durée plus longue : solde dégradé."""
    fin = sc.ANNEE_PREMIERE_MESURE + 5
    for levier, signe in (
        (sc.LEVIER_CHOMAGE_CONTRIBUTION, 1),
        (sc.LEVIER_CHOMAGE_REVALORISATION, -1),
        (sc.LEVIER_CHOMAGE_DUREE, -1),
    ):
        r = {a.annee: a for a in sc.scenario([sc.Mesure(levier, 0.1, ANNEE)])}
        assert signe * r[fin].ecart_solde_primaire.central > 0


def test_aucun_effet_de_la_duree_l_annee_d_entree() -> None:
    effet = sc.effet_solde(sc.Mesure(sc.LEVIER_CHOMAGE_DUREE, 0.1, ANNEE))
    assert effet.central == 0.0
