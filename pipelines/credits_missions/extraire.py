"""Extrait les crédits de paiement par programme : PLF 2026 et exécution 2023-2025 (lot 2.5).

Sources (voir registres/datasets.yaml) :

- « PLF 2026 - Budget vert » (direction du Budget, data.economie.gouv.fr) : crédits de paiement
  par action, exécution 2024, LFI 2025 et PLF 2026 ; seules les lignes « Crédits budgétaires »
  sont reprises, sommées par programme ;
- projets de loi relatifs aux résultats de la gestion (PLRG) 2023, 2024 et 2025, annexe 1,
  état des crédits de paiement du budget général (DGFiP, data.economie.gouv.fr) : crédits votés
  en LFI et dépenses constatées par programme et par titre, sommés par programme.

Les fichiers PLRG sont publiés en UTF-8 dont les caractères accentués ont été encodés deux
fois : ils sont décodés une seconde fois quand c'est possible. Montants en euros, sans arrondi.

Sorties :

- data/processed/credits_missions/plf2026_programmes.csv (mission, programme, libelle,
  execution_2024, lfi_2025, plf_2026) ;
- data/processed/credits_missions/plrg_programmes.csv (exercice, mission, programme, libelle,
  lfi, depenses_constatees).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/credits_missions/extraire.py
"""

from __future__ import annotations

import csv
import re
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).parents[2]
BRUTES = RACINE / "data" / "raw" / "credits_missions"
SORTIES = RACINE / "data" / "processed" / "credits_missions"
BUDGET_VERT = BRUTES / "plf2026_budget_vert.csv"
EXERCICES_PLRG = (2023, 2024, 2025)
CREDITS = "Crédits budgétaires"
COLONNES_BV = {
    "execution_2024": "execution_2024_cp",
    "lfi_2025": "lfi_2025_cp_ou_prevision_2025_si_depense_fiscale",
    "plf_2026": "plf_2026_cp_ou_prevision_2026_si_depense_fiscale",
}
NUMERO_PROGRAMME = re.compile(r"^(.*?)\s*-\s*(\d+)\s*$")


def redecoder(texte: str) -> str:
    """Corrige un texte UTF-8 encodé deux fois (« Ã© » pour « é ») ; inchangé sinon."""
    try:
        return texte.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return texte


def montant(cellule: str) -> float:
    cellule = cellule.strip()
    return float(cellule.replace(",", ".")) if cellule else 0.0


def budget_vert() -> list[dict[str, object]]:
    sommes: dict[tuple[str, str], dict[str, float]] = defaultdict(
        lambda: dict.fromkeys(COLONNES_BV, 0.0)
    )
    libelles: dict[tuple[str, str], str] = {}
    with BUDGET_VERT.open(encoding="utf-8-sig") as f:
        for ligne in csv.DictReader(f, delimiter=";"):
            if ligne["type_depense"] != CREDITS:
                continue
            # Les lignes de mesures de périmètre n'ont pas toujours de libellé de programme.
            cle = (ligne["mission"], ligne["numero_programme"])
            if ligne["programme"]:
                libelles[cle] = ligne["programme"]
            for nom, colonne in COLONNES_BV.items():
                sommes[cle][nom] += montant(ligne[colonne])
    return [
        {"mission": m, "programme": p, "libelle": libelles.get((m, p), ""), **valeurs}
        for (m, p), valeurs in sorted(sommes.items())
    ]


def plrg(exercice: int) -> list[dict[str, object]]:
    sommes: dict[tuple[str, str, str], dict[str, float]] = defaultdict(
        lambda: {"lfi": 0.0, "depenses_constatees": 0.0}
    )
    with (BRUTES / f"plrg{exercice}_annexe1_etat_cp.csv").open(encoding="utf-8") as f:
        for ligne in csv.DictReader(f, delimiter=";"):
            programme = NUMERO_PROGRAMME.match(redecoder(ligne["Programme"]))
            if programme is None:
                msg = f"PLRG {exercice} : numéro de programme absent : {ligne['Programme']!r}"
                raise ValueError(msg)
            cle = (redecoder(ligne["Mission"]), programme.group(2), programme.group(1))
            sommes[cle]["lfi"] += montant(ligne["LFI"])
            sommes[cle]["depenses_constatees"] += montant(ligne["Depenses_constatees"])
    return [
        {"exercice": exercice, "mission": m, "programme": p, "libelle": lib, **valeurs}
        for (m, p, lib), valeurs in sorted(sommes.items())
    ]


def _ecrire(nom: str, lignes: list[dict[str, object]]) -> None:
    SORTIES.mkdir(parents=True, exist_ok=True)
    with (SORTIES / nom).open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def main() -> None:
    _ecrire("plf2026_programmes.csv", budget_vert())
    _ecrire("plrg_programmes.csv", [ligne for e in EXERCICES_PLRG for ligne in plrg(e)])


if __name__ == "__main__":
    main()
