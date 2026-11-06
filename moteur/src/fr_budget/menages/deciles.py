"""Répartition de l'effet des mesures par décile de niveau de vie (lot V2 « déciles »).

Plan validé par le responsable du projet le 6 novembre 2026 (``docs/fiches/deciles.md``).

L'effet national d'une mesure (rendement d'une unité du levier, en Md€ de 2025, année pleine ;
``fr_budget.scenario.rendement_unitaire``) est réparti selon la part de chaque décile de niveau de
vie dans l'assiette qu'elle touche. Variation du revenu des ménages = moins l'effet sur le solde
public (une hausse d'impôt réduit le revenu, une hausse de prestation l'augmente).

Données : comptes nationaux distribués 2023 de l'Insee, base 2020, tableau CND.101 (vingtièmes
de niveau de vie usuel, regroupés en déciles ; ``data/processed/deciles/cnd_deciles.csv``,
``pipelines/deciles/extraire_cnd.py``). Clés (``CLES``) : ligne(s) de l'assiette ; variante
éventuelle (autre ligne) ; TVA et accises : variante tirée du Budget de famille 2017
(``fr_budget.menages.depense``).

Fourchette, décile par décile : extrêmes du produit des bornes de l'effet national par les parts
de chaque année 2020 à 2023 et de chaque variante de clé ; valeur centrale : effet central et
part de 2023 de la clé centrale. Plusieurs mesures : sommes des valeurs centrales, des bornes
basses et des bornes hautes. Termes croisés (``fr_budget.agrege.interactions``) : clé du levier de
CSG de la paire.

Euros par unité de consommation : effet en euros de 2025 divisé par le nombre d'unités de
consommation de 2023. Part du revenu disponible : revenu disponible net de 2023 porté en 2025
par le PIB nominal (``fr_budget.agrege.indexation.facteur_pib``).
"""

from __future__ import annotations

import csv
from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache

import numpy as np

from fr_budget import scenario as sc
from fr_budget.agrege import indexation, interactions
from fr_budget.fourchette import Fourchette
from fr_budget.menages import depense
from fr_budget.registres.verification import RACINE_DEPOT

FICHIER = RACINE_DEPOT / "data" / "processed" / "deciles" / "cnd_deciles.csv"
NOMBRE = 10
ANNEES = (2020, 2021, 2022, 2023)
ANNEE_CENTRALE = 2023
ANNEE_EFFETS = sc.ANNEE_REFERENCE
EUROS_PAR_MILLIARD = 1e9
UNITES_PAR_MILLION = 1e6
POURCENT = 100.0


@dataclass(frozen=True)
class Cle:
    """Lignes des comptes distribués dont la somme répartit l'effet, et variante éventuelle."""

    lignes: tuple[str, ...]
    variante: tuple[str, ...] | None = None
    budget_de_famille: bool = False
    """TVA et accises : variante tirée du Budget de famille 2017 (``fr_budget.menages.depense``)."""


_COTISATIONS = (
    "cotisations_retraite",
    "cotisations_chomage",
    "cotisations_famille",
    "cotisations_autres",
)
_IR = Cle(("impot_revenu",))
_CSG = ("csg",)

CLES: dict[str, Cle] = {
    sc.LEVIER_TVA_NORMAL: Cle(("taxes_produits",), budget_de_famille=True),
    sc.LEVIER_ACCISE_GAZOLE: Cle(("taxes_produits",), budget_de_famille=True),
    sc.LEVIER_ACCISE_ESSENCES: Cle(("taxes_produits",), budget_de_famille=True),
    "csg_activite": Cle(("salaires_nets", "revenus_mixtes"), _CSG),
    "csg_retraites": Cle(("pensions_retraite",), _CSG),
    "csg_capital": Cle(("revenus_propriete",), _CSG),
    sc.LEVIER_IR_SEUILS: _IR,
    sc.LEVIER_IR_QF: _IR,
    sc.LEVIER_IR_BAREME: _IR,
    sc.levier_depenses_fiscales_impot(sc.IMPOT_REVENU_DEPENSES_FISCALES): _IR,
    sc.LEVIER_IS_TAUX_NORMAL: Cle(("impot_societes",)),
    sc.LEVIER_IS_SURTAXE: Cle(("impot_societes",)),
    sc.LEVIER_COTISATIONS_TAUX: Cle(_COTISATIONS),
    sc.LEVIER_ALLEGEMENTS: Cle(_COTISATIONS),
    sc.LEVIER_CHOMAGE_CONTRIBUTION: Cle(("cotisations_chomage",)),
    sc.LEVIER_INDEXATION: Cle(("pensions_retraite", "invalidite", "famille", "exclusion_sociale")),
    sc.LEVIER_PA_PENTE: Cle(("exclusion_sociale",)),
    sc.LEVIER_CHOMAGE_REVALORISATION: Cle(("allocations_chomage",)),
    sc.LEVIER_CHOMAGE_DUREE: Cle(("allocations_chomage",)),
}
"""Clé de répartition de chaque levier (plan validé, tableau de la fiche § 3)."""

