"""Flux du budget de l'État en 2026, pour le diagramme de la page d'accueil (sans calcul).

Données : projet de loi de finances pour 2026, article 48 (équilibre) et état B (crédits de
paiement par mission), et annexe « Évaluation des voies et moyens », tome I (recettes par impôt,
prélèvements sur recettes) ; ``pipelines/budget_etat/extraire_plf2026.py`` →
``data/processed/budget_etat/``.

Les ressources (recettes fiscales nettes par impôt, recettes non fiscales, déficit du budget
général) financent les prélèvements sur recettes (collectivités, Union européenne) et les
dépenses nettes du budget général, réparties par mission. Les deux côtés sont égaux par
construction de l'article 48 : recettes - prélèvements - dépenses = solde du budget général.
Seul calcul : les « autres impôts » sont le complément des recettes fiscales nettes de l'article
48 (en millions d'euros) aux quatre grands impôts du tome I (publiés au dixième de milliard).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache

from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "budget_etat"
ANNEE = 2026
SOURCES = ("plf2026_projet_loi", "plf2026_voies_et_moyens_tome1")
GRANDS_IMPOTS = ("impot_revenu", "tva", "impot_societes", "accises_energies")
PRELEVEMENTS = ("collectivites", "union_europeenne")
MILLIONS_PAR_MILLIARD = 1000.0


@dataclass(frozen=True)
class Flux:
    identifiant: str
    libelle: str | None
    """Libellé publié (missions) ; ``None`` quand le site fournit le libellé."""
    montant: float
    """Milliards d'euros."""


@dataclass(frozen=True)
class BudgetEtat:
    annee: int
    ressources: list[Flux]
    emplois: list[Flux]


def _lire(nom: str) -> list[dict[str, str]]:
    with (DOSSIER / nom).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def budget() -> BudgetEtat:
    """Ressources et emplois du budget de l'État pour 2026, en milliards d'euros."""
    equilibre = {r["ligne"]: float(r["montant_meur"]) for r in _lire("equilibre_2026.csv")}
    recettes = {r["poste"]: float(r["montant_meur"]) for r in _lire("recettes_2026.csv")}
    grands = [Flux(i, None, recettes[i] / MILLIONS_PAR_MILLIARD) for i in GRANDS_IMPOTS]
    autres = equilibre["recettes_fiscales_nettes"] - sum(recettes[i] for i in GRANDS_IMPOTS)
    ressources = [
        *grands,
        Flux("autres_impots", None, autres / MILLIONS_PAR_MILLIARD),
        Flux(
            "recettes_non_fiscales",
            None,
            equilibre["recettes_non_fiscales"] / MILLIONS_PAR_MILLIARD,
        ),
        Flux("deficit", None, -equilibre["solde_budget_general"] / MILLIONS_PAR_MILLIARD),
    ]
    missions = sorted(
        (
            Flux(f"mission_{i}", r["mission"], float(r["credits_paiement_meur"]) / 1000)
            for i, r in enumerate(_lire("missions_2026.csv"))
        ),
        key=lambda f: -f.montant,
    )
    emplois = [
        *(
            Flux(f"prelevement_{p}", None, recettes[f"prelevement_{p}"] / MILLIONS_PAR_MILLIARD)
            for p in PRELEVEMENTS
        ),
        *missions,
    ]
    return BudgetEtat(ANNEE, ressources, emplois)
