"""Extrait de l'Ageing Report 2024 les séries françaises de la baseline après 2030 (lot 1.3).

Source : Commission européenne et comité de politique économique, « 2024 Ageing Report »,
annexe statistique de toutes les fiches pays, onglets FRa (hypothèses démographiques et
macroéconomiques), FRb (retraites) et FRc (santé, dépendance, éducation, coût total du
vieillissement), dans data/raw/baseline/commission_europeenne/ (voir registres/datasets.yaml,
``ce_ageing_report_2024_annexe_pays_xlsx``).

Les valeurs sont reprises sans arrondi ni calcul. Les lignes « diff. from baseline » sont des
écarts au scénario de référence, en points de PIB.

Sortie : data/processed/baseline/ageing_report_2024_fr.csv (annee, indicateur, valeur, unite,
onglet).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/baseline/extraire_ageing_report.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
SOURCE = (
    RACINE
    / "data"
    / "raw"
    / "baseline"
    / "commission_europeenne"
    / "2024_Ageing_Report-Statistical_annex_all_countryfiches.xlsx"
)
SORTIE = RACINE / "data" / "processed" / "baseline" / "ageing_report_2024_fr.csv"

# (onglet, titre de la section, libellé de ligne, indicateur, unité). Le libellé est cherché
# après le titre de section, ce qui distingue les lignes homonymes (« Baseline »).
LIGNES = (
    (
        "FRa",
        "Macroeconomic assumptions",
        "Potential GDP (growth rate)",
        "croissance_potentielle",
        "%",
    ),
    ("FRa", "Macroeconomic assumptions", "HICP (growth rate)", "ipc", "%"),
    ("FRa", "Macroeconomic assumptions", "Nominal interest rate", "taux_nominal", "%"),
    ("FRb", "Baseline as % of GDP", "Public pensions, gross", "retraites", "% du PIB"),
    ("FRc", "Health care spending as % of GDP", "Baseline", "sante", "% du PIB"),
    ("FRc", "Long-term care spending as % of GDP", "Baseline", "dependance", "% du PIB"),
    ("FRc", "Education spending as % of GDP", "Baseline", "education", "% du PIB"),
    ("FRc", "Total spending as % of GDP", "Baseline", "cout_vieillissement", "% du PIB"),
    *(
        (
            "FRc",
            "Total cost of ageing as % of GDP -  (diff. from baseline)",
            libelle,
            f"cout_vieillissement_ecart_{code}",
            "points de PIB",
        )
        for libelle, code in (
            ("Risk scenario (health care & long-term care)", "risque_sante_dependance"),
            ("High life expectancy (+2 years)", "esperance_vie_haute"),
            ("Higher migration (+33%)", "migration_haute"),
            ("Lower migration (-33%)", "migration_basse"),
            ("Lower fertility (-20%)", "fecondite_basse"),
            ("Higher employment rate of older workers (+10 pps)", "emploi_seniors_haut"),
            ("Higher TFP growth (+0.2 pps)", "pgf_haute"),
            ("Lower TFP growth (-0.2 pps)", "pgf_basse"),
        )
    ),
)


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
    for onglet, section, libelle, indicateur, unite in LIGNES:
        lignes = classeur.get_sheet_by_name(onglet).to_python()
        debut = next((i for i, r in enumerate(lignes) if _libelle(r) == section), None)
        if debut is None:
            msg = f"section absente : {onglet} / {section!r}"
            raise ValueError(msg)
        en_tete = _annees(lignes[debut])
        ligne = next((r for r in lignes[debut + 1 :] if _libelle(r) == libelle), None)
        if ligne is None or not en_tete:
            msg = f"ligne absente : {onglet} / {section!r} / {libelle!r}"
            raise ValueError(msg)
        resultats.extend(
            (annee, indicateur, float(ligne[colonne]), unite, onglet)
            for colonne, annee in en_tete
            if isinstance(ligne[colonne], float)
        )
    return resultats


def main() -> None:
    lignes = extraire(CalamineWorkbook.from_path(str(SOURCE)))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.writer(f, lineterminator="\n")
        ecrivain.writerow(["annee", "indicateur", "valeur", "unite", "onglet"])
        ecrivain.writerows(sorted(lignes))


if __name__ == "__main__":
    main()
