"""Met en table les agrégats des comptes consolidés des collectivités (OFGL), lot 2.6.

Sources (voir registres/datasets.yaml) : réponses de l'API de data.ofgl.fr, enregistrées telles
que reçues dans data/raw/dotations_collectivites/ofgl_<niveau>_agregats.json (somme par exercice
de quatre agrégats : dépenses d'investissement hors remboursements, concours de l'État, dotation
globale de fonctionnement, péréquations et compensations fiscales). Niveaux : communes,
groupements à fiscalité propre, départements, régions. Montants en euros, sans arrondi.

Sortie : data/processed/dotations_collectivites/ofgl_agregats.csv (niveau, annee, agregat,
euros).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/dotations_collectivites/extraire_ofgl.py
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

RACINE = Path(__file__).parents[2]
BRUTES = RACINE / "data" / "raw" / "dotations_collectivites"
SORTIE = RACINE / "data" / "processed" / "dotations_collectivites" / "ofgl_agregats.csv"
NIVEAUX = ("communes", "gfp", "departements", "regions")


def main() -> None:
    lignes = []
    for niveau in NIVEAUX:
        contenu = json.loads((BRUTES / f"ofgl_{niveau}_agregats.json").read_text(encoding="utf-8"))
        for r in contenu["results"]:
            lignes.append(
                {
                    "niveau": niveau,
                    "annee": int(r["exer"][:4]),
                    "agregat": r["agregat"],
                    "euros": r["montant"],
                }
            )
    lignes.sort(key=lambda r: (r["niveau"], r["annee"], r["agregat"]))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


if __name__ == "__main__":
    main()
