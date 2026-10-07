"""Refuse tout fichier suivi par git qui ressemble à des micro-données d'enquête.

Les micro-données d'enquête (ERFS, par exemple) ne sont pas publiables : elles ne doivent
jamais être committées. Ce contrôle tourne en pré-commit et en intégration continue.
Il complète ``.gitignore`` : il attrape aussi les fichiers ajoutés de force.

Usage : ``python3 outils/verifier_donnees_interdites.py``
"""

from __future__ import annotations

import re
import subprocess
import sys

# Formats de fichiers des logiciels statistiques utilisés pour diffuser des micro-données.
EXTENSIONS_INTERDITES = (".sas7bdat", ".sas7bcat", ".dta", ".sav", ".zsav", ".por", ".xpt")

# Enquêtes dont les micro-données sont sous accès restreint (liste à compléter au besoin).
MOTIFS_INTERDITS = re.compile(r"erfs", re.IGNORECASE)


def fichiers_suivis() -> list[str]:
    sortie = subprocess.run(
        ["git", "ls-files", "-z"], check=True, capture_output=True, text=True
    ).stdout
    return [chemin for chemin in sortie.split("\0") if chemin]


def fichiers_interdits(chemins: list[str]) -> list[str]:
    return [
        chemin
        for chemin in chemins
        if chemin.lower().endswith(EXTENSIONS_INTERDITES)
        or (MOTIFS_INTERDITS.search(chemin) and not chemin.startswith(("outils/", "docs/")))
    ]


def main() -> int:
    interdits = fichiers_interdits(fichiers_suivis())
    if interdits:
        print("Fichiers refusés (micro-données d'enquête possibles) :", file=sys.stderr)
        for chemin in interdits:
            print(f"  {chemin}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
