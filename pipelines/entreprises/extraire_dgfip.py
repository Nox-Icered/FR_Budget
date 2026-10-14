"""Met en table l'impôt sur les sociétés brut et le résultat fiscal par taille d'entreprise et
par secteur (module « entreprises »).

Sources (voir registres/datasets.yaml) : tableaux des notes DGFiP Statistiques n° 51 (impôt
2025, onglets « Tableau 1 » et « Tableau 2 ») et n° 39 (impôt 2024, mêmes onglets, présentés
autrement : montants en euros, tailles en colonnes). Valeurs reprises sans calcul, converties
en milliards d'euros et en nombre d'entreprises.

Sorties :

- data/processed/entreprises/is_taille.csv (annee, categorie, entreprises, resultat_fiscal_md,
  is_brut_md) : très petites, petites et moyennes, de taille intermédiaire, grandes ;
- data/processed/entreprises/is_secteur.csv (annee, secteur, entreprises, resultat_fiscal_md,
  is_brut_md) : les dix secteurs de la note, sans les lignes de total ni « dont ».

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/entreprises/extraire_dgfip.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
DGFIP = RACINE / "data" / "raw" / "impot_societes" / "dgfip"
SORTIE = RACINE / "data" / "processed" / "entreprises"
EUROS_PAR_MILLIARD = 1e9
MILLIERS = 1000
CATEGORIES = {
    "Très petites entreprises": "tpe",
    "Petites et moyennes entreprises": "pme",
    "Entreprises de taille intermédiaire": "eti",
    "Grandes Entreprises": "ge",
}
EXCLUS = ("total", "tous secteurs", "dont ")


def _feuille(fichier: str, nom: str) -> list[list[object]]:
    lignes: list[list[object]] = CalamineWorkbook.from_path(str(DGFIP / fichier)).get_sheet_by_name(
        nom
    ).to_python()
    return lignes


def _nombre(valeur: object) -> float:
    return float(str(valeur).replace(" ", "").replace(" ", "").replace(",", "."))


def taille_2025() -> list[dict[str, object]]:
    sortie = []
    for ligne in _feuille("dgfip_stat_51_is-2025.xlsx", "Tableau 2"):
        libelle = str(ligne[0]).strip()
        if libelle in CATEGORIES:
            sortie.append(
                {
                    "annee": 2025,
                    "categorie": CATEGORIES[libelle],
                    "entreprises": round(_nombre(ligne[1]) * MILLIERS),
                    "resultat_fiscal_md": _nombre(ligne[2]),
                    "is_brut_md": _nombre(ligne[4]),
                }
            )
    return sortie


def taille_2024() -> list[dict[str, object]]:
    lignes = _feuille("dgfip_stat_39_is-2024.xlsx", "Tableau 2")
    en_tete = next(ligne for ligne in lignes if str(ligne[0]).startswith("Taille"))
    colonnes = {j: CATEGORIES[str(c).strip()] for j, c in enumerate(en_tete) if str(c).strip() in CATEGORIES}
    valeurs = {str(ligne[0]).strip(): ligne for ligne in lignes}
    return [
        {
            "annee": 2024,
            "categorie": categorie,
            "entreprises": round(_nombre(valeurs["Nombre d'entreprises (en milliers)"][j])),
            "resultat_fiscal_md": _nombre(valeurs["Résultat fiscal (en Md€)"][j])
            / EUROS_PAR_MILLIARD,
            "is_brut_md": _nombre(valeurs["IS brut (en Md€)"][j]) / EUROS_PAR_MILLIARD,
        }
        for j, categorie in colonnes.items()
    ]


def _secteur_retenu(libelle: str) -> bool:
    return bool(libelle) and not libelle.lower().startswith(EXCLUS)


def secteur_2025() -> list[dict[str, object]]:
    sortie = []
    for ligne in _feuille("dgfip_stat_51_is-2025.xlsx", "Tableau 1"):
        libelle = str(ligne[0]).strip()
        if not _secteur_retenu(libelle) or not isinstance(ligne[2], float):
            continue
        sortie.append(
            {
                "annee": 2025,
                "secteur": libelle,
                "entreprises": round(_nombre(ligne[6]) * MILLIERS),
                "resultat_fiscal_md": _nombre(ligne[2]),
                "is_brut_md": _nombre(ligne[5]),
            }
        )
    return sortie


def secteur_2024() -> list[dict[str, object]]:
    sortie = []
    for ligne in _feuille("dgfip_stat_39_is-2024.xlsx", "Tableau 1"):
        libelle = str(ligne[0]).strip()
        if not _secteur_retenu(libelle) or not isinstance(ligne[1], float):
            continue
        sortie.append(
            {
                "annee": 2024,
                "secteur": libelle,
                "entreprises": round(_nombre(ligne[5])),
                "resultat_fiscal_md": _nombre(ligne[1]) / EUROS_PAR_MILLIARD,
                "is_brut_md": _nombre(ligne[4]) / EUROS_PAR_MILLIARD,
            }
        )
    return sortie


def _ecrire(nom: str, lignes: list[dict[str, object]]) -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    with (SORTIE / nom).open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)
    print(f"{nom} : {len(lignes)} lignes")


def main() -> None:
    _ecrire("is_taille.csv", taille_2025() + taille_2024())
    _ecrire("is_secteur.csv", secteur_2025() + secteur_2024())


if __name__ == "__main__":
    main()
