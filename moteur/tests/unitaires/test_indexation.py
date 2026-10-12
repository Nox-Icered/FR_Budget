"""Tests du levier « indexation des pensions et prestations » (fr_budget.agrege.indexation)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import indexation as ix

JANVIER = 1
AVRIL = 4


def test_les_blocs_existent_dans_les_comptes_de_2024() -> None:
    for bloc in ix.BLOCS:
        assert ix.montant(bloc, ix.ANNEE_COMPTES) > 0, bloc


def test_aucun_code_dans_deux_blocs() -> None:
    codes = [c for b in ix.BLOCS.values() for c in b.codes]
    assert len(codes) == len(set(codes))


def test_pensions_complementaires_exclues() -> None:
    codes = {c for b in ix.BLOCS.values() for c in b.codes}
    assert not codes & set(ix.CODES_EXCLUS)


def test_dates_de_revalorisation() -> None:
    assert ix.mois_revalorisation(ix.PENSIONS) == JANVIER
    assert ix.mois_revalorisation(ix.FAMILLE) == AVRIL
    assert ix.mois_revalorisation("rsa") == AVRIL


def test_part_de_la_premiere_annee() -> None:
    assert ix.part_premiere_annee(ix.PENSIONS) == 1.0
    assert ix.part_premiere_annee(ix.FAMILLE) == pytest.approx(9 / 12)


def test_montant_suit_le_pib_nominal() -> None:
    rapport = ix.montant(ix.PENSIONS, 2025) / ix.montant(ix.PENSIONS, 2024)
    assert rapport == pytest.approx(ix.facteur_pib(2025))


@pytest.mark.parametrize("foyer", ix.FOYERS)
def test_retours_sur_les_pensions_ordonnes(foyer: str) -> None:
    retour = ix.retour_pension(foyer)
    assert 0 < retour.prelevements_sociaux < retour.total < 1


def test_lectures_ordonnees() -> None:
    brut = ix.cout_mesure(0.01, 2026, tuple(ix.BLOCS), ix.BRUT)
    net_ps = ix.cout_mesure(0.01, 2026, tuple(ix.BLOCS), ix.NET_PRELEVEMENTS_SOCIAUX)
    net = ix.cout_mesure(0.01, 2026, tuple(ix.BLOCS), ix.NET_TOTAL)
    assert brut > net_ps > net > 0


def test_cout_net_d_un_point_en_fourchette() -> None:
    f = ix.cout_un_point()
    assert 0 < f.bas <= f.central <= f.haut < ix.cout_brut_un_point()
