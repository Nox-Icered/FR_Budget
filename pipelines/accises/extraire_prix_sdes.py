"""Extrait les prix moyens annuels TTC des carburants (lot « dépense des ménages »).

Sources (registres/datasets.yaml) : SDES, données DGEC, tableau 3 « prix à la consommation des
carburants » de deux éditions, dans data/raw/accises/sdes/ :

- édition 2019 (``prix_produits_petroliers_2019.xls``) : années 2009 à 2018, France
  métropolitaine ;
- édition 2025 (``prix_produits_petroliers_2025.xlsx``) : années 2019 à 2025, France
  continentale.

Transformation : ligne « TTC » de chaque carburant, en euros par litre ; pour une année
présente dans les deux éditions, l'édition la plus récente l'emporte.

Sortie : data/processed/accises/prix_carburants_ttc.csv (annee, produit, euros_par_litre).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/accises/extraire_prix_sdes.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
BRUT = RACINE / "data" / "raw" / "accises" / "sdes"
EDITIONS = ("prix_produits_petroliers_2019.xls", "prix_produits_petroliers_2025.xlsx")
SORTIE = RACINE / "data" / "processed" / "accises" / "prix_carburants_ttc.csv"
FEUILLE = "Tableau 3"
PRODUITS = {"Gazole": "gazole", "SP98": "sp98", "SP95-E10": "sp95_e10", "SP95": "sp95"}
TTC = "TTC"


def prix(fichier: str) -> dict[tuple[int, str], float]:
    lignes = CalamineWorkbook.from_path(str(BRUT / fichier)).get_sheet_by_name(FEUILLE).to_python()
    entete = next(r for r in lignes if any(str(c).startswith("20") for c in r[2:]))
    annees = {i: int(float(c)) for i, c in enumerate(entete) if str(c).startswith("20")}
    resultat: dict[tuple[int, str], float] = {}
    produit = None
    for ligne in lignes:
        libelle = str(ligne[0]).split(" (")[0].strip()
        if libelle:
            produit = PRODUITS.get(libelle)
        if produit is not None and str(ligne[1]).strip() == TTC:
            for i, annee in annees.items():
                if isinstance(ligne[i], float):
                    resultat[(annee, produit)] = ligne[i]
    return resultat


def main() -> None:
    tous: dict[tuple[int, str], float] = {}
    for fichier in EDITIONS:
        tous.update(prix(fichier))
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(["annee", "produit", "euros_par_litre"])
        for (annee, produit), valeur in sorted(tous.items()):
            ecrivain.writerow([annee, produit, f"{valeur:.6f}"])


if __name__ == "__main__":
    main()
