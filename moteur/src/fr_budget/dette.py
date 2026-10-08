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

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage, hypothese

HYPOTHESE_EXPOSITION = "dette_fraction_premiere_annee_exposee"
UN_POINT = 0.01


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


def part_refinancee(
    emissions_long_terme: float,
    encours_court_terme: float,
    variation_court_terme: float,
    encours: float,
) -> float:
    """Part de la dette refinancée dans l'année, au taux de marché de l'année.

    Émissions à moyen et long terme, plus renouvellement de tout l'encours à court terme (titres
    de moins d'un an) et sa variation, rapportés à l'encours de début d'année.
    """
    return (emissions_long_terme + encours_court_terme + variation_court_terme) / encours


def surcout_choc_taux(
    encours: float, part: float, choc: float, annee: int, fraction_premiere_annee: float
) -> float:
    """Surcoût d'intérêts, l'année ``annee`` (1 = première), d'un choc de taux sur toute la courbe.

    Application de ``taux_apparent_suivant`` à un écart de taux : après k années de
    refinancement à la part constante s, l'écart de taux apparent vaut
    choc * (1 - (1 - s) ** k). La première année ne compte que ``fraction_premiere_annee``
    d'exposition (émissions étalées dans l'année). L'encours est tenu constant.
    """
    exposition = annee - 1 + fraction_premiere_annee
    return float(encours * choc * (1 - (1 - part) ** exposition))


def surcout_choc_taux_etat(annee: int) -> Fourchette:
    """Surcoût, en Md€, d'un choc de +1 point au 1er janvier 2027 sur la dette négociable de l'État.

    Données : PLF 2027, PAP « Engagements financiers de l'État » (chiffrages
    ``dette_etat_*``). Encours fin 2026 = encours nominal fin 2025 + émissions à moyen et long
    terme 2026 - amortissements nominaux 2026 + variation des titres courts 2026. Part
    refinancée 2027 = (émissions 2027 + titres courts fin 2026 + leur variation 2027) / encours
    fin 2026. Fourchette : plage de l'hypothèse ``dette_fraction_premiere_annee_exposee``.
    """
    court_terme_fin_2026 = chiffrage("dette_etat_btf_fin_2025") + chiffrage(
        "dette_etat_variation_btf_2026"
    )
    encours_fin_2026 = (
        chiffrage("dette_etat_negociable_nominal_fin_2025")
        + chiffrage("dette_etat_emissions_mlt_2026")
        - chiffrage("dette_etat_amortissements_mlt_nominal_2026")
        + chiffrage("dette_etat_variation_btf_2026")
    )
    part = part_refinancee(
        chiffrage("dette_etat_emissions_mlt_2027"),
        court_terme_fin_2026,
        chiffrage("dette_etat_variation_btf_2027"),
        encours_fin_2026,
    )
    h = hypothese(HYPOTHESE_EXPOSITION)
    calcul = {
        f: surcout_choc_taux(encours_fin_2026, part, UN_POINT, annee, f)
        for f in (h.valeur_centrale, h.plage.basse, h.plage.haute)
    }
    return encadrer(calcul[h.valeur_centrale], [calcul[h.plage.basse], calcul[h.plage.haute]])
