"""Extrait du Debt Sustainability Monitor 2025 de la Commission européenne la projection de la
dette française à politique inchangée, 2024-2036 (fiche France, partie II).

Source : Commission européenne, « Debt Sustainability Monitor 2025 », Institutional Paper 332,
février 2026, dans data/raw/baseline/commission_europeenne/ (voir registres/datasets.yaml,
``ce_dsm_2025_pdf``). Le texte est lu avec ``pdftotext -layout`` (poppler).

Valeurs reprises telles que publiées, sans calcul :

- tableau « France - baseline scenario (% of GDP) » : dette brute et solde primaire, 2024-2036 ;
- tableau « Overview of key fiscal sustainability risks » : dette en 2036 du scénario central et
  des quatre scénarios déterministes (solde primaire structurel historique, solde primaire plus
  bas, écart taux-croissance défavorable, tension financière).

Sorties : data/processed/baseline/ce_dsm_2025_france.csv (annee, dette, solde_primaire) et
data/processed/baseline/ce_dsm_2025_france_scenarios_2036.csv (scenario, dette_2036).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/baseline/extraire_dsm.py
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

RACINE = Path(__file__).parents[2]
SOURCE = RACINE / "data" / "raw" / "baseline" / "commission_europeenne" / "dsm_2025_ip332_en.pdf"
SORTIE = RACINE / "data" / "processed" / "baseline" / "ce_dsm_2025_france.csv"
SORTIE_SCENARIOS = (
    RACINE / "data" / "processed" / "baseline" / "ce_dsm_2025_france_scenarios_2036.csv"
)
TITRE_TABLEAU = "France - baseline scenario (% of GDP)"
SCENARIOS = ("central", "spb_historique", "spb_plus_bas", "r_g_defavorable", "tension_financiere")
# Nombres isolés par des espaces (les libellés comme « (1.1+1.2+1.3) » ne comptent pas).
NOMBRE = re.compile(r"(?<!\S)-?\d+\.\d(?!\S)")


def _nombres(ligne: str) -> list[float]:
    return [float(x) for x in NOMBRE.findall(ligne)]


def _texte() -> list[str]:
    sortie = subprocess.run(
        ["pdftotext", "-layout", str(SOURCE), "-"], check=True, capture_output=True, text=True
    )
    return sortie.stdout.splitlines()


def extraire(lignes: list[str]) -> tuple[list[tuple[int, float, float]], dict[str, float]]:
    debut = next(i for i, ligne in enumerate(lignes) if ligne.startswith(TITRE_TABLEAU))
    annees = [int(a) for a in re.findall(r"\b20\d\d\b", lignes[debut])]
    dette = next(lg for lg in lignes[debut:] if lg.startswith("Gross debt ratio"))
    solde = next(lg for lg in lignes[debut:] if "(1) Primary balance" in lg)
    valeurs_dette, valeurs_solde = _nombres(dette), _nombres(solde)
    if not len(annees) == len(valeurs_dette) == len(valeurs_solde):
        msg = "tableau de la fiche France : nombre de colonnes inattendu"
        raise ValueError(msg)
    # Dernière occurrence de la ligne de synthèse avant le tableau : celle de la fiche France.
    synthese = next(lg for lg in reversed(lignes[:debut]) if "Debt level (2036), % of GDP" in lg)
    niveaux = _nombres(synthese)
    if len(niveaux) != len(SCENARIOS) or niveaux[0] != valeurs_dette[-1]:
        msg = "synthèse de la fiche France : scénarios de 2036 inattendus"
        raise ValueError(msg)
    serie = list(zip(annees, valeurs_dette, valeurs_solde, strict=True))
    return serie, dict(zip(SCENARIOS, niveaux, strict=True))


def main() -> None:
    serie, scenarios = extraire(_texte())
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["annee", "dette", "solde_primaire"])
        w.writerows(serie)
    with SORTIE_SCENARIOS.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["scenario", "dette_2036"])
        w.writerows(scenarios.items())
    print(f"{SORTIE.relative_to(RACINE)} : {len(serie)} années ; scénarios 2036 : {scenarios}")


if __name__ == "__main__":
    main()
