"""Extrait les ventes annuelles de produits pétroliers en France métropolitaine (lot 2.2).

Source : SDES, « Données mensuelles de consommation de produits pétroliers (à partir de
2017) », dans data/raw/accises/sdes/ (voir registres/datasets.yaml,
``sdes_conso_produits_petroliers_csv``). Unités : tonnes (liste des variables du SDES).

Transformation : somme des douze mois de chaque année ; seules les années complètes sont
gardées. ``SUPER_SANS_PLOMB`` (total des supercarburants) n'est pas repris : c'est la somme
des quatre supercarburants détaillés.

Sortie : data/processed/accises/ventes_produits_petroliers.csv (annee, produit, tonnes).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/accises/extraire_ventes_sdes.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).parents[2]
SOURCE = (
    RACINE / "data" / "raw" / "accises" / "sdes" / "consommation_produits_petroliers_mensuelle.csv"
)
SORTIE = RACINE / "data" / "processed" / "accises" / "ventes_produits_petroliers.csv"
MOIS_PAR_AN = 12
EXCLUS = {"MOIS", "ANNEE", "SUPER_SANS_PLOMB"}


def main() -> None:
    with SOURCE.open(encoding="utf-8") as f:
        lignes = list(csv.DictReader(f, delimiter=";"))
    totaux: dict[tuple[int, str], float] = defaultdict(float)
    mois: dict[int, int] = defaultdict(int)
    for ligne in lignes:
        annee = int(ligne["ANNEE"])
        mois[annee] += 1
        for produit, valeur in ligne.items():
            if produit not in EXCLUS:
                totaux[(annee, produit.lower())] += float(valeur)
    sortie = [(a, p, round(v, 3)) for (a, p), v in sorted(totaux.items()) if mois[a] == MOIS_PAR_AN]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(["annee", "produit", "tonnes"])
        ecrivain.writerows(sortie)


if __name__ == "__main__":
    main()
