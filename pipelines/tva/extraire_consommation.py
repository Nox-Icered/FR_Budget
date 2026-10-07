"""Extrait la consommation par produit (niveau le plus fin) d'une année.

Source : INSEE, comptes nationaux annuels base 2020, « Consommation effective des ménages
par produit » (fichiers T_CONSO_EFF_PRODUITS_{MENAGES,APU,ISBLSM}.xlsx, feuille MEURcour,
millions d'euros courants, prix d'acquisition). Voir registres/datasets.yaml.

Les montants sont ceux de la dépense territoriale (achats sur le territoire, y compris par
les non-résidents), qui correspond au champ de la TVA française.

Le niveau le plus fin d'une ligne est déduit de la hiérarchie des codes
(17_ < 38_ < 88_ < 138G_ < H_ < HI_) : une ligne est retenue si la suivante n'est pas plus fine.
Chaque ligne retenue porte le code A38 (niveau 38_) dont elle dépend.

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/tva/extraire_consommation.py 2022
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
NIVEAUX = {"17": 0, "38": 1, "88": 2, "138G": 3, "H": 4, "HI": 5}
SECTEURS = {"menages": "MENAGES", "apu": "APU", "isblsm": "ISBLSM"}
LIGNE_ANNEES = 3
PREMIERE_LIGNE = 5


def niveau(code: str) -> int:
    return NIVEAUX[code.split("_")[0]]


def feuilles(fichier: Path, annee: int) -> list[tuple[str, str, str, float]]:
    lignes = CalamineWorkbook.from_path(fichier).get_sheet_by_name("MEURcour").to_python()
    en_tete = [str(int(v)) if isinstance(v, float) else str(v) for v in lignes[LIGNE_ANNEES]]
    colonne = en_tete.index(str(annee))
    donnees: list[tuple[str, str, float]] = []
    for r in lignes[PREMIERE_LIGNE:]:
        if not r[0]:
            continue
        if str(r[0]).split("_")[0] not in NIVEAUX:
            break  # lignes de total (P31…) après la nomenclature
        valeur = r[colonne]
        donnees.append((str(r[0]), str(r[1]).strip(), float(valeur) if valeur != "" else 0.0))
    retenues = []
    a38 = ""
    for i, (code, libelle, valeur) in enumerate(donnees):
        if code.startswith("38_"):
            a38 = code.removeprefix("38_")
        suivant = donnees[i + 1][0] if i + 1 < len(donnees) else None
        if suivant is None or niveau(suivant) <= niveau(code):
            retenues.append((code, libelle, a38, valeur))
    return retenues


def main(annee: int) -> None:
    for secteur, suffixe in SECTEURS.items():
        source = RACINE / "data" / "raw" / "tva" / "insee" / f"T_CONSO_EFF_PRODUITS_{suffixe}.xlsx"
        sortie = RACINE / "data" / "processed" / "tva" / f"consommation_{secteur}_{annee}.csv"
        with sortie.open("w", newline="", encoding="utf-8") as f:
            ecrivain = csv.writer(f)
            ecrivain.writerow(["code", "libelle", "a38", "millions_euros"])
            ecrivain.writerows(feuilles(source, annee))


if __name__ == "__main__":
    main(int(sys.argv[1]))
