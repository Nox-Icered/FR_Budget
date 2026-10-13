"""Écrit les déclarations des ménages types, à soumettre au simulateur d'impots.gouv.fr.

Sortie : registres/references/menages/cas_impot_revenu.json (une entrée par ménage type), lue
par outils/references_impots/generer.mjs.

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/menages/cas_impot.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fr_budget.menages.types import ANNEE, PROFILS, declaration

SORTIE = (
    Path(__file__).parents[2] / "registres" / "references" / "menages" / "cas_impot_revenu.json"
)


def main() -> None:
    cas = [{"id": i, "revenus": ANNEE, "declaration": declaration(i)} for i in PROFILS]
    SORTIE.write_text(
        json.dumps({"cas": cas}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{SORTIE.name} : {len(cas)} cas")


if __name__ == "__main__":
    main()
