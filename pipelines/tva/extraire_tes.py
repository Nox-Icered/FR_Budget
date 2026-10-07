"""Extrait le tableau des entrées-sorties (TES) A38 d'une année en tables longues.

Source : INSEE, comptes nationaux annuels base 2020, « Tableaux de synthèse - TES et TEE »,
fichiers TES_38_{année}_fr.xlsx (à partir de 2020) ou TES_38_{année}.xlsx dans l'archive
TES_38_1978_2019_fr.zip. Millions d'euros courants. Voir registres/datasets.yaml.

Tables produites dans data/processed/tva/ :
- tes_{année}_tei.csv : consommations intermédiaires, produit par branche (prix d'acquisition) ;
- tes_{année}_tef.csv : emplois finals par produit (consommation finale par secteur,
  FBCF par secteur), prix d'acquisition ;
- tes_{année}_trp.csv : ressources par produit, dont « taxes du type TVA » ;
- tes_{année}_cpr.csv : production des branches (P1, P11 marchande, P12, P13 non marchande).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/tva/extraire_tes.py 2022
"""

from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path
from typing import Any

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
DOSSIER = RACINE / "data" / "raw" / "tva" / "insee"
SORTIE = RACINE / "data" / "processed" / "tva"
DERNIERE_ANNEE_ARCHIVE = 2019

# Lignes d'en-tête de chaque feuille (index de ligne, à partir de 0).
EN_TETE = {"TRP": 3, "TEF": 3, "TEI": 2, "CPR_CEB": 2}
LIGNES_HORS_PRODUITS = {"PCHTR", "PCAFAB", "TOTAL"}


def classeur(annee: int) -> CalamineWorkbook:
    if annee <= DERNIERE_ANNEE_ARCHIVE:
        with zipfile.ZipFile(DOSSIER / "TES_38_1978_2019_fr.zip") as archive:
            contenu = archive.read(f"TES_38_{annee}.xlsx")
        return CalamineWorkbook.from_filelike(io.BytesIO(contenu))
    return CalamineWorkbook.from_path(DOSSIER / f"TES_38_{annee}_fr.xlsx")


def nombre(valeur: Any) -> float:
    return float(valeur) if valeur not in ("", None) else 0.0


def table_produits(feuille: list[list[Any]], ligne_en_tete: int) -> list[tuple[str, str, float]]:
    """Lignes « produit » par colonnes nommées, en format long (produit, colonne, valeur)."""
    colonnes = [str(c).strip() for c in feuille[ligne_en_tete]]
    sortie = []
    for ligne in feuille[ligne_en_tete + 1 :]:
        code = str(ligne[1]).strip()
        if not code or code in LIGNES_HORS_PRODUITS:
            continue
        for j in range(2, len(colonnes)):
            if colonnes[j] and colonnes[j] != "TOTAL":
                sortie.append((code, colonnes[j], nombre(ligne[j])))
    return sortie


def ecrire(nom: str, entete: list[str], lignes: list[tuple[Any, ...]]) -> None:
    with (SORTIE / nom).open("w", newline="", encoding="utf-8") as f:
        ecrivain = csv.writer(f)
        ecrivain.writerow(entete)
        ecrivain.writerows(lignes)


def main(annee: int) -> None:
    tes = classeur(annee)
    feuilles = {nom: tes.get_sheet_by_name(nom).to_python() for nom in EN_TETE}
    ecrire(
        f"tes_{annee}_tei.csv",
        ["produit", "branche", "millions_euros"],
        table_produits(feuilles["TEI"], EN_TETE["TEI"]),
    )
    tef = feuilles["TEF"]
    # En-tête de la TEF sur deux lignes : « Dépense de consommation finale » puis
    # « Formation brute de capital fixe » ; on préfixe les secteurs par l'emploi.
    groupes, secteurs = tef[EN_TETE["TEF"] - 1], tef[EN_TETE["TEF"]]
    emploi = ""
    noms = []
    for g, s in zip(groupes, secteurs, strict=True):
        if str(g).startswith("Dépense"):
            emploi = "CF"
        elif str(g).startswith("Formation"):
            emploi = "FBCF"
        nom = str(s).strip()
        if nom.startswith(("Acq", "Variation", "FBC totale", "Exportations", "Total des emplois")):
            emploi = ""
        noms.append(f"{emploi} {nom}".strip() if nom else "")
    tef[EN_TETE["TEF"]] = noms
    ecrire(
        f"tes_{annee}_tef.csv",
        ["produit", "emploi", "millions_euros"],
        table_produits(tef, EN_TETE["TEF"]),
    )
    ecrire(
        f"tes_{annee}_trp.csv",
        ["produit", "colonne", "millions_euros"],
        table_produits(feuilles["TRP"], EN_TETE["TRP"]),
    )
    cpr = feuilles["CPR_CEB"]
    branches = [str(c).strip() for c in cpr[EN_TETE["CPR_CEB"]]]
    lignes = []
    for ligne in cpr[EN_TETE["CPR_CEB"] + 1 :]:
        operation = str(ligne[0]).strip()
        if operation in {"P1", "P11", "P12", "P13"}:
            for j in range(2, len(branches)):
                if branches[j] and branches[j] != "TOTAL":
                    lignes.append((operation, branches[j], nombre(ligne[j])))
    # P1 apparaît deux fois dans la feuille : on garde la première occurrence.
    vues: set[tuple[str, str]] = set()
    uniques = [r for r in lignes if (r[0], r[1]) not in vues and not vues.add((r[0], r[1]))]
    ecrire(f"tes_{annee}_cpr.csv", ["operation", "branche", "millions_euros"], uniques)


if __name__ == "__main__":
    main(int(sys.argv[1]))
