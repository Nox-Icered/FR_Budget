"""Extrait les dépenses des APU par fonction (classification COFOG) depuis Eurostat.

Source : Eurostat, tableau gov_10a_exp (dépenses des administrations publiques par fonction),
France, millions d'euros, total des dépenses (TE), téléchargé au format JSON-stat dans
data/raw/apu/eurostat/gov_10a_exp_FR.json (voir registres/datasets.yaml). Ces données sont
transmises à Eurostat par l'INSEE.

Sortie : data/processed/apu/cofog.csv (annee, sous_secteur, cofog, libelle, milliards_euros).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/apu/extraire_cofog.py
"""

from __future__ import annotations

import csv
import json
from itertools import product
from pathlib import Path

RACINE = Path(__file__).parents[2]
SOURCE = RACINE / "data" / "raw" / "apu" / "eurostat" / "gov_10a_exp_FR.json"
SORTIE = RACINE / "data" / "processed" / "apu" / "cofog.csv"
MILLIONS_PAR_MILLIARD = 1000


def main() -> None:
    donnees = json.loads(SOURCE.read_text(encoding="utf-8"))
    dimensions = donnees["id"]
    categories = [
        sorted(donnees["dimension"][d]["category"]["index"].items(), key=lambda kv: kv[1])
        for d in dimensions
    ]
    libelles = donnees["dimension"]["cofog99"]["category"]["label"]
    valeurs = donnees["value"]
    lignes = []
    for position, combinaison in enumerate(product(*[[c for c, _ in cats] for cats in categories])):
        valeur = valeurs.get(str(position))
        if valeur is None:
            continue
        cles = dict(zip(dimensions, combinaison, strict=True))
        lignes.append(
            (
                int(cles["time"]),
                cles["sector"],
                cles["cofog99"],
                libelles[cles["cofog99"]],
                valeur / MILLIONS_PAR_MILLIARD,
            )
        )
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(["annee", "sous_secteur", "cofog", "libelle", "milliards_euros"])
        ecrivain.writerows(sorted(lignes))


if __name__ == "__main__":
    main()
