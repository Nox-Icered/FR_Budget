"""Effet de croissance d'une mesure (interrupteur du site, désactivé par défaut ; lot 3.2).

Modèle simple de l'OFCE (Policy brief n° 146, juillet 2025, encadré 3, page 15) :

- écart de production : OG(t) = rho * OG(t-1) + m * IB(t), où IB(t) est l'impulsion
  budgétaire, opposée de la variation du solde primaire due à la mesure ;
- solde primaire : la mesure, plus alpha * OG(t) (recettes perdues quand l'activité ralentit) ;
- dette en ratio du PIB : le PIB effectif vaut le PIB de la baseline fois (1 + OG). Au premier
  ordre, d(t) = d(t-1) * (1 + r) / (1 + g) * (1 + OG(t-1) - OG(t)) - pb(t) + sfa(t), la dette
  de l'année précédente étant celle de la baseline dans le terme d'écart de production (le
  calcul reste linéaire dans la valeur des leviers, ce dont le site statique a besoin).

Paramètres (registre d'hypothèses, choix du lot 3.2 à relire, ``docs/fiches/croissance.md``) :

- multiplicateur à un an m par instrument : valeur centrale = variante de Mésange 2017 (Insee
  et DG Trésor) la plus proche ; plage = Mésange et multiplicateurs de l'OFCE (0,5 pour les
  recettes, 1 pour les dépenses) ;
- rho = 0,7 et alpha = 0,5 : valeurs usuelles citées par l'OFCE, sans plage.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import replace

from fr_budget.baseline import AnneeBaseline
from fr_budget.dette import dette_suivante
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import hypothese

DEPENSES = "depenses"
PRESTATIONS = "prestations"
TVA = "tva"
ACCISES = "accises"
COTISATIONS_EMPLOYEURS = "cotisations_employeurs"
CSG = "csg"
IMPOT_REVENU = "impot_revenu"
AUTRES_PRELEVEMENTS = "autres_prelevements"
CATEGORIES = (
    DEPENSES,
    PRESTATIONS,
    TVA,
    ACCISES,
    COTISATIONS_EMPLOYEURS,
    CSG,
    IMPOT_REVENU,
    AUTRES_PRELEVEMENTS,
)
PREFIXE_HYPOTHESE = "croissance_multiplicateur_"
HYPOTHESE_PERSISTANCE = "croissance_persistance_ecart_production"
HYPOTHESE_EFFET_SOLDE = "croissance_effet_ecart_production_solde"
POURCENT = 100.0


def multiplicateur(categorie: str) -> Fourchette:
    """Multiplicateur à un an d'une catégorie d'instruments (registre d'hypothèses)."""
    h = hypothese(PREFIXE_HYPOTHESE + categorie)
    return encadrer(h.valeur_centrale, [h.plage.basse, h.plage.haute])


def persistance() -> float:
    """rho : part de l'écart de production qui subsiste l'année suivante (OFCE)."""
    return hypothese(HYPOTHESE_PERSISTANCE).valeur_centrale


def effet_sur_le_solde() -> float:
    """alpha : effet d'un point d'écart de production sur le solde, en point de PIB (OFCE)."""
    return hypothese(HYPOTHESE_EFFET_SOLDE).valeur_centrale


def impulsions(effets: Mapping[int, float], annees: Sequence[int]) -> list[float]:
    """Impulsion budgétaire de chaque année : opposée de la variation de l'effet sur le solde."""
    return [-(effets.get(a, 0.0) - effets.get(a - 1, 0.0)) for a in annees]


def ecart_production(
    effets: Mapping[int, float], annees: Sequence[int], m: float, rho: float
) -> list[float]:
    """Écart de production dû à la mesure, en points de PIB, nul avant la première année."""
    resultat: list[float] = []
    precedent = 0.0
    for ib in impulsions(effets, annees):
        precedent = rho * precedent + m * ib
        resultat.append(precedent)
    return resultat


def trajectoire_avec_croissance(
    trajectoire: Sequence[AnneeBaseline],
    effets: Mapping[int, float],
    ecart: Sequence[float],
    alpha: float,
) -> list[AnneeBaseline]:
    """Trajectoire avec l'effet de la mesure sur le solde et l'écart de production ``ecart``.

    La première année est reprise telle quelle, comme dans ``scenario.trajectoire_avec_effet``,
    qu'on retrouve quand l'écart de production est nul.
    """
    lignes = [trajectoire[0]]
    for i in range(1, len(trajectoire)):
        a = trajectoire[i]
        pb = a.solde_primaire + effets.get(a.annee, 0.0) + alpha * ecart[i]
        r = a.taux_apparent / POURCENT
        g = a.croissance_nominale / POURCENT
        effet_pib = trajectoire[i - 1].dette * (1 + r) / (1 + g) * (ecart[i - 1] - ecart[i])
        dette = (
            dette_suivante(lignes[-1].dette, r, g, pb, a.ajustement_stock_flux)
            + effet_pib / POURCENT
        )
        lignes.append(replace(a, dette=dette, solde_primaire=pb))
    return lignes


def provenance(categories: Iterable[str]) -> tuple[list[str], list[str]]:
    """Sources et hypothèses de l'effet de croissance pour ces catégories d'instruments."""
    hypotheses = [PREFIXE_HYPOTHESE + c for c in dict.fromkeys(categories)]
    hypotheses += [HYPOTHESE_PERSISTANCE, HYPOTHESE_EFFET_SOLDE]
    sources: list[str] = []
    for h in hypotheses:
        sources += [s for s in hypothese(h).sources if s not in sources]
    return sources, hypotheses
