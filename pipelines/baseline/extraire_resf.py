"""Extrait du RESF 2027 les séries de la baseline 2025-2030 (lot 1.3 du plan).

Source : Direction générale du Trésor, « Tableaux RESF 2027.xlsx », annexé au rapport
économique, social et financier du PLF 2027, dans data/raw/baseline/tresor/ (voir
registres/datasets.yaml, ``plf2027_resf_tableaux_xlsx``).

Les valeurs sont reprises telles que publiées (arrondies au dixième), sans calcul. Les nombres
écrits en texte avec un signe moins typographique ou un trait d'union insécable sont convertis
en nombres.

Sortie : data/processed/baseline/resf_2027.csv (annee, indicateur, valeur, unite, tableau).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/baseline/extraire_resf.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
SOURCE = RACINE / "data" / "raw" / "baseline" / "tresor" / "Tableaux_RESF_2027.xlsx"
MOINS = chr(0x2212)
TRAIT_INSECABLE = chr(0x2011)
SORTIE = RACINE / "data" / "processed" / "baseline" / "resf_2027.csv"

# (onglet, titre du tableau, libellé de ligne, indicateur, unité)
LIGNES = (
    ("Finances publiques", "Tableau 21", "Solde public", "solde_public", "% du PIB"),
    (
        "Finances publiques",
        "Tableau 21",
        "Solde structurel *",
        "solde_structurel",
        "% du PIB potentiel",
    ),
    (
        "Finances publiques",
        "Tableau 21",
        "Ajustement structurel*",
        "ajustement_structurel",
        "points de PIB potentiel",
    ),
    (
        "Finances publiques",
        "Tableau 21",
        "Ajustement structurel primaire*",
        "ajustement_structurel_primaire",
        "points de PIB potentiel",
    ),
    ("Finances publiques", "Tableau 21", "Solde conjoncturel", "solde_conjoncturel", "% du PIB"),
    ("Finances publiques", "Tableau 21", "Dette publique", "dette", "% du PIB"),
    ("Finances publiques", "Tableau 21", "Croissance volume (%)", "croissance_volume", "%"),
    (
        "Finances publiques",
        "Tableau 21",
        "Croissance potentielle volume (%)",
        "croissance_potentielle",
        "%",
    ),
    (
        "Finances publiques",
        "Tableau 21",
        "Écart de production (points de PIB potentiel)",
        "ecart_production",
        "% du PIB potentiel",
    ),
    ("Perspectives éco_Fiche 7", "Tableau 1", "Déflateur du PIB", "deflateur", "%"),
    ("Perspectives éco_Fiche 7", "Tableau 1", "IPC (hors tabac)", "ipc", "%"),
    (
        "Annexe macro",
        "Tableau 8",
        "Taux obligataire à 10 ans en France (moyenne annuelle)",
        "taux_10_ans",
        "%",
    ),
    (
        "Annexe finances publiques",
        "Tableau 13",
        "6. Charge d'intérêt",
        "charge_interets",
        "% du PIB",
    ),
    (
        "Annexe finances publiques",
        "Tableau 13",
        "7. Solde primaire (1 + 6)",
        "solde_primaire",
        "% du PIB",
    ),
    (
        "Annexe finances publiques",
        "Tableau 13",
        "12. Composante conjoncturelle du solde public (0,57 * écart de production)",
        "composante_conjoncturelle",
        "% du PIB",
    ),
    (
        "Annexe finances publiques",
        "Tableau 14",
        "5. Flux de créances (en % du PIB)",
        "flux_creances",
        "% du PIB",
    ),
    (
        "Annexe finances publiques",
        "Tableau 14",
        "p.m.: Taux d'intérêt apparent sur la dette (%)*",
        "taux_apparent",
        "%",
    ),
    (
        "Finances publiques",
        "Tableau 4",
        "Croissance nominale du PIB (en\xa0%) (2)",
        "croissance_nominale",
        "%",
    ),
)


def nombre(cellule: object) -> float | None:
    """Nombre d'une cellule : flottant ou texte à virgule décimale ; None si vide."""
    if isinstance(cellule, (int, float)):
        return float(cellule)
    texte = str(cellule).strip().replace(MOINS, "-").replace(TRAIT_INSECABLE, "-").replace(",", ".")
    if not texte:
        return None
    return float(texte)


def _libelle(ligne: list[object]) -> str:
    """Premier texte non vide d'une ligne, espaces de bord retirés."""
    return next((str(c).strip() for c in ligne if str(c).strip()), "")


def _annees(ligne: list[object]) -> list[tuple[int, int]]:
    """Positions des années (colonne, année) dans une ligne d'en-tête."""
    return [
        (j, int(c))
        for j, c in enumerate(ligne)
        if isinstance(c, float) and c.is_integer() and 2000 <= c <= 2100  # noqa: PLR2004
    ]


def extraire(classeur: CalamineWorkbook) -> list[tuple[int, str, float, str, str]]:
    resultats = []
    for onglet, tableau, libelle, indicateur, unite in LIGNES:
        lignes = classeur.get_sheet_by_name(onglet).to_python()
        debut = next(
            i
            for i, r in enumerate(lignes)
            if any(str(c).startswith((f"{tableau}\xa0:", f"{tableau} :")) for c in r)
        )
        en_tete = next(_annees(r) for r in lignes[debut + 1 :] if _annees(r))
        ligne = next((r for r in lignes[debut + 1 :] if _libelle(r) == libelle.strip()), None)
        if ligne is None:
            msg = f"ligne absente : {onglet} / {tableau} / {libelle!r}"
            raise ValueError(msg)
        for colonne, annee in en_tete:
            valeur = nombre(ligne[colonne]) if colonne < len(ligne) else None
            if valeur is not None:
                resultats.append((annee, indicateur, valeur, unite, f"{onglet} / {tableau}"))
    return resultats


def main() -> None:
    lignes = extraire(CalamineWorkbook.from_path(str(SOURCE)))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(["annee", "indicateur", "valeur", "unite", "tableau"])
        ecrivain.writerows(sorted(lignes))


if __name__ == "__main__":
    main()