NON_REPARTIS = frozenset(set(sc.LEVIERS_REGISTRE) - set(CLES))
"""Leviers du simulateur sans clé : rémunérations publiques, dotations, crédits des missions,
dépenses fiscales hors impôt sur le revenu, âge de départ."""


@cache
def _lignes() -> dict[tuple[int, str], np.ndarray]:
    with FICHIER.open(encoding="utf-8") as f:
        return {
            (int(r["annee"]), r["ligne"]): np.array(
                [float(r[f"d{i}"]) for i in range(1, NOMBRE + 1)]
            )
            for r in csv.DictReader(f)
        }


def _parts(lignes: Sequence[str], annee: int) -> np.ndarray:
    total = sum((_lignes()[(annee, x)] for x in lignes), np.zeros(NOMBRE))
    return np.asarray(total / total.sum())


def parts_budget_de_famille(levier: str) -> np.ndarray:
    """Part de chaque décile dans l'effet d'une unité du levier, d'après le Budget de famille
    2017 (euros par ménage, chaque décile comptant le même nombre de ménages)."""
    effets = [e for e in depense.effets("decile", ANNEE_EFFETS) if e.classe != depense.ENSEMBLE]
    v = np.array([e.effets[levier].central for e in effets])
    return np.asarray(v / v.sum())


def _cle(levier: str) -> Cle:
    if interactions.est_interaction(levier):
        return CLES[sc.LEVIERS_CSG_PAR_INTERACTION[levier]]
    return CLES[levier]


def part_centrale(levier: str) -> np.ndarray:
    """Parts de la clé centrale, en 2023."""
    return _parts(_cle(levier).lignes, ANNEE_CENTRALE)


def variantes_parts(levier: str) -> list[np.ndarray]:
    """Parts de chaque variante : clé centrale et variante, années 2020 à 2023, et Budget de
    famille pour la TVA et les accises."""
    cle = _cle(levier)
    cles = [cle.lignes] + ([cle.variante] if cle.variante else [])
    resultat = [_parts(c, a) for c in cles for a in ANNEES]
    if cle.budget_de_famille:
        resultat.append(parts_budget_de_famille(levier))
    return resultat


def est_reparti(levier: str) -> bool:
    return levier in CLES or interactions.est_interaction(levier)


def unites_consommation() -> np.ndarray:
    """Nombre d'unités de consommation de chaque décile en 2023, en millions."""
    return _lignes()[(ANNEE_CENTRALE, "unites_consommation")]


def revenu_disponible() -> np.ndarray:
    """Revenu disponible net de chaque décile, en Md€ de 2025 (2023 porté par le PIB nominal)."""
    facteur = indexation.facteur_pib(ANNEE_EFFETS) / indexation.facteur_pib(ANNEE_CENTRALE)
    return _lignes()[(ANNEE_CENTRALE, "revenu_disponible")] * facteur


@dataclass(frozen=True)
class Repartition:
    milliards: list[Fourchette]
    """Variation du revenu de chaque décile, en Md€ de 2025 (négative : revenu en baisse)."""
    euros_par_uc: list[Fourchette]
    pourcent_revenu: list[Fourchette]
    non_repartis: list[str]


def repartition_mesure(levier: str, valeur: float) -> list[Fourchette]:
    """Variation du revenu de chaque décile due à une mesure, en Md€ de 2025."""
    unite = sc.rendement_unitaire(levier)
    effets = [-valeur * v for v in (unite.bas, unite.central, unite.haut)]
    centrale = part_centrale(levier)
    variantes = variantes_parts(levier)
    resultat = []
    for d in range(NOMBRE):
        candidats = [e * p[d] for e in effets for p in variantes]
        central = -valeur * unite.central * centrale[d]
        resultat.append(Fourchette(min(central, *candidats), central, max(central, *candidats)))
    return resultat


def repartition(mesures: Sequence[sc.Mesure]) -> Repartition:
    """Variation du revenu de chaque décile, mesures et termes croisés compris."""
    sc.verifier_double_compte(mesures)
    total = [[0.0, 0.0, 0.0] for _ in range(NOMBRE)]
    non_repartis: list[str] = []
    for m in sc.avec_interactions(mesures):
        if m.valeur == 0:
            continue
        if not est_reparti(m.levier):
            if m.levier not in non_repartis:
                non_repartis.append(m.levier)
            continue
        for d, f in enumerate(repartition_mesure(m.levier, m.valeur)):
            total[d][0] += f.bas
            total[d][1] += f.central
            total[d][2] += f.haut
    milliards = [Fourchette(*t) for t in total]
    uc = unites_consommation()
    rdn = revenu_disponible()

    def echelle(f: Fourchette, k: float) -> Fourchette:
        return Fourchette(f.bas * k, f.central * k, f.haut * k)

    return Repartition(
        milliards=milliards,
        euros_par_uc=[
            echelle(f, EUROS_PAR_MILLIARD / (uc[d] * UNITES_PAR_MILLION))
            for d, f in enumerate(milliards)
        ],
        pourcent_revenu=[echelle(f, POURCENT / rdn[d]) for d, f in enumerate(milliards)],
        non_repartis=non_repartis,
    )
