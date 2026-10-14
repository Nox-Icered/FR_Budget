"""Effet des leviers sur la charge des entreprises, par taille et par secteur.

Méthode (choix à relire, ``docs/fiches/entreprises.md``) : l'effet national d'une mesure (le
rendement unitaire du levier, en fourchette, ``fr_budget.scenario.rendement_unitaire``) est
réparti entre les classes d'entreprises selon leur part de l'assiette du levier, sans
changement de comportement. Les totaux par classe redonnent donc l'effet national du
simulateur.

Clés de répartition :

- taux de cotisation patronale : masse salariale du secteur privé (Urssaf, 2024), par tranche
  de taille d'entreprise et par grand secteur ;
- allègements généraux : réduction générale et réductions des taux maladie et famille (Urssaf,
  2024), mêmes classes ;
- taux normal de l'impôt sur les sociétés : impôt brut (DGFiP, 2025, valeur centrale) ; la
  fourchette de la part prend aussi le résultat fiscal et l'année 2024, par catégorie
  d'entreprise (très petites, PME, intermédiaires, grandes) et par secteur de la DGFiP ;
- surtaxe des grandes entreprises (chiffre d'affaires de plus d'un milliard d'euros) : toute la
  charge aux grandes entreprises ; pas de répartition par secteur (aucune donnée publiée).

Chaque levier garde la nomenclature de ses données : tranches d'effectif et grands secteurs de
l'Urssaf pour les cotisations, catégories et secteurs de la DGFiP pour l'impôt.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache

from fr_budget import scenario
from fr_budget.fourchette import Fourchette
from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "entreprises"
EUROS_PAR_MILLIARD = 1e9
POURCENT = 100.0
ANNEE_IS = 2025
ANNEE_IS_ALTERNATIVE = 2024
TAILLE = "taille"
SECTEUR = "secteur"
LIBELLES_CATEGORIES = {
    "tpe": "Très petites entreprises",
    "pme": "Petites et moyennes entreprises",
    "eti": "Entreprises de taille intermédiaire",
    "ge": "Grandes entreprises",
}
GRANDES = "ge"


def _lire(nom: str) -> list[dict[str, str]]:
    with (DOSSIER / nom).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@dataclass(frozen=True)
class Classe:
    id: str
    libelle: str
    part: Fourchette
    """Part de la classe dans l'assiette du levier (basse, centrale, haute)."""
    effectifs: float | None = None
    """Salariés (moyenne annuelle, Urssaf), pour l'effet par salarié."""
    entreprises: float | None = None
    """Entreprises redevables (DGFiP), pour l'effet par entreprise."""


def _parts(valeurs: dict[str, float]) -> dict[str, float]:
    total = sum(valeurs.values())
    return {k: v / total for k, v in valeurs.items()}


def _classes_urssaf(nomenclature: str, colonne: str) -> list[Classe]:
    fichier, cle, libelle = (
        ("taille.csv", "tranche", "tranche")
        if nomenclature == TAILLE
        else ("secteur.csv", "code", "secteur")
    )
    lignes = _lire(fichier)
    parts = _parts({ligne[cle]: float(ligne[colonne]) for ligne in lignes})
    return [
        Classe(
            id=ligne[cle],
            libelle=ligne[libelle].split(") ", 1)[-1] if nomenclature == TAILLE else ligne[libelle],
            part=Fourchette(parts[ligne[cle]], parts[ligne[cle]], parts[ligne[cle]]),
            effectifs=float(ligne["effectifs"]),
        )
        for ligne in lignes
    ]


