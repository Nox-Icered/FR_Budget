"""Extrait le bénéfice imposable à l'IS par taux d'imposition (lot 2.3).

Source : DGFiP Statistiques n° 51, « L'impôt sur le bénéfice 2025 des entreprises »,
fichier de tableaux, onglet « Graphique 2 » (voir registres/datasets.yaml,
``dgfip_stat_51_is_2025_xlsx``). Montants en Md€, repris sans arrondi ni calcul.

Lignes reprises : bénéfice imposable à 15 %, à 25 %, assiette de la contribution
exceptionnelle sur les bénéfices des grandes entreprises (CEBGE), déficits ; années 2022 à 2025.

Sortie : data/processed/impot_societes/benefice_imposable.csv (annee, indicateur, md_euros).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/impot_societes/extraire_dgfip.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
SOURCE = RACINE / "data" / "raw" / "impot_societes" / "dgfip" / "dgfip_stat_51_is-2025.xlsx"
SORTIE = RACINE / "data" / "processed" / "impot_societes" / "benefice_imposable.csv"
LIGNES = {
    "B.I. à 15%": "benefice_imposable_15",
    "B.I. à 25%": "benefice_imposable_25",
    "Assiette CEGBE": "assiette_cebge",
    "Déficit": "deficit",
}


def main() -> None:
    lignes = CalamineWorkbook.from_path(str(SOURCE)).get_sheet_by_name("Graphique 2").to_python()
    en_tete = next(r for r in lignes if any(c == 2025.0 for c in r))  # noqa: PLR2004
    annees = [(j, int(c)) for j, c in enumerate(en_tete) if isinstance(c, float)]
    sortie = []
    for ligne in lignes:
        libelle = str(ligne[0]).strip()
        if libelle in LIGNES:
            sortie.extend(
                (annee, LIGNES[libelle], float(ligne[j]))
                for j, annee in annees
                if isinstance(ligne[j], float)
            )
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(["annee", "indicateur", "md_euros"])
        ecrivain.writerows(sorted(sortie))


if __name__ == "__main__":
    main()
