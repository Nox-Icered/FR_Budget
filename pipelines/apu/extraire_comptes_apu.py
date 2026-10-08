"""Extrait les comptes des administrations publiques (APU) par sous-secteur et par année.

Source : INSEE, comptes nationaux annuels base 2020, édition 2025 (compte semi-définitif des
APU du 28 août 2026). Voir registres/datasets.yaml :

- tableaux 3.201 à 3.212 (dépenses et recettes par sous-secteur) : total des dépenses, total
  des recettes, intérêts versés et reçus (D41), capacité ou besoin de financement (B9NF) ;
- tableau 3.101 : dette au sens de Maastricht par sous-secteur ;
- tableau 3.106 : déficit au sens de Maastricht par sous-secteur ;
- tableau 1.101 : produit intérieur brut (B1GQ).

Sortie : data/processed/apu/comptes_apu.csv, format long (annee, sous_secteur, indicateur,
milliards_euros). Les montants sont repris tels quels, sans arrondi.

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/apu/extraire_comptes_apu.py
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
BRUTES = RACINE / "data" / "raw" / "apu" / "insee"
SORTIE = RACINE / "data" / "processed" / "apu" / "comptes_apu.csv"

TABLEAUX_DEPENSES_RECETTES = {
    "S13": "t_3201_fr.xlsx",
    "S1311": "t_3202_fr.xlsx",
    "S13111": "t_3203_fr.xlsx",
    "S13112": "t_3204_fr.xlsx",
    "S1313": "t_3205_fr.xlsx",
    "S1314": "t_3212_fr.xlsx",
}
LIGNES_DEPENSES_RECETTES = {
    "Total des dépenses": "depenses",
    "Total des recettes": "recettes",
    "Capacité (+) ou besoin (-) de financement (B9NF)": "capacite_financement",
}
LIBELLE_INTERETS = "Intérêts (D41)"
"""Première occurrence : intérêts versés (dépenses) ; seconde : intérêts reçus (recettes)."""
LIBELLES_DEFICIT = {
    "S13 - Ensemble des administrations publiques": "S13",
    "S1311 - Administration publique centrale": "S1311",
    "S13111 - État": "S13111",
    "S13112 - Organismes divers d'administration centrale": "S13112",
    "S1313 - Administrations publiques locales": "S1313",
    "S1314 - Administrations de sécurité sociale": "S1314",
}


def feuille(fichier: str, nom: str | None = None) -> list[list[Any]]:
    classeur = CalamineWorkbook.from_path(BRUTES / fichier)
    feuilles = [f for f in classeur.sheet_names if f != "Métadonnées" and "notice" not in f]
    return classeur.get_sheet_by_name(nom or feuilles[0]).to_python()


def annees(lignes: list[list[Any]]) -> dict[int, int]:
    """Colonne de chaque année, lue sur la première ligne qui contient des années."""
    for ligne in lignes:
        trouvees = {}
        for j, v in enumerate(ligne):
            texte = str(v).removesuffix(".0").strip()
            if texte.isdigit() and len(texte) == 4:  # noqa: PLR2004 (année sur 4 chiffres)
                trouvees[int(texte)] = j
        if len(trouvees) > 5:  # noqa: PLR2004 (une ligne d'en-tête compte de nombreuses années)
            return trouvees
    msg = "aucune ligne d'années"
    raise ValueError(msg)


def nombre(v: Any) -> float | None:
    return float(v) if isinstance(v, (int, float)) else None


def extraire() -> list[tuple[int, str, str, float]]:
    sortie: list[tuple[int, str, str, float]] = []

    def ajouter(ligne: list[Any], colonnes: dict[int, int], secteur: str, indicateur: str) -> None:
        for an, j in colonnes.items():
            valeur = nombre(ligne[j]) if j < len(ligne) else None
            if valeur is not None:
                sortie.append((an, secteur, indicateur, valeur))

    for secteur, fichier in TABLEAUX_DEPENSES_RECETTES.items():
        lignes = feuille(fichier)
        colonnes = annees(lignes)
        interets = [lg for lg in lignes if str(lg[1]).strip() == LIBELLE_INTERETS]
        ajouter(interets[0], colonnes, secteur, "interets_verses")
        ajouter(interets[1], colonnes, secteur, "interets_recus")
        for lg in lignes:
            indicateur = LIGNES_DEPENSES_RECETTES.get(str(lg[1]).strip())
            if indicateur:
                ajouter(lg, colonnes, secteur, indicateur)

    # Dette au sens de Maastricht (en milliards ; on s'arrête avant le bloc en % du PIB).
    lignes = feuille("t_3101_fr.xlsx", "T_3101")
    colonnes = annees(lignes)
    for lg in lignes:
        if "En % du produit intérieur brut" in str(lg[1]):
            break
        if str(lg[0]).startswith("S13"):
            ajouter(lg, colonnes, str(lg[0]).strip(), "dette_maastricht")

    # Déficit au sens de Maastricht (bloc en milliards).
    lignes = feuille("t_3106_fr.xlsx")
    colonnes = annees(lignes)
    for lg in lignes:
        if "En % du produit intérieur brut" in str(lg[1]):
            break
        secteur = LIBELLES_DEFICIT.get(str(lg[1]).strip())
        if secteur:
            ajouter(lg, colonnes, secteur, "solde_maastricht")

    # PIB en valeur.
    lignes = feuille("T_1101_1103_fr.xlsx", "T_1101 en niveau")
    colonnes = annees(lignes)
    pib = next(lg for lg in lignes if str(lg[0]).strip() == "B1GQ")
    ajouter(pib, colonnes, "S1", "pib")
    return sortie


def main() -> None:
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(["annee", "sous_secteur", "indicateur", "milliards_euros"])
        ecrivain.writerows(sorted(extraire()))


if __name__ == "__main__":
    main()
