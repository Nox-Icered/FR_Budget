"""Dépense supplémentaire des ménages à consommation inchangée : TVA et accises (spécification,
« Pouvoir d'achat » : le net après impôt n'inclut pas l'effet des prix ; pour les réformes de TVA
et d'accises, un indicateur séparé estime la variation de dépense à partir des budgets de famille
de l'Insee).

Méthode, pour chaque classe de ménages (décile de niveau de vie, type de ménage) :

- dépenses par poste : enquête Budget de famille 2017 de l'Insee (tableaux TF105 et TF106,
  ``data/processed/menages/bdf2017_depenses.csv``, ``pipelines/menages/extraire_bdf.py``),
  portées à l'année simulée comme la dépense de consommation des ménages des comptes nationaux
  (P31, euros courants ; au-delà de la dernière année des comptes, comme le PIB nominal,
  ``fr_budget.agrege.indexation.facteur_pib``) ;
- taux normal de TVA : part de chaque poste au taux normal, bornée (``registres/menages/
  bdf_postes_tva.csv``) ; un poste mixte va de 0 à 1, la valeur centrale est le milieu de la
  plage. Une hausse de x points du taux normal t (en fraction) relève les prix TTC des postes
  au taux normal de x / (1 + t) ;
- accises sur le gazole et les essences : litres achetés = dépense du poste « carburants »
  (07221) de 2017 divisée par le prix moyen TTC du litre en 2017 (SDES, données DGEC,
  ``data/processed/accises/prix_carburants_ttc.csv`` ; gazole et SP95-E10, produit de référence
  du levier sur les essences), pondéré par la part du gazole dans l'assiette du levier
  (``fr_budget.agrege.accises.assiette_levier``, faute de répartition par classe de ménages) ;
  les litres de l'année simulée suivent le volume de consommation de produits pétroliers des
  ménages (comptes nationaux, 17_C2, euros chaînés de 2020). Une hausse d'un centime par litre
  coûte un centime plus la TVA au taux normal.

Hypothèses de méthode (fiche ``docs/fiches/depense_menages.md``) : répercussion complète sur les
prix, aucun changement de comportement, structure de consommation de 2017 par classe.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache

from fr_budget.agrege import accises, indexation, tva
from fr_budget.fourchette import Fourchette
from fr_budget.registres.verification import RACINE_DEPOT

DONNEES = RACINE_DEPOT / "data" / "processed"
REGISTRE_POSTES = RACINE_DEPOT / "registres" / "menages" / "bdf_postes_tva.csv"
ANNEE_ENQUETE = 2017
NOMENCLATURES = ("decile", "type_menage")
ENSEMBLE = "TOT"
POSTE_CARBURANTS = "07221"
PRIX_GAZOLE = "gazole"
PRIX_ESSENCES = "sp95_e10"
"""Prix de référence des essences : SP95-E10, produit de référence du levier (simulateur)."""
CENTIME = 0.01
POINT = 0.01

TVA_NORMAL = "tva_taux_normal"
ACCISE_GAZOLE = "accise_gazole"
ACCISE_ESSENCES = "accise_essences"
LEVIERS = (TVA_NORMAL, ACCISE_GAZOLE, ACCISE_ESSENCES)


@dataclass(frozen=True)
class PartPoste:
    basse: float
    haute: float
    carburant: bool

    @property
    def centrale(self) -> float:
        return (self.basse + self.haute) / 2


@dataclass(frozen=True)
class EffetClasse:
    """Effet d'une unité de chaque levier sur une classe de ménages, en euros par ménage et par
    an, et dépense de consommation de la classe (même année)."""

    classe: str
    consommation: float
    effets: dict[str, Fourchette]


@cache
def parts_postes() -> dict[str, PartPoste]:
    with REGISTRE_POSTES.open(encoding="utf-8") as f:
        return {
            r["poste"]: PartPoste(
                float(r["part_normal_basse"]), float(r["part_normal_haute"]), r["carburant"] == "1"
            )
            for r in csv.DictReader(f)
        }


@cache
def depenses(nomenclature: str) -> dict[str, dict[str, float]]:
    """Dépenses de 2017 par classe puis par poste, en euros par ménage."""
    resultat: dict[str, dict[str, float]] = {}
    with (DONNEES / "menages" / "bdf2017_depenses.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["nomenclature"] == nomenclature:
                resultat.setdefault(r["classe"], {})[r["poste"]] = float(r["euros"])
    return resultat


@cache
def _consommation_nationale() -> dict[int, tuple[float, float]]:
    with (DONNEES / "menages" / "consommation_nationale.csv").open(encoding="utf-8") as f:
        return {
            int(r["annee"]): (
                float(r["p31_millions_courants"]),
                float(r["carburants_volume_millions_2020"]),
            )
            for r in csv.DictReader(f)
        }


@cache
def prix_carburants() -> dict[tuple[int, str], float]:
    with (DONNEES / "accises" / "prix_carburants_ttc.csv").open(encoding="utf-8") as f:
        return {
            (int(r["annee"]), r["produit"]): float(r["euros_par_litre"]) for r in csv.DictReader(f)
        }


def derniere_annee_comptes() -> int:
    return max(_consommation_nationale())


def facteur_consommation(annee: int) -> float:
    """Dépense de consommation des ménages (P31, euros courants) de ``annee`` rapportée à celle
    de 2017 ; au-delà de la dernière année des comptes, croissance du PIB nominal."""
    comptes = _consommation_nationale()
    derniere = derniere_annee_comptes()
    base = comptes[min(annee, derniere)][0] / comptes[ANNEE_ENQUETE][0]
    if annee <= derniere:
        return base
    return base * indexation.facteur_pib(annee) / indexation.facteur_pib(derniere)


def facteur_volume_carburants(annee: int) -> float:
    """Volume de produits pétroliers consommé par les ménages en ``annee`` rapporté à 2017 ;
    au-delà de la dernière année des comptes, volume de la dernière année."""
    comptes = _consommation_nationale()
    return comptes[min(annee, derniere_annee_comptes())][1] / comptes[ANNEE_ENQUETE][1]


def part_gazole(annee: int) -> float:
    """Part du gazole dans l'assiette du levier (hectolitres de gazole et d'essences)."""
    assiette = accises.assiette_levier(annee)
    return assiette["gazole"] / (assiette["gazole"] + assiette["essences"])


def litres_carburants(depense_carburants: float, annee: int) -> float:
    """Litres achetés en ``annee`` par un ménage qui dépensait ``depense_carburants`` en 2017."""
    gazole = part_gazole(annee)
    prix = prix_carburants()
    prix_moyen = (
        gazole * prix[(ANNEE_ENQUETE, PRIX_GAZOLE)]
        + (1 - gazole) * prix[(ANNEE_ENQUETE, PRIX_ESSENCES)]
    )
    return depense_carburants / prix_moyen * facteur_volume_carburants(annee)


def _unique(valeur: float) -> Fourchette:
    return Fourchette(bas=valeur, central=valeur, haut=valeur)


def depense_taux_normal(postes: dict[str, float]) -> Fourchette:
    """Dépense au taux normal de TVA (euros de 2017), bornée par les postes mixtes."""
    parts = parts_postes()
    return Fourchette(
        bas=sum(m * parts[p].basse for p, m in postes.items()),
        central=sum(m * parts[p].centrale for p, m in postes.items()),
        haut=sum(m * parts[p].haute for p, m in postes.items()),
    )


def effet_classe(postes: dict[str, float], annee: int, classe: str = "") -> EffetClasse:
    """Effet d'un point de taux normal de TVA et d'un centime par litre d'accise, en euros par
    ménage et par an de ``annee``."""
    taux = tva.taux_tva(annee)["normal"]
    facteur = facteur_consommation(annee)
    normal = depense_taux_normal(postes)
    tva_point = Fourchette(
        bas=normal.bas * facteur * POINT / (1 + taux),
        central=normal.central * facteur * POINT / (1 + taux),
        haut=normal.haut * facteur * POINT / (1 + taux),
    )
    carburants = sum(m for p, m in postes.items() if parts_postes()[p].carburant)
    litres = litres_carburants(carburants, annee)
    gazole = part_gazole(annee)
    centime = CENTIME * (1 + taux)
    return EffetClasse(
        classe=classe,
        consommation=sum(postes.values()) * facteur,
        effets={
            TVA_NORMAL: tva_point,
            ACCISE_GAZOLE: _unique(litres * gazole * centime),
            ACCISE_ESSENCES: _unique(litres * (1 - gazole) * centime),
        },
    )


@cache
def effets(nomenclature: str, annee: int) -> tuple[EffetClasse, ...]:
    """Effet d'une unité de chaque levier sur chaque classe de la nomenclature (ensemble
    compris)."""
    classes = sorted(depenses(nomenclature).items(), key=lambda c: _ordre(c[0]))
    return tuple(effet_classe(postes, annee, classe) for classe, postes in classes)


def _ordre(classe: str) -> tuple[int, int]:
    """Classes numérotées dans l'ordre (déciles, types de ménage), l'ensemble à la fin."""
    return (1, 0) if classe == ENSEMBLE else (0, int(classe))


def part_taux_normal(nomenclature: str = "type_menage", classe: str = ENSEMBLE) -> Fourchette:
    """Part de la consommation de 2017 d'une classe au taux normal de TVA."""
    postes = depenses(nomenclature)[classe]
    total = sum(postes.values())
    normal = depense_taux_normal(postes)
    return Fourchette(
        bas=normal.bas / total, central=normal.central / total, haut=normal.haut / total
    )


LOYERS_IMPUTES = ("HI_L68I0A_B2020", "HI_L68I0B_B2020")
"""Loyers imputés aux propriétaires (comptes nationaux) : l'enquête ne les compte pas."""
ANNEES_CONTROLE = (2015, 2022)
"""Années des comptes nationaux disponibles au niveau le plus fin qui encadrent l'enquête."""


def part_taux_normal_comptes_nationaux(annee: int) -> float:
    """Part de la consommation des ménages des comptes nationaux au taux normal de TVA, hors
    loyers imputés : produits rattachés à un régime par le levier TVA (correspondance et
    répartition des produits mixtes)."""
    repartitions = tva.repartitions_produits_mixtes()
    regimes = tva.regimes_produits()
    lignes = [c for c in tva.consommation_fine("menages", annee) if c[0] not in LOYERS_IMPUTES]
    total = sum(m for _, _, m in lignes)
    normal = sum(
        m
        * (
            repartitions[code].parts.get("normal", 0.0)
            if code in repartitions
            else float(regimes[code] == "normal")
        )
        for code, _, m in lignes
    )
    return normal / total