def _classes_is(nomenclature: str) -> list[Classe]:
    fichier, cle = (
        ("is_taille.csv", "categorie") if nomenclature == TAILLE else ("is_secteur.csv", "secteur")
    )
    lignes = _lire(fichier)
    cles = [
        _parts(
            {ligne[cle]: float(ligne[colonne]) for ligne in lignes if int(ligne["annee"]) == annee}
        )
        for annee in (ANNEE_IS, ANNEE_IS_ALTERNATIVE)
        for colonne in ("is_brut_md", "resultat_fiscal_md")
    ]
    centrale = cles[0]
    classes = []
    for ligne in lignes:
        if int(ligne["annee"]) != ANNEE_IS:
            continue
        identifiant = ligne[cle]
        valeurs = [c[identifiant] for c in cles if identifiant in c]
        classes.append(
            Classe(
                id=identifiant,
                libelle=LIBELLES_CATEGORIES.get(identifiant, identifiant),
                part=Fourchette(min(valeurs), centrale[identifiant], max(valeurs)),
                entreprises=float(ligne["entreprises"]),
            )
        )
    return classes


def _classes_surtaxe() -> list[Classe]:
    return [
        Classe(
            id=c.id,
            libelle=c.libelle,
            part=Fourchette(*(3 * (1.0 if c.id == GRANDES else 0.0,))),
            entreprises=c.entreprises,
        )
        for c in _classes_is(TAILLE)
    ]


LEVIERS_ENTREPRISES = (
    scenario.LEVIER_COTISATIONS_TAUX,
    scenario.LEVIER_ALLEGEMENTS,
    scenario.LEVIER_IS_TAUX_NORMAL,
    scenario.LEVIER_IS_SURTAXE,
)


@cache
def classes(levier: str, nomenclature: str) -> tuple[Classe, ...]:
    """Classes d'entreprises et leur part de l'assiette du levier ; vide si le levier n'est pas
    réparti dans cette nomenclature (surtaxe par secteur)."""
    if levier == scenario.LEVIER_COTISATIONS_TAUX:
        return tuple(_classes_urssaf(nomenclature, "masse_salariale"))
    if levier == scenario.LEVIER_ALLEGEMENTS:
        return tuple(_classes_urssaf(nomenclature, "allegements"))
    if levier == scenario.LEVIER_IS_TAUX_NORMAL:
        return tuple(_classes_is(nomenclature))
    if levier == scenario.LEVIER_IS_SURTAXE:
        return tuple(_classes_surtaxe()) if nomenclature == TAILLE else ()
    msg = f"{levier} : pas de répartition par entreprise"
    raise ValueError(msg)


def produit(a: Fourchette, b: Fourchette) -> Fourchette:
    """Produit de deux fourchettes : extrêmes des quatre produits, centre des centres."""
    produits = [x * y for x in (a.bas, a.haut) for y in (b.bas, b.haut)]
    return Fourchette(min(produits), a.central * b.central, max(produits))


def effet_unitaire(levier: str, nomenclature: str) -> list[tuple[Classe, Fourchette]]:
    """Variation de la charge de chaque classe pour une unité du levier, en Md€ par an (le
    signe suit les recettes publiques : positif, la charge augmente)."""
    national = scenario.rendement_unitaire(levier)
    return [(c, produit(national, c.part)) for c in classes(levier, nomenclature)]


# Contrôles indépendants (tests de validation).


def point_masse_salariale(annee: int) -> float:
    """1 % de la masse salariale du secteur privé de l'Urssaf, en Md€."""
    for ligne in _lire("masse_salariale_annuelle.csv"):
        if int(ligne["annee"]) == annee:
            return float(ligne["masse_salariale"]) / POURCENT / EUROS_PAR_MILLIARD
    msg = f"{annee} : masse salariale absente"
    raise ValueError(msg)


def allegements_urssaf() -> float:
    """Allègements généraux (catégories 11, 15 et 16) de l'Urssaf, en Md€ (année des données)."""
    return sum(float(ligne["allegements"]) for ligne in _lire("taille.csv")) / EUROS_PAR_MILLIARD


def annee_urssaf() -> int:
    return int(_lire("taille.csv")[0]["annee"])
