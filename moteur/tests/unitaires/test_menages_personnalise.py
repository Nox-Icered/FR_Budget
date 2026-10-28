from __future__ import annotations

import pytest

from fr_budget.menages import personnalise as p
from fr_budget.menages import types as t


def test_meme_cascade_que_le_menage_type_au_smic() -> None:
    brut = t.brut_mensuel(t.SMIC, t.ANNEE)
    saisi = p.MenageSaisi((p.AdulteSaisi("salarie", brut, 1995),))
    assert p.calculer(saisi) == t.cascade_annuelle("celibataire_smic")


def test_adulte_seul_avec_enfant_est_parent_isole() -> None:
    saisi = p.MenageSaisi((p.AdulteSaisi("salarie", 2000, 1990),), (2019,))
    assert p.profil(saisi).parent_isole
    couple = p.MenageSaisi(
        (p.AdulteSaisi("salarie", 2000, 1990), p.AdulteSaisi("retraite", 1200, 1955)), (2019,)
    )
    assert not p.profil(couple).parent_isole


def test_statuts_traduits() -> None:
    saisi = p.MenageSaisi(
        (p.AdulteSaisi("retraite", 1500, 1955), p.AdulteSaisi("independant", 2000, 1975))
    )
    adultes = p.profil(saisi).adultes
    assert adultes[0].retraite and adultes[0].montant_mensuel == 1500
    assert adultes[1].independant


@pytest.mark.parametrize(
    "saisi",
    [
        p.MenageSaisi(()),
        p.MenageSaisi(tuple(p.AdulteSaisi("salarie", 2000, 1990) for _ in range(3))),
        p.MenageSaisi((p.AdulteSaisi("chomeur", 2000, 1990),)),
        p.MenageSaisi((p.AdulteSaisi("salarie", -1, 1990),)),
        p.MenageSaisi((p.AdulteSaisi("salarie", 2000, 2020),)),
        p.MenageSaisi((p.AdulteSaisi("retraite", 2000, 1950, cadre=True),)),
        p.MenageSaisi((p.AdulteSaisi("salarie", 2000, 1990),), (1980,)),
        p.MenageSaisi((p.AdulteSaisi("salarie", 2000, 1990),), tuple([2015] * 9)),
    ],
)
def test_saisie_invalide(saisi: p.MenageSaisi) -> None:
    with pytest.raises(p.SaisieInvalideError):
        p.profil(saisi)


def test_message_d_erreur_sans_valeur_saisie() -> None:
    with pytest.raises(p.SaisieInvalideError) as erreur:
        p.profil(p.MenageSaisi((p.AdulteSaisi("salarie", 123456.78, 1990),)))
    assert "123456" not in str(erreur.value)


def test_aucun_cache_sur_le_calcul_d_un_profil_saisi() -> None:
    # Règle 5 : rien de la saisie ne reste en mémoire après le calcul.
    assert not hasattr(t.cascade_profil, "cache_info")
    assert not hasattr(t.rfr_point_fixe, "cache_info")
    assert not hasattr(p.calculer, "cache_info")


def test_minimum_vieillesse_et_allocation_de_base_de_la_paje_comptes() -> None:
    """Revue de code du 28 octobre 2026 : un retraité à faible pension reçoit le minimum
    vieillesse, un parent d'un enfant de moins de trois ans l'allocation de base de la PAJE ;
    les deux étaient calculés par OpenFisca mais absents de la cascade."""
    retraite = p.calculer(p.MenageSaisi((p.AdulteSaisi("retraite", 500.0, 1950),)))
    assert retraite.prestations.get("aspa", 0.0) > 0
    parent = p.calculer(p.MenageSaisi((p.AdulteSaisi("salarie", 2000.0, 1990),), (t.ANNEE - 1,)))
    assert parent.prestations.get("paje_base", 0.0) > 0
