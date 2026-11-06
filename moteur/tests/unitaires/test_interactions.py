"""Combinaison de mesures sans double compte : termes croisés (fr_budget.agrege.interactions)."""

from __future__ import annotations

import pytest

from fr_budget import scenario as sc
from fr_budget.agrege import interactions as it
from fr_budget.agrege import remunerations

ENTREE = 2027
POINT = "remunerations_point_indice"
EFFECTIFS = "remunerations_effectifs"
CSG_ACTIVITE = "csg_activite"
INDEXATION = "indexation_pensions_prestations"
CSG_RETRAITES = "csg_retraites"
PAIRES = [(POINT, CSG_ACTIVITE), (EFFECTIFS, CSG_ACTIVITE), (INDEXATION, CSG_RETRAITES)]


def _ecart(mesures: list[sc.Mesure], borne: str = "central") -> list[float]:
    return [getattr(a.ecart_solde_primaire, borne) for a in sc.scenario(mesures)]


def _croise(a: str, x: float, b: str, y: float, borne: str = "central") -> list[float]:
    """Écart de solde de la combinaison moins la somme des écarts de chaque mesure."""
    ensemble = _ecart([sc.Mesure(a, x, ENTREE), sc.Mesure(b, y, ENTREE)], borne)
    seul_a = _ecart([sc.Mesure(a, x, ENTREE)], borne)
    seul_b = _ecart([sc.Mesure(b, y, ENTREE)], borne)
    return [e - u - v for e, u, v in zip(ensemble, seul_a, seul_b, strict=True)]


@pytest.mark.parametrize(("a", "b"), PAIRES)
def test_terme_croise_proportionnel_au_produit(a: str, b: str) -> None:
    un = _croise(a, 1.0, b, 1.0)
    autre = _croise(a, -2.0, b, 1.5)
    assert max(abs(v) for v in un) > 0
    for u, v in zip(un, autre, strict=True):
        assert v == pytest.approx(-3.0 * u, abs=1e-12)


@pytest.mark.parametrize(("a", "b"), PAIRES)
def test_terme_croise_nul_si_une_mesure_a_zero(a: str, b: str) -> None:
    assert max(abs(v) for v in _croise(a, 1.0, b, 0.0)) == 0.0
    assert max(abs(v) for v in _croise(a, 0.0, b, 1.0)) == 0.0


def test_terme_croise_symetrique() -> None:
    m1 = [sc.Mesure(POINT, 2.0, ENTREE), sc.Mesure(CSG_ACTIVITE, 1.0, ENTREE)]
    assert _ecart(m1) == _ecart(list(reversed(m1)))


def test_hausse_du_point_et_de_la_csg_ameliore_le_solde() -> None:
    """La CSG prélevée sur la hausse des traitements revient aux administrations publiques."""
    assert all(v >= 0 for v in _croise(POINT, 1.0, CSG_ACTIVITE, 1.0))
    assert any(v > 0 for v in _croise(INDEXATION, 1.0, CSG_RETRAITES, 1.0))


def test_ordre_de_grandeur_borne() -> None:
    """L'assiette de CSG ajoutée ne dépasse pas le coût brut de la hausse : le terme croisé
    d'un pour cent et d'un point est au plus 1 % du coût brut d'un pour cent."""
    for levier, cle in ((POINT, remunerations.POINT), (EFFECTIFS, remunerations.EFFECTIFS)):
        k = it.rendement_unitaire(it.identifiant(levier, CSG_ACTIVITE))
        assert 0 < k.bas <= k.central <= k.haut
        assert k.haut <= remunerations.cout_brut_un_pourcent(cle) / 100
    k = it.rendement_unitaire(it.identifiant(INDEXATION, CSG_RETRAITES))
    assert 0 < k.bas <= k.central <= k.haut


def test_fourchette_du_terme_croise_dans_les_bornes() -> None:
    bas = _croise(POINT, 2.0, CSG_ACTIVITE, 1.0, "bas")
    haut = _croise(POINT, 2.0, CSG_ACTIVITE, 1.0, "haut")
    central = _croise(POINT, 2.0, CSG_ACTIVITE, 1.0)
    for b, c, h in zip(bas, central, haut, strict=True):
        assert b - 1e-12 <= c <= h + 1e-12


def test_mesure_interne_refusee_en_entree() -> None:
    with pytest.raises(ValueError, match="interne"):
        sc.scenario([sc.Mesure(it.identifiant(POINT, CSG_ACTIVITE), 1.0, ENTREE)])


def test_interactions_non_chiffrees_nomment_des_leviers_connus() -> None:
    for paire in it.NON_CHIFFREES:
        assert len(paire.leviers_a) > 0 and len(paire.leviers_b) > 0
        for levier in (*paire.leviers_a, *paire.leviers_b):
            assert sc.levier_registre(levier) is not None, levier
    chiffrees = {frozenset(p) for p in it.CHIFFREES.values()}
    for paire in it.NON_CHIFFREES:
        for a in paire.leviers_a:
            for b in paire.leviers_b:
                assert frozenset((a, b)) not in chiffrees
