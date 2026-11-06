"""Extrait les comptes nationaux distribués par décile de niveau de vie (lot V2 « déciles »).

Source (registres/datasets.yaml, ``insee_cnd_2023_t101``) : INSEE, comptes nationaux distribués
2023, base 2020, tableau CND.101 « Comptes nationaux distribués selon les vingtièmes de niveau de
vie usuel », feuilles CND_2020 à CND_2023, en milliards d'euros
(``data/raw/deciles/insee_cnd_2023_T_CND_101.xlsx``, tel que téléchargé).

Transformation :

- lignes retenues par leur libellé exact (``LIGNES`` : identifiant -> libellé) ;
- déciles : somme des vingtièmes deux à deux (V1 + V2 = premier décile, etc.) ;
- le script vérifie, pour chaque ligne et chaque année, que la somme des vingtièmes redonne la
  colonne « Ensemble » à l'arrondi près (``TOLERANCE``, valeurs publiées au dixième).

Sortie : data/processed/deciles/cnd_deciles.csv (annee, ligne, d1 ... d10, ensemble), en Md€
(nombres d'unités de consommation et d'individus : en millions).

Références de validation (même script) : effet par dixième de niveau de vie, en euros par an, de
deux réformes évaluées par l'Insee (France, portrait social), colonnes retenues par leur
libellé : réforme de la prime d'activité de 2018 (édition 2019, dossier 3, figure 7,
``data/raw/deciles/insee_fps2019_D3.xls``) et baisse de l'impôt sur le revenu de 2020 (édition
2022, dossier 2, figure 4, effet en euros, ``data/raw/deciles/insee_fps2022_D2.xlsx``). Sortie :
data/processed/deciles/validation_insee.csv (reference, d1 ... d10).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/deciles/extraire_cnd.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
FICHIER = RACINE / "data" / "raw" / "deciles" / "insee_cnd_2023_T_CND_101.xlsx"
SORTIE = RACINE / "data" / "processed" / "deciles" / "cnd_deciles.csv"
ANNEES = (2020, 2021, 2022, 2023)
VINGTIEMES = 20
DECILES = 10
TOLERANCE = 0.15
"""Écart admis, en Md€, entre la somme des vingtièmes et l'ensemble (arrondis au dixième)."""

LIGNES = {
    "salaires_nets": "Revenus salariaux nets",
    "revenus_mixtes": "Revenus mixtes des indépendants",
    "revenus_propriete": "Revenus nets de la propriété (intérêts, dividendes, etc.)",
    "taxes_produits": "Taxes sur les produits (TVA, TICPE, acises, DMTO, etc.)",
    "impot_societes": "Impôt sur les sociétés",
    "csg": "Contribution sociale généralisée (CSG)",
    "impot_revenu": "Impôt sur le revenu (IR)",
    "cotisations_retraite": "Cotisations sociales retraite",
    "cotisations_chomage": "Cotisations sociales chômage",
    "cotisations_famille": "Cotisations sociales famille",
    "cotisations_autres": "Autres cotisations sociales (maladie, invalidité, ATMP)",
    "pensions_retraite": "Pensions de retraite",
    "allocations_chomage": "Allocations chômage",
    "famille": "Famille",
    "exclusion_sociale": "Exclusion sociale",
    "invalidite": "Invalidité",
    "revenu_disponible": "Revenu disponible net (RDN) des ménages (S14)",
    "unites_consommation": "Nombre d'unités de consommation (en millions)",
    "individus": "Nombre d'individus (en millions)",
}


def deciles(vingtiemes: list[float]) -> list[float]:
    """Somme des vingtièmes deux à deux."""
    if len(vingtiemes) != VINGTIEMES:
        msg = f"{VINGTIEMES} vingtièmes attendus, {len(vingtiemes)} lus"
        raise ValueError(msg)
    return [vingtiemes[2 * i] + vingtiemes[2 * i + 1] for i in range(DECILES)]


def extraire() -> list[list[object]]:
    classeur = CalamineWorkbook.from_path(str(FICHIER))
    sortie: list[list[object]] = []
    for annee in ANNEES:
        lignes = classeur.get_sheet_by_name(f"CND_{annee}").to_python()
        entete = [str(v).strip() for v in lignes[0]]
        colonnes = [entete.index(f"V{i}") for i in range(1, VINGTIEMES + 1)]
        ensemble = entete.index("Ensemble")
        par_libelle = {str(r[0]).strip(): r for r in lignes[1:] if r and r[0]}
        for ident, libelle in LIGNES.items():
            if libelle not in par_libelle:
                msg = f"{annee} : ligne absente : {libelle}"
                raise ValueError(msg)
            r = par_libelle[libelle]
            v = [float(r[c]) for c in colonnes]
            total = float(r[ensemble])
            if abs(sum(v) - total) > TOLERANCE * max(1.0, abs(total)) ** 0.5:
                msg = f"{annee} / {ident} : somme des vingtièmes {sum(v):.2f} / ensemble {total}"
                raise ValueError(msg)
            sortie.append([annee, ident, *[round(x, 6) for x in deciles(v)], total])
    return sortie


BRUT = RACINE / "data" / "raw" / "deciles"
VALIDATION = RACINE / "data" / "processed" / "deciles" / "validation_insee.csv"
LIGNES_DIXIEMES = (
    "Inférieur à D1",
    *(f"D{i} à D{i + 1}" for i in range(1, 9)),
    "Supérieur à D9",
)
REFERENCES = {
    # identifiant : (fichier, feuille, début du libellé de la colonne)
    "fps2019_prime_activite_2018": (
        "insee_fps2019_D3.xls",
        "Figure 7",
        "Réforme de la prime d'activité",
    ),
    "fps2022_baisse_impot_revenu_2020": (
        "insee_fps2022_D2.xlsx",
        "Figure 4",
        "Baisse de l'impôt",
    ),
}


def _norme(texte: object) -> str:
    return " ".join(str(texte).split())


def extraire_reference(fichier: str, feuille: str, colonne: str) -> list[float]:
    """Première colonne dont le libellé commence par ``colonne``, lignes des dixièmes."""
    lignes = CalamineWorkbook.from_path(str(BRUT / fichier)).get_sheet_by_name(feuille).to_python()
    position = next(
        (i, j)
        for i, r in enumerate(lignes)
        for j, v in enumerate(r)
        if _norme(v).startswith(colonne)
    )
    par_libelle = {_norme(r[0]): r for r in lignes[position[0] + 1 :] if r and r[0]}
    return [float(par_libelle[x][position[1]]) for x in LIGNES_DIXIEMES]


def main() -> None:
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["annee", "ligne", *[f"d{i}" for i in range(1, DECILES + 1)], "ensemble"])
        w.writerows(extraire())
    with VALIDATION.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["reference", *[f"d{i}" for i in range(1, DECILES + 1)]])
        for ident, (fichier, feuille, colonne) in REFERENCES.items():
            w.writerow([ident, *extraire_reference(fichier, feuille, colonne)])


if __name__ == "__main__":
    main()
