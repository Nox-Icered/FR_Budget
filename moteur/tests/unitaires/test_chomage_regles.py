"""Assurance chômage, deuxième étape : condition d'affiliation et dégressivité (calées sur les
études d'impact de l'Unédic de 2019 et de 2021)."""

from __future__ import annotations

import pytest

from fr_budget import scenario as sc
from fr_budget.agrege import assurance_chomage as ac
from fr_budget.registres.acces import chiffrage

ANNEE = 2027


def test_affiliation_cout_d_un_mois_de_baisse() -> None:
    f = ac.effet_affiliation_mois()
    assert f.bas <= f.central <= f.haut < 0
    ecart = ac.ecart_affiliation_mois()
    assert ecart == chiffrage("chomage_affiliation_mois_apres_2019") - chiffrage(
        "chomage_affiliation_mois_avant_2019"
    )
    # Brut, avant le retour de CSG et de CRDS : l'économie de 2021 ramenée à un mois.
    brut = ac.economie_affiliation_brute()
    assert brut.central == pytest.approx(
        ac.vers_euros_2025_depuis(chiffrage("chomage_affiliation_croisiere_2021") / 1000, 2023)
        / ecart
    )
    assert -f.central < brut.central


def test_degressivite_cout_d_un_point() -> None:
    f = ac.effet_degressivite_point()
    assert f.bas <= f.central <= f.haut < 0
    brut = ac.economie_degressivite_brute()
    assert brut.central * chiffrage("chomage_degressivite_taux") == pytest.approx(
        ac.vers_euros_2025_depuis(chiffrage("chomage_degressivite_croisiere_2021") / 1000, 2023)
    )


def test_premiere_annee() -> None:
    assert ac.part_premiere_annee_affiliation() == pytest.approx(0.9)
    assert 0.5 < ac.part_premiere_annee_degressivite() < 0.6


@pytest.mark.parametrize("levier", sc.LEVIERS_CHOMAGE_REGLES)
def test_leviers_dans_le_scenario(levier: str) -> None:
    basse, haute = sc.bornes_levier(levier)
    assert basse == 0 and haute >= 1
    sc.reponse_lineaire(levier, ANNEE)
    assert sc.levier_registre(levier) == "assurance_chomage"
    e = {
        a.annee: a.ecart_solde_primaire.central
        for a in sc.scenario([sc.Mesure(levier, 1.0, ANNEE)])
    }
    assert e[ANNEE + 1] < e[ANNEE] < 0


@pytest.mark.parametrize("levier", sc.LEVIERS_CHOMAGE_REGLES)
def test_lineaire_dans_la_valeur(levier: str) -> None:
    _, haute = sc.bornes_levier(levier)
    un = sc.scenario([sc.Mesure(levier, haute / 2, ANNEE)])
    deux = sc.scenario([sc.Mesure(levier, haute, ANNEE)])
    for a, b in zip(un, deux, strict=True):
        assert 2 * a.ecart_dette.central == pytest.approx(b.ecart_dette.central, abs=1e-12)
