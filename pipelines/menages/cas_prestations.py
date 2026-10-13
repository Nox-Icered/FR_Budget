"""Écrit les cas des ménages types à soumettre au simulateur RSA - prime d'activité.

Sortie : registres/references/menages/cas_prestations.json (une entrée par ménage type qui
reçoit des prestations), lue par outils/references_prestations/generer.mjs. Méthode et choix :
``fr_budget.menages.prestations``.

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/menages/cas_prestations.py
"""

from __future__ import annotations

import json
from pathlib import Path

from fr_budget.menages.prestations import PROFILS_AVEC_PRESTATIONS, cas_simulateur

SORTIE = Path(__file__).parents[2] / "registres" / "references" / "menages" / "cas_prestations.json"


def main() -> None:
    cas = [cas_simulateur(i) for i in PROFILS_AVEC_PRESTATIONS]
    SORTIE.write_text(
        json.dumps({"cas": cas}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{SORTIE.name} : {len(cas)} cas")


if __name__ == "__main__":
    main()
