"""Met en table les données du modèle de retraites par cohortes (module retraites, deuxième
étape).

Sources (registres/datasets.yaml) :

- Insee, projections de population 2021-2070, scénario central, feuille « population »
  (population au 1er janvier par âge révolu, France) ;
- DREES, Les retraités et les retraites, édition 2025, fiche 15, graphique 3 : taux de
  retraités par âge au 31 décembre, de 50 à 70 ans ;
- même édition, fiche 14, tableaux 1 et 3 : âge légal d'ouverture des droits et âge
  d'annulation de la décote par génération (salariés du secteur privé et indépendants).

Transformation : population des âges 20 à 104, années 2023 à 2070 ; taux de retraités
de 2023 (dernière année publiée), en fraction.

Sorties :

- data/processed/retraites/cohortes_population.csv (annee, age, effectif) ;
- data/processed/retraites/cohortes_taux_retraites.csv (age, taux) ;
- data/processed/retraites/cohortes_ages_legaux.csv (generation, age_ouverture,
  age_annulation_decote), en années décimales, générations 1955 à la dernière ligne publiée
  (« et suivantes » : prolongée jusqu'à la génération 2010).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/retraites/extraire_cohortes.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
BRUT = RACINE / "data" / "raw" / "retraites"
SORTIES = RACINE / "data" / "processed" / "retraites"
POPULATION = BRUT / "insee" / "projections_population_2021_central.xlsx"
TAUX = BRUT / "drees" / "fiche15_age_depart.xlsx"
REGLES = BRUT / "drees" / "fiche14_regles_liquidation.xlsx"
GENERATION_MIN = 1955
GENERATION_MAX = 2010
MOIS_PAR_AN = 12
AGE_MIN = 20
ANNEES = range(2023, 2071)
ANNEE_TAUX = 2023
POURCENT = 100.0


def _age(cellule: object) -> int | None:
    texte = str(cellule).strip()
    chiffres = texte.split(".")[0].split(" ")[0]
    return int(chiffres) if chiffres.isdigit() else None


def population() -> list[dict[str, object]]:
    lignes = CalamineWorkbook.from_path(str(POPULATION)).get_sheet_by_name("population").to_python()
    entete = next(r for r in lignes if str(r[0]).startswith("Âge"))
    colonnes = {
        int(str(c).split(" ")[0].split(".")[0]): i
        for i, c in enumerate(entete)
        if i and str(c).split(" ")[0].split(".")[0].isdigit()
    }
    resultat = []
    for ligne in lignes:
        age = _age(ligne[0])
        if age is None or age < AGE_MIN:
            continue
        resultat.extend(
            {"annee": a, "age": age, "effectif": float(ligne[colonnes[a]])} for a in ANNEES
        )
    return resultat


def taux_retraites() -> list[dict[str, object]]:
    lignes = CalamineWorkbook.from_path(str(TAUX)).get_sheet_by_name("F15_Graphique 3").to_python()
    entete = next(r for r in lignes if str(r[0]).strip() == "Âge")
    colonne = [i for i, c in enumerate(entete) if str(c).startswith(str(ANNEE_TAUX))][0]
    return [
        {"age": int(float(r[0])), "taux": float(r[colonne]) / POURCENT}
        for r in lignes
        if isinstance(r[0], float)
    ]


def _annees(texte: object) -> float:
    """« 63 ans et 3 mois » → 63,25."""
    mots = str(texte).replace("\xa0", " ").split()
    ans = int(mots[0])
    mois = int(mots[3]) if len(mots) > 3 and mots[4].startswith("mois") else 0
    return ans + mois / MOIS_PAR_AN


def _par_generation(feuille: str) -> dict[int, float]:
    """Âge par génération, colonne des salariés du secteur privé ; une ligne « Du … au … »
    vaut pour l'année de sa date de début ; « et suivantes » prolonge la dernière ligne."""
    lignes = CalamineWorkbook.from_path(str(REGLES)).get_sheet_by_name(feuille).to_python()
    ages: dict[int, float] = {}
    dernier = None
    for ligne in lignes:
        cle = str(ligne[0]).strip()
        if not str(ligne[1]).strip()[:2].isdigit():
            continue
        if cle.startswith("Du "):
            generation = int(cle.split()[1][-4:])
        elif cle[:4].isdigit():
            generation = int(cle[:4])
        else:
            continue
        ages.setdefault(generation, _annees(ligne[1]))
        dernier = generation
        if "suivantes" in cle:
            for g in range(generation, GENERATION_MAX + 1):
                ages.setdefault(g, ages[generation])
    assert dernier is not None
    for g in range(dernier + 1, GENERATION_MAX + 1):
        ages.setdefault(g, ages[dernier])
    return ages


def ages_legaux() -> list[dict[str, object]]:
    ouverture = _par_generation("F14_Tableau 1")
    decote = _par_generation("F14_Tableau 3")
    return [
        {"generation": g, "age_ouverture": ouverture[g], "age_annulation_decote": decote[g]}
        for g in range(GENERATION_MIN, GENERATION_MAX + 1)
    ]


def ecrire(chemin: Path, lignes: list[dict[str, object]]) -> None:
    with chemin.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def main() -> None:
    ecrire(SORTIES / "cohortes_population.csv", population())
    ecrire(SORTIES / "cohortes_taux_retraites.csv", taux_retraites())
    ecrire(SORTIES / "cohortes_ages_legaux.csv", ages_legaux())


if __name__ == "__main__":
    main()
