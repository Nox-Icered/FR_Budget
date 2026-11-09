"""Mode « atteindre un objectif » côté moteur (fr_budget.objectif), même règle que le site
(web/lib/objectif.ts)."""

from __future__ import annotations

import pytest

from fr_budget import objectif as ob
from fr_budget import scenario as sc

ENTREE = 2027


def _cible(levier: str, ecart: float, indicateur: str = "dette", annee: int = 2040) -> ob.Objectif:
    sans = ob.niveau(levier, 0.0, ENTREE, ob.Objectif(indicateur, annee, 0.0), "central")
    return ob.Objectif(indicateur, annee, sans + ecart)


@pytest.mark.parametrize("levier", ["tva_taux_normal", "csg_activite", "ondam_progression"])
def test_la_valeur_trouvee_redonne_la_cible(levier: str) -> None:
    o = _cible(levier, -0.2)
    s = ob.resoudre(levier, ENTREE, o)
    v = s.par_borne["central"]
    assert v is not None
    assert ob.niveau(levier, v, ENTREE, o, "central") == pytest.approx(o.cible, abs=1e-6)
    f = ob.fourchette_valeur(s)
    assert f is not None and f.bas <= f.central <= f.haut


def test_solde_primaire() -> None:
    o = _cible("tva_taux_normal", 0.2, "solde_primaire", 2030)
    v = ob.resoudre("tva_taux_normal", ENTREE, o).par_borne["central"]
    assert v is not None and v > 0


def test_cible_hors_de_portee() -> None:
    o = ob.Objectif("dette", 2040, 0.0)
    s = ob.resoudre("accise_gazole", ENTREE, o)
    assert s.par_borne["central"] is None
    assert ob.fourchette_valeur(s) is None


def test_levier_a_crans_cran_qui_atteint_la_cible() -> None:
    levier = sc.LEVIER_RETRAITES_AGE_LEGAL
    o = _cible(levier, -0.5)
    v = ob.resoudre(levier, ENTREE, o).par_borne["central"]
    assert v is not None and v in sc.grille_levier(levier)
    assert ob.niveau(levier, v, ENTREE, o, "central") <= o.cible + 1e-9


def test_entrees_refusees() -> None:
    with pytest.raises(ValueError, match="indicateur"):
        ob.resoudre("tva_taux_normal", ENTREE, ob.Objectif("chomage", 2040, 100.0))
    with pytest.raises(ValueError, match="année"):
        ob.resoudre("tva_taux_normal", ENTREE, ob.Objectif("dette", 2026, 100.0))
    with pytest.raises(ValueError, match="levier"):
        ob.resoudre("inconnu", ENTREE, ob.Objectif("dette", 2040, 100.0))
