"""Met en table les projections du COR utilisées par le module retraites (lot 3.1).

Source (voir registres/datasets.yaml) : data/raw/retraites/cor_ra2026_donnees_partie2.xlsx,
fichier des tableaux et figures de la partie 2 du rapport annuel du COR de juin 2026, scénario
de référence :

- figure 2.2 : dépenses du système de retraite, en part du PIB ;
- figure 2.8 : ressources du système de retraite, en part du PIB ;
- figure 2.24 : pension moyenne relative, âge effectif moyen de départ et taux de prélèvement
  global, à législation inchangée (« Sc. Ref ») et au niveau qui assure l'équilibre chaque
  année (« Niveau pour assurer l'équilibre »), un seul levier variant à la fois.

Les valeurs sont repérées par la colonne de leur année dans la ligne d'en-tête de chaque
feuille (les séries projetées commencent en 2024 ou 2025 selon la figure).

Sortie : data/processed/retraites/cor_2026_reference.csv (annee, depenses_pib,
ressources_pib, pension_relative_ref, pension_relative_equilibre, age_ref, age_equilibre,
taux_ref, taux_equilibre), années communes aux trois figures, valeurs telles que publiées
(parts et taux en fraction, âges en années).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/retraites/extraire_cor.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
BRUTES = RACINE / "data" / "raw" / "retraites" / "cor_ra2026_donnees_partie2.xlsx"
SORTIE = RACINE / "data" / "processed" / "retraites" / "cor_2026_reference.csv"
REFERENCE = "Sc. Ref"
EQUILIBRE = "Niveau pour assurer l'équilibre"
# Ordre des blocs de la figure 2.24 : pension relative, âge, taux de prélèvement.
BLOCS_224 = ("pension_relative", "age", "taux")

Ligne = list[object]


def _feuille(nom: str) -> list[Ligne]:
    return [list(r) for r in CalamineWorkbook.from_path(str(BRUTES)).get_sheet_by_name(nom).to_python()]


def _colonnes_annees(lignes: list[Ligne]) -> dict[int, int]:
    """Colonne de chaque année, d'après la première ligne d'en-tête qui contient des années."""
    for ligne in lignes:
        annees = {
            int(v): i
            for i, v in enumerate(ligne)
            if isinstance(v, (int, float)) and not isinstance(v, bool) and 1990 < v < 2100
        }
        if len(annees) > 10:
            return annees
    msg = "en-tête des années introuvable"
    raise ValueError(msg)


def _series(lignes: list[Ligne], etiquette: str) -> list[dict[int, float]]:
    """Séries des lignes dont une cellule vaut ``etiquette``, dans l'ordre de la feuille."""
    colonnes = _colonnes_annees(lignes)
    resultat = []
    for ligne in lignes:
        if etiquette in ligne:
            serie = {
                a: float(ligne[c])
                for a, c in colonnes.items()
                if c < len(ligne) and isinstance(ligne[c], (int, float))
            }
            resultat.append(serie)
    return resultat


def reference() -> list[dict[str, object]]:
    depenses = _series(_feuille("Fig 2.2"), REFERENCE)[0]
    ressources = _series(_feuille("Fig 2.8"), REFERENCE)[0]
    fig = _feuille("Fig 2.24")
    refs = _series(fig, REFERENCE)[: len(BLOCS_224)]
    equilibres = _series(fig, EQUILIBRE)[: len(BLOCS_224)]
    series = {"depenses_pib": depenses, "ressources_pib": ressources}
    for bloc, ref, eq in zip(BLOCS_224, refs, equilibres, strict=True):
        series[f"{bloc}_ref"] = ref
        series[f"{bloc}_equilibre"] = eq
    annees = sorted(set.intersection(*(set(s) for s in series.values())))
    return [{"annee": a, **{k: s[a] for k, s in series.items()}} for a in annees]


def main() -> None:
    lignes = reference()
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    print(f"{SORTIE.relative_to(RACINE)} : {len(lignes)} années")


if __name__ == "__main__":
    main()
