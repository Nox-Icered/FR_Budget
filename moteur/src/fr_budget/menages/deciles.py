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

Impôt sur le revenu (option C, 6 novembre 2026) : une clé au prorata de l'impôt payé ne vaut pas
pour une mesure ciblée sur une tranche (écart de 50,7 points à l'Insee sur la baisse de 2020).
Le moteur du barème (``fr_budget.agrege.bareme_ir``) calcule l'écart d'impôt par dixième de
foyers classés selon le revenu fiscal de référence par part (DGFiP) ; le k-ième dixième fiscal
est assimilé au k-ième dixième de niveau de vie (hypothèse de correspondance, écart de 6,0
points à l'Insee sur la même réforme). Revalorisation des seuils : parts d'une revalorisation de
1 % du barème de 2025 ; barème saisi sur le site : écart par dixième de ce barème. Plafond du
quotient familial et dépenses fiscales de l'impôt sur le revenu : non répartis (le moteur du
barème ne traite pas le plafonnement, et aucune source ne répartit les dépenses fiscales).

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
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import cache

import numpy as np

from fr_budget import scenario as sc
from fr_budget.agrege import bareme_ir, indexation, interactions
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
_CSG = ("csg",)

CLES: dict[str, Cle] = {
    sc.LEVIER_TVA_NORMAL: Cle(("taxes_produits",), budget_de_famille=True),
    sc.LEVIER_ACCISE_GAZOLE: Cle(("taxes_produits",), budget_de_famille=True),
    sc.LEVIER_ACCISE_ESSENCES: Cle(("taxes_produits",), budget_de_famille=True),
    "csg_activite": Cle(("salaires_nets", "revenus_mixtes"), _CSG),
    "csg_retraites": Cle(("pensions_retraite",), _CSG),
    "csg_capital": Cle(("revenus_propriete",), _CSG),
    # Parts tirées du moteur du barème (``parts_seuils``), pas des comptes distribués.
    sc.LEVIER_IR_SEUILS: Cle(()),
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

BAREME = sc.LEVIER_IR_BAREME
"""Barème saisi sur le site : réparti par le moteur du barème quand le barème est donné."""

NON_REPARTIS = frozenset(set(sc.LEVIERS_REGISTRE) - set(CLES) - {BAREME})
"""Leviers du simulateur sans clé : rémunérations publiques, dotations, crédits des missions,
dépenses fiscales, plafond du quotient familial, âge de départ."""


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


REVALORISATION_TEST = 0.01
"""Revalorisation des seuils (et de la décote) dont on tire les parts du levier sur les seuils."""


@cache
def parts_seuils() -> list[np.ndarray]:
    """Parts de chaque dixième dans l'effet d'une revalorisation de 1 % du barème de 2025
    (seuils et décote), pour chaque variante du moteur du barème (centrale en premier)."""
    reference = bareme_ir.bareme_openfisca(bareme_ir.ANNEE_SITE)
    revalorise = bareme_ir._indexe(reference, 1 + REVALORISATION_TEST)
    return [np.asarray(np.array(v) / sum(v)) for v in bareme_ir.ecart_par_dixieme_site(revalorise)]


def _cle(levier: str) -> Cle:
    if interactions.est_interaction(levier):
        return CLES[sc.LEVIERS_CSG_PAR_INTERACTION[levier]]
    return CLES[levier]


def part_centrale(levier: str) -> np.ndarray:
    """Parts de la clé centrale, en 2023 (seuils de l'impôt sur le revenu : moteur du barème)."""
    if levier == sc.LEVIER_IR_SEUILS:
        return parts_seuils()[0]
    return _parts(_cle(levier).lignes, ANNEE_CENTRALE)


def variantes_parts(levier: str) -> list[np.ndarray]:
    """Parts de chaque variante : clé centrale et variante, années 2020 à 2023, et Budget de
    famille pour la TVA et les accises."""
    if levier == sc.LEVIER_IR_SEUILS:
        return parts_seuils()
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


def repartition_bareme(reforme: bareme_ir.Bareme) -> list[Fourchette]:
    """Variation du revenu de chaque décile due à un barème saisi, en Md€ de 2025 : moins l'écart
    d'impôt par dixième (moteur du barème), bornes : variantes du moteur du barème, multipliées
    par la plage de l'écart à la validation (rendement du levier générique)."""
    unite = sc.rendement_unitaire(BAREME)
    facteurs = (unite.bas, unite.central, unite.haut)
    variantes = bareme_ir.ecart_par_dixieme_site(reforme)
    resultat = []
    for d in range(NOMBRE):
        central = -variantes[0][d] * unite.central
        candidats = [-v[d] * k for v in variantes for k in facteurs]
        resultat.append(Fourchette(min(central, *candidats), central, max(central, *candidats)))
    return resultat


def repartition(
    mesures: Sequence[sc.Mesure], bareme: bareme_ir.Bareme | None = None
) -> Repartition:
    """Variation du revenu de chaque décile, mesures et termes croisés compris. ``bareme`` :
    barème saisi sur le site, dont la mesure ``ir_bareme`` porte l'effet national."""
    sc.verifier_double_compte(mesures)
    total = [[0.0, 0.0, 0.0] for _ in range(NOMBRE)]
    non_repartis: list[str] = []
    for m in sc.avec_interactions(mesures):
        if m.valeur == 0:
            continue
        if m.levier == BAREME and bareme is not None:
            for d, f in enumerate(repartition_bareme(bareme)):
                total[d][0] += f.bas
                total[d][1] += f.central
                total[d][2] += f.haut
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


# Validation : forme de la répartition face aux évaluations de réformes par l'Insee (modèle Ines,
# France, portrait social ; ``data/processed/deciles/validation_insee.csv``,
# ``pipelines/deciles/extraire_cnd.py``). Part de chaque dixième dans l'effet total ; tolérance :
# au plus 10 points de part sur chaque dixième (choix du lot, à relire).
FICHIER_VALIDATION = RACINE_DEPOT / "data" / "processed" / "deciles" / "validation_insee.csv"
TOLERANCE_VALIDATION_POINTS = 10.0


def _baisse_impot_revenu_2020() -> np.ndarray:
    """Baisse de l'impôt sur le revenu de 2020 (même réforme que
    ``bareme_ir.validation_classes_moyennes_2020``) : parts par dixième fiscal."""
    apres, avant = bareme_ir.bareme_openfisca(2020), bareme_ir.bareme_openfisca(2019)
    revalorise = bareme_ir._indexe(avant, apres.seuils[-1] / avant.seuils[-1])
    v = np.array(bareme_ir.ecart_par_dixieme(revalorise, apres, 2020)[0])
    return np.asarray(v / v.sum())


def _prime_activite() -> np.ndarray:
    return part_centrale(sc.LEVIER_PA_PENTE)


VALIDATIONS: dict[str, tuple[str, str, Callable[[], np.ndarray]]] = {
    # référence : (source, levier, parts du modèle)
    "fps2019_prime_activite_2018": (
        "insee_fps2019_reformes_2018",
        sc.LEVIER_PA_PENTE,
        _prime_activite,
    ),
    "fps2022_baisse_impot_revenu_2020": (
        "insee_fps2022_reformes_2020_2021",
        sc.LEVIER_IR_BAREME,
        _baisse_impot_revenu_2020,
    ),
}


@dataclass(frozen=True)
class ComparaisonForme:
    reference: str
    source: str
    levier: str
    modele: list[float]
    """Part de chaque dixième dans l'effet total, en %."""
    insee: list[float]
    ecart_max_points: float
    tolerance_points: float

    @property
    def dans_la_tolerance(self) -> bool:
        return self.ecart_max_points <= self.tolerance_points


def _parts_insee(reference: str) -> np.ndarray:
    with FICHIER_VALIDATION.open(encoding="utf-8") as f:
        ligne = next(r for r in csv.DictReader(f) if r["reference"] == reference)
    v = np.array([float(ligne[f"d{i}"]) for i in range(1, NOMBRE + 1)])
    return np.asarray(v / v.sum())


def validation_insee() -> list[ComparaisonForme]:
    """Comparaison de la forme de la répartition aux évaluations de l'Insee."""
    resultat = []
    for reference, (source, levier, parts) in VALIDATIONS.items():
        m, r = parts(), _parts_insee(reference)
        resultat.append(
            ComparaisonForme(
                reference=reference,
                source=source,
                levier=levier,
                modele=[float(POURCENT * x) for x in m],
                insee=[float(POURCENT * x) for x in r],
                ecart_max_points=float(POURCENT * np.max(np.abs(m - r))),
                tolerance_points=TOLERANCE_VALIDATION_POINTS,
            )
        )
    return resultat
