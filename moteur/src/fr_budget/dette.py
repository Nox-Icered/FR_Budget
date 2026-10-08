"""Dynamique de la dette publique en ratio de PIB (lot 1.2 du plan).

Formule (CLAUDE.md, « Dynamique de la dette ») :

    d(t+1) = d(t) * (1 + r) / (1 + g) - pb + sfa

- d : dette au sens de Maastricht en ratio de PIB ;
- r : taux d'intérêt apparent (intérêts versés rapportés à la dette de l'année précédente) ;
- g : croissance du PIB en valeur ;
- pb : solde primaire en ratio de PIB (positif pour un excédent) ;
- sfa : ajustement stock-flux en ratio de PIB.

Toutes les grandeurs sont des fractions (0,03 pour 3 %). Le taux apparent suit le profil de
maturité de la dette : chaque année, une part de la dette (titres arrivant à échéance et
nouveaux emprunts) est refinancée au taux de marché, le reste garde son taux. Les valeurs
(part refinancée, taux de marché, croissance) viendront du registre d'hypothèses ; ce module
ne contient que les formules.
"""

from __future__ import annotations

from collections.abc import Sequence


def dette_suivante(d: float, r: float, g: float, pb: float, sfa: float = 0.0) -> float:
    """Dette de l'année suivante, en ratio de PIB."""
    return d * (1 + r) / (1 + g) - pb + sfa


def solde_primaire_stabilisant(d: float, r: float, g: float) -> float:
    """Solde primaire qui maintient le ratio de dette constant (sans ajustement stock-flux)."""
    return d * (r - g) / (1 + g)


def trajectoire_dette(
    d0: float,
    r: Sequence[float],
    g: Sequence[float],
    pb: Sequence[float],
    sfa: Sequence[float] | None = None,
) -> list[float]:
    """Trajectoire du ratio de dette : d0 puis une valeur par année des séries."""
    ajustements = sfa if sfa is not None else [0.0] * len(r)
    if not len(r) == len(g) == len(pb) == len(ajustements):
        msg = "les séries r, g, pb et sfa doivent avoir la même longueur"
        raise ValueError(msg)
    trajectoire = [d0]
    for r_t, g_t, pb_t, sfa_t in zip(r, g, pb, ajustements, strict=True):
        trajectoire.append(dette_suivante(trajectoire[-1], r_t, g_t, pb_t, sfa_t))
    return trajectoire


def taux_apparent_suivant(r_precedent: float, taux_marche: float, part_refinancee: float) -> float:
    """Taux apparent de l'année suivante.

    La part refinancée de la dette (titres arrivés à échéance et emprunts nouveaux, rapportés à
    la dette) prend le taux de marché ; le reste garde le taux apparent précédent.
    """
    if not 0.0 <= part_refinancee <= 1.0:
        msg = f"la part refinancée doit être comprise entre 0 et 1 : {part_refinancee}"
        raise ValueError(msg)
    return (1 - part_refinancee) * r_precedent + part_refinancee * taux_marche


def ajustement_stock_flux_implicite(
    d_precedent: float, d: float, r: float, g: float, pb: float
) -> float:
    """Ajustement stock-flux qui fait coïncider la formule avec une dette observée."""
    return d - d_precedent * (1 + r) / (1 + g) + pb
