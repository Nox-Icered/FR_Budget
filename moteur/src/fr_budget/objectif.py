"""Mode « atteindre un objectif » : valeur d'un levier qui amène la dette ou le solde primaire à
une cible une année donnée, par dichotomie sur le calcul du scénario (même règle que le site,
``web/lib/objectif.ts`` ; sert à l'API publique). Aucun levier n'est proposé ni classé :
l'utilisateur choisit lequel régler.
"""

from __future__ import annotations

from dataclasses import dataclass

from fr_budget import scenario as sc
from fr_budget.baseline import ANNEE_FIN
from fr_budget.fourchette import Fourchette

INDICATEURS = ("dette", "solde_primaire")
BORNES = ("bas", "central", "haut")
ITERATIONS = 60


@dataclass(frozen=True)
class Objectif:
    indicateur: str
    annee: int
    cible: float
    """En % du PIB."""


@dataclass(frozen=True)
class Solution:
    par_borne: dict[str, float | None]
    """Valeur du levier qui atteint la cible sur la trajectoire de chaque borne ; ``None`` si la
    cible est hors de portée dans les bornes du levier."""
    sans_mesure: float
    """Niveau de l'indicateur sans mesure, l'année de l'objectif (trajectoire centrale)."""


def _verifier(levier: str, entree: int, objectif: Objectif) -> None:
    if objectif.indicateur not in INDICATEURS:
        msg = f"indicateur inconnu : {objectif.indicateur}"
        raise ValueError(msg)
    if levier not in sc.LEVIERS_REGISTRE:
        msg = f"levier inconnu : {levier}"
        raise ValueError(msg)
    if not entree <= objectif.annee <= ANNEE_FIN:
        msg = f"année de l'objectif hors de {entree}-{ANNEE_FIN}"
        raise ValueError(msg)


def niveau(levier: str, valeur: float, entree: int, objectif: Objectif, borne: str) -> float:
    """Indicateur l'année de l'objectif, avec le levier réglé à ``valeur``, en % du PIB."""
    mesures = [] if valeur == 0 else [sc.Mesure(levier, valeur, entree)]
    ligne = next(a for a in sc.scenario(mesures) if a.annee == objectif.annee)
    return float(getattr(getattr(ligne, objectif.indicateur), borne))


def _resoudre_borne(levier: str, entree: int, objectif: Objectif, borne: str) -> float | None:
    def f(v: float) -> float:
        return niveau(levier, v, entree, objectif, borne) - objectif.cible

    zero = f(0.0)
    if zero == 0:
        return 0.0
    if levier in sc.LEVIERS_NON_LINEAIRES:
        # Premier cran, en partant de zéro, qui atteint ou dépasse la cible.
        crans = sorted(sc.grille_levier(levier), key=abs)
        return next((v for v in crans if (f(v) > 0) != (zero > 0) or f(v) == 0), None)
    bas, haut = sc.bornes_levier(levier)
    fb, fh = f(bas), f(haut)
    if fb == 0:
        return bas
    if fh == 0:
        return haut
    if (fb > 0) == (fh > 0):
        return None
    for _ in range(ITERATIONS):
        milieu = (bas + haut) / 2
        fm = f(milieu)
        if fm == 0:
            return milieu
        if (fm > 0) == (fb > 0):
            bas, fb = milieu, fm
        else:
            haut = milieu
    return (bas + haut) / 2


def resoudre(levier: str, entree: int, objectif: Objectif) -> Solution:
    """Valeur du levier qui atteint la cible, pour chaque borne des hypothèses."""
    _verifier(levier, entree, objectif)
    return Solution(
        par_borne={b: _resoudre_borne(levier, entree, objectif, b) for b in BORNES},
        sans_mesure=niveau(levier, 0.0, entree, objectif, "central"),
    )


def fourchette_valeur(s: Solution) -> Fourchette | None:
    """Extrêmes des valeurs trouvées ; ``None`` si la valeur centrale est hors de portée."""
    c = s.par_borne["central"]
    if c is None:
        return None
    autres = [v for b, v in s.par_borne.items() if b != "central" and v is not None]
    return Fourchette(min(c, *autres), c, max(c, *autres))
