"""Crédits par mission du budget général de l'État : assiette du levier et exécution (lot 2.5).

Données (``data/processed/credits_missions/``, script ``pipelines/credits_missions/extraire.py``) :

- crédits de paiement du PLF 2026 par programme, « PLF 2026 - Budget vert » (direction du
  Budget) : hors charge de la dette et hors remboursements et dégrèvements, hors cotisations
  au compte d'affectation spéciale « Pensions » dans les crédits de personnel ;
- crédits votés en LFI et dépenses constatées par programme, annexe 1 des projets de loi
  relatifs aux résultats de la gestion (PLRG) 2023, 2024 et 2025.

Périmètre du levier (décisions du mainteneur du 9 octobre 2026, options (a)) : programmes du
budget général (ceux de l'annexe 1 des PLRG), hors mission « Relations avec les collectivités
territoriales » (levier des dotations aux collectivités), hors « Crédits non répartis »
(provision répartie en cours d'année entre les autres missions) et hors « Régimes sociaux et
de retraite » (subventions aux régimes spéciaux, levier de l'indexation des pensions ;
décision du mainteneur du 9 octobre 2026). Les pensions de l'État
(compte d'affectation spéciale), les prélèvements sur recettes au profit des collectivités et
de l'Union européenne, les budgets annexes et les autres comptes spéciaux ne sont pas dans le
budget général. Les crédits de personnel restent dans chaque mission (option 2 (a)).
"""

from __future__ import annotations

import csv
import re
import statistics
import unicodedata
from dataclasses import dataclass
from functools import cache

from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "credits_missions"
FICHIER_PLF = DOSSIER / "plf2026_programmes.csv"
FICHIER_PLRG = DOSSIER / "plrg_programmes.csv"
EXERCICES_PLRG = (2023, 2024, 2025)
MISSIONS_EXCLUES = (
    "Relations avec les collectivités territoriales",
    "Crédits non répartis",
    "Régimes sociaux et de retraite",
)
# Dans les PLRG : missions hors du budget vert (remboursements et dégrèvements) ou exclues.
MISSIONS_EXCLUES_PLRG = (*MISSIONS_EXCLUES, "Remboursements et dégrèvements")
ANNEE_CREDITS = 2026
EUROS_PAR_MILLIARD = 1e9
# Quantiles des écarts d'exécution par mission retenus pour la plage (10e et 90e centiles).
DECILES = 10
DECILE_BAS = 0
DECILE_HAUT = 8


@cache
def _plf() -> list[dict[str, str]]:
    with FICHIER_PLF.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def _plrg() -> list[dict[str, str]]:
    with FICHIER_PLRG.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def programmes_budget_general() -> frozenset[str]:
    """Numéros des programmes du budget général (annexe 1 des PLRG 2023 à 2025)."""
    return frozenset(r["programme"] for r in _plrg())


def identifiant(mission: str) -> str:
    """Identifiant ASCII d'une mission (minuscules, mots séparés par « _ »)."""
    sans_accents = unicodedata.normalize("NFKD", mission).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sans_accents.lower()).strip("_")


@dataclass(frozen=True)
class Mission:
    """Mission du levier : crédits de paiement demandés au PLF 2026, en euros."""

    identifiant: str
    libelle: str
    credits: float


@cache
def missions() -> list[Mission]:
    """Missions du levier, par crédits décroissants ; seules celles dotées en 2026."""
    sommes: dict[str, float] = {}
    for r in _plf():
        if r["programme"] in programmes_budget_general() and r["mission"] not in MISSIONS_EXCLUES:
            sommes[r["mission"]] = sommes.get(r["mission"], 0.0) + float(r["plf_2026"])
    liste = [Mission(identifiant(m), m, v) for m, v in sommes.items() if v > 0]
    if len({m.identifiant for m in liste}) != len(liste):
        msg = "deux missions ont le même identifiant"
        raise ValueError(msg)
    return sorted(liste, key=lambda m: -m.credits)


def mission(ident: str) -> Mission:
    for m in missions():
        if m.identifiant == ident:
            return m
    msg = f"mission absente du levier : {ident}"
    raise ValueError(msg)


def total_credits() -> float:
    """Crédits de paiement du PLF 2026 de toutes les missions du levier, en euros."""
    return sum(m.credits for m in missions())


@cache
def programmes_du_levier() -> frozenset[str]:
    """Programmes des missions du levier au PLF 2026."""
    return frozenset(
        r["programme"]
        for r in _plf()
        if r["programme"] in programmes_budget_general() and r["mission"] not in MISSIONS_EXCLUES
    )


def execution(exercice: int) -> dict[str, tuple[float, float]]:
    """(LFI, dépenses constatées) par mission, en euros, programmes du levier (PLRG).

    Les programmes absents du PLF 2026 (clos, ou charge de la dette) ne sont pas comptés.
    """
    resultat: dict[str, tuple[float, float]] = {}
    for r in _plrg():
        if (
            int(r["exercice"]) != exercice
            or r["programme"] not in programmes_du_levier()
            or r["mission"] in MISSIONS_EXCLUES_PLRG
        ):
            continue
        lfi, constatees = resultat.get(r["mission"], (0.0, 0.0))
        resultat[r["mission"]] = (
            lfi + float(r["lfi"]),
            constatees + float(r["depenses_constatees"]),
        )
    return resultat


def total_execution(exercice: int) -> tuple[float, float]:
    """(LFI, dépenses constatées) de toutes les missions du levier, en euros."""
    e = execution(exercice).values()
    return sum(v[0] for v in e), sum(v[1] for v in e)


def ecarts_execution() -> list[float]:
    """Écart relatif (constaté - LFI) / LFI par mission et par exercice (2023 à 2025)."""
    return [
        (constatees - lfi) / lfi
        for exercice in EXERCICES_PLRG
        for lfi, constatees in execution(exercice).values()
        if lfi > 0
    ]


def plage_ecart_execution() -> tuple[float, float]:
    """10e et 90e centiles des écarts d'exécution par mission."""
    q = statistics.quantiles(ecarts_execution(), n=DECILES)
    return q[DECILE_BAS], q[DECILE_HAUT]
