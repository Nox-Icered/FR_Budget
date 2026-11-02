"""Projection de la dette de la Commission européenne à politique inchangée, pour comparaison.

Source : Debt Sustainability Monitor 2025 (février 2026), fiche France
(``data/processed/baseline/ce_dsm_2025_france.csv``, ``pipelines/baseline/extraire_dsm.py``).
La Commission ne retient que les mesures votées : le redressement annoncé par le Gouvernement
au-delà de 2026 n'y figure pas. Elle sert de seconde trajectoire de référence, affichée à côté de
la prévision du Gouvernement (``fr_budget.baseline``) ; les leviers ne s'y appliquent pas.

- 2025-2036 : dette publiée, reprise telle quelle (valeur centrale) ;
- après 2036 : prolongement linéaire, qui n'est pas une projection de la Commission (hypothèse
  ``baseline_commission_prolongement_pente``) ;
- fourchette : de la projection centrale au plus élevé des quatre scénarios déterministes de la
  Commission, écart croissant linéairement de 0 en 2026 à sa valeur publiée de 2036 (hypothèse
  ``baseline_commission_ecart_scenarios``).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache

from fr_budget.fourchette import Fourchette
from fr_budget.registres.acces import hypothese
from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "baseline"
FICHIER = DOSSIER / "ce_dsm_2025_france.csv"
FICHIER_SCENARIOS = DOSSIER / "ce_dsm_2025_france_scenarios_2036.csv"
HYPOTHESE_PENTE = "baseline_commission_prolongement_pente"
HYPOTHESE_ECART = "baseline_commission_ecart_scenarios"
SOURCE = "ce_dsm_2025"
ANNEE_DEBUT = 2025
ANNEE_SANS_ECART = 2026
"""Les scénarios déterministes de la Commission s'écartent de la projection centrale à partir
de 2027 : l'écart est nul en 2026."""


@dataclass(frozen=True)
class AnneeCommission:
    annee: int
    dette: Fourchette
    publiee: bool
    """Vrai pour une année publiée par la Commission, faux pour le prolongement."""


@cache
def serie_publiee() -> dict[int, float]:
    """Dette brute publiée par la Commission, en % du PIB, par année."""
    with FICHIER.open(encoding="utf-8") as f:
        return {int(r["annee"]): float(r["dette"]) for r in csv.DictReader(f)}


@cache
def scenarios_2036() -> dict[str, float]:
    """Dette en 2036 des cinq scénarios déterministes publiés, en % du PIB."""
    with FICHIER_SCENARIOS.open(encoding="utf-8") as f:
        return {r["scenario"]: float(r["dette_2036"]) for r in csv.DictReader(f)}


def annee_derniere_publiee() -> int:
    return max(serie_publiee())


def pentes_prolongement() -> tuple[float, float, float]:
    """Hausse annuelle de la dette après la dernière année publiée (basse, centrale, haute) :
    moyenne des six et des trois dernières années, plus forte hausse annuelle des six dernières."""
    s = serie_publiee()
    fin = annee_derniere_publiee()
    hausses = [s[a] - s[a - 1] for a in range(fin - 5, fin + 1)]
    return (s[fin] - s[fin - 6]) / 6, (s[fin] - s[fin - 3]) / 3, max(hausses)


def ecart_haut_publie() -> float:
    """Écart du scénario le plus élevé à la projection centrale en 2036, en points de PIB."""
    scenarios = scenarios_2036()
    return max(scenarios.values()) - scenarios["central"]


def trajectoire(annee_fin: int) -> list[AnneeCommission]:
    """Dette de 2025 à ``annee_fin`` : publiée jusqu'en 2036, prolongée ensuite."""
    s = serie_publiee()
    fin = annee_derniere_publiee()
    pente = hypothese(HYPOTHESE_PENTE)
    ecart_2036 = hypothese(HYPOTHESE_ECART).plage.haute
    rythme_ecart = ecart_2036 / (fin - ANNEE_SANS_ECART)
    lignes = []
    for annee in range(ANNEE_DEBUT, annee_fin + 1):
        ecart = rythme_ecart * max(0, annee - ANNEE_SANS_ECART)
        if annee <= fin:
            central = s[annee]
            bas, haut = central, central + ecart
        else:
            n = annee - fin
            central = s[fin] + n * pente.valeur_centrale
            bas = s[fin] + n * pente.plage.basse
            haut = s[fin] + n * pente.plage.haute + ecart
        lignes.append(AnneeCommission(annee, Fourchette(bas, central, haut), annee <= fin))
    return lignes
