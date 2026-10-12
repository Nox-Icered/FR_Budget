"""Met en table les prestations des comptes de la protection sociale et la distribution des
pensions (DREES), lot 2.8.

Sources (voir registres/datasets.yaml) :

- data/raw/indexation/drees_comptes_protection_sociale.csv : export CSV (séparateur
  point-virgule) du jeu « Les comptes de la protection sociale » de data.drees, prestations par
  code (ps_code), par régime et par secteur institutionnel (si_code), en millions d'euros ;
- data/raw/indexation/drees_eir2020_distribution_pensions.xlsx : DREES, EIR 2020, tableau 5,
  distribution de la pension mensuelle brute totale des retraités de droit direct d'un régime
  de base, fin 2020 (colonne « Ensemble », en % des retraités, tranches de 100 euros).

Sorties :

- data/processed/indexation/prestations_apu.csv (annee, ps_code, ps_lib, si_code, millions) :
  prestations au niveau le plus fin (ps_niveau 4), lignes de total de chaque sous-secteur des
  administrations publiques (si_niveau 1) ;
- data/processed/indexation/distribution_pensions_2020.csv (borne_basse, borne_haute,
  part_pourcent) : la dernière tranche (« Supérieur à 4500 euros ») n'a pas de borne haute.

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/indexation/extraire_drees.py
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
BRUTES = RACINE / "data" / "raw" / "indexation"
SORTIES = RACINE / "data" / "processed" / "indexation"
SOUS_SECTEURS_APU = ("S13111", "S13112", "S1313", "S13141", "S13142")
NIVEAU_PRESTATION = "4"
NIVEAU_SOUS_SECTEUR = "1"
FEUILLE_EIR = "pension brute totale "
TRANCHE = re.compile(r"De (\d+) à (\d+) euros")
DERNIERE_TRANCHE = re.compile(r"Supérieur à (\d+) euros")
COLONNE_ENSEMBLE = 3


def prestations() -> list[dict[str, object]]:
    lignes = []
    with (BRUTES / "drees_comptes_protection_sociale.csv").open(encoding="utf-8-sig") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if (
                r["ps_niveau"] == NIVEAU_PRESTATION
                and r["si_niveau"] == NIVEAU_SOUS_SECTEUR
                and r["si_code"] in SOUS_SECTEURS_APU
            ):
                lignes.append(
                    {
                        "annee": int(r["annee"]),
                        "ps_code": r["ps_code"],
                        "ps_lib": r["ps_lib"],
                        "si_code": r["si_code"],
                        "millions": r["val"],
                    }
                )
    lignes.sort(key=lambda r: (r["annee"], r["ps_code"], r["si_code"]))
    return lignes


def distribution() -> list[dict[str, object]]:
    classeur = CalamineWorkbook.from_path(BRUTES / "drees_eir2020_distribution_pensions.xlsx")
    lignes: list[dict[str, object]] = []
    for ligne in classeur.get_sheet_by_name(FEUILLE_EIR).to_python():
        libelle = str(ligne[0])
        if m := TRANCHE.fullmatch(libelle):
            bornes = (int(m[1]), int(m[2]))
        elif m := DERNIERE_TRANCHE.fullmatch(libelle):
            bornes = (int(m[1]), "")
        else:
            continue
        lignes.append(
            {
                "borne_basse": bornes[0],
                "borne_haute": bornes[1],
                "part_pourcent": ligne[COLONNE_ENSEMBLE],
            }
        )
    return lignes


def ecrire(nom: str, lignes: list[dict[str, object]]) -> None:
    SORTIES.mkdir(parents=True, exist_ok=True)
    with (SORTIES / nom).open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def main() -> None:
    ecrire("prestations_apu.csv", prestations())
    ecrire("distribution_pensions_2020.csv", distribution())


if __name__ == "__main__":
    main()
