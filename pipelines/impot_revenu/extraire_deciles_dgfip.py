"""Extrait les déciles de revenu fiscal de référence (RFR) par part publiés par la DGFiP.

Source : DGFiP, tableau statistique « Impôt sur le revenu : répartition de l'impôt moyen par
déciles de RFR par part » (.xls, impots.gouv.fr, ``dgfip_ir_deciles_rfr_part_xlsx`` dans
registres/datasets.yaml), un onglet par année de revenus (a2003 à a2024). Valeurs reprises
telles que publiées ; seule l'unité est harmonisée en euros (l'en-tête de chaque onglet la
donne : montants en euros ou en milliers d'euros, nombres en milliers ou en millions).

Sorties :

- data/processed/impot_revenu/deciles_rfr_part.csv : annee, decile, borne_inferieure,
  borne_superieure (euros de RFR par part ; vide pour les bornes non publiées), impot_moyen
  (euros par foyer, impôt net ; vide en 2024, publié par part), nombre_foyers (ensemble) ;
- data/processed/impot_revenu/deciles_rfr_part_2024.csv : onglet a2024, plus détaillé : nombre
  de parts moyen, RFR moyen par part et impôt au barème moyen par part, pour les dix dixièmes,
  le dernier centième et le dernier millième.

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/impot_revenu/extraire_deciles_dgfip.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
SOURCE = RACINE / "data" / "raw" / "impot_revenu" / "dgfip_ir_deciles_rfr_part.xlsx"
SORTIE = RACINE / "data" / "processed" / "impot_revenu" / "deciles_rfr_part.csv"
SORTIE_2024 = RACINE / "data" / "processed" / "impot_revenu" / "deciles_rfr_part_2024.csv"
DECILES = 10
MILLIER = 1000.0
MILLION = 1e6
HAUT = {"dont dernier centième": "centieme", "dont dernier millième": "millieme"}


def _nombre(v: object) -> float | None:
    return float(v) if isinstance(v, (int, float)) else None


def _unites(lignes: list[list[object]]) -> tuple[float, float]:
    """Facteurs vers l'euro (montants) et vers l'unité (nombres), lus dans l'en-tête."""
    entete = " ".join(str(c) for c in lignes[0]).lower()
    montant = 1.0 if "montants en euros" in entete else MILLIER
    nombre = MILLIER if "nombres en milliers" in entete else MILLION
    return montant, nombre


def _foyers(lignes: list[list[object]], facteur: float) -> float:
    ligne = next(lg for lg in lignes if str(lg[0]).startswith("Nombre de foyers"))
    valeur = _nombre(ligne[1])
    if valeur is None:
        msg = "nombre de foyers introuvable"
        raise ValueError(msg)
    # L'onglet a2021 donne un nombre entier de foyers malgré un en-tête « en milliers ».
    return valeur if valeur > MILLION else valeur * facteur


def extraire() -> tuple[list[list[object]], list[list[object]]]:
    classeur = CalamineWorkbook.from_path(str(SOURCE))
    lignes_csv: list[list[object]] = []
    detail: list[list[object]] = []
    for onglet in classeur.sheet_names:
        annee = int(onglet[1:])
        lignes = classeur.get_sheet_by_name(onglet).to_python()
        montant, nombre = _unites(lignes)
        foyers = _foyers(lignes, nombre)
        trouves = 0
        for ligne in lignes:
            if _nombre(ligne[0]) is None or not 1 <= float(ligne[0]) <= DECILES:
                continue
            bas, haut = _nombre(ligne[1]), _nombre(ligne[2])
            impot = None if annee == 2024 else _nombre(ligne[3])  # noqa: PLR2004
            lignes_csv.append(
                [
                    annee,
                    int(float(ligne[0])),
                    "" if bas is None else round(bas * montant, 2),
                    "" if haut is None else round(haut * montant, 2),
                    "" if impot is None else round(impot * montant, 2),
                    round(foyers),
                ]
            )
            trouves += 1
            if annee == 2024:  # noqa: PLR2004
                detail.append(_detail(str(int(float(ligne[0]))), ligne, montant))
        if trouves != DECILES:
            msg = f"onglet {onglet} : {trouves} déciles au lieu de {DECILES}"
            raise ValueError(msg)
        if annee == 2024:  # noqa: PLR2004
            for ligne in lignes:
                if str(ligne[0]) in HAUT:
                    detail.append(_detail(HAUT[str(ligne[0])], ligne, montant))
    return lignes_csv, detail


def _detail(segment: str, ligne: list[object], montant: float) -> list[object]:
    bas = _nombre(ligne[1])
    return [
        segment,
        "" if bas is None else round(bas * montant, 2),
        ligne[3],
        round(float(ligne[4]) * montant, 2),  # type: ignore[arg-type]
        round(float(ligne[5]) * montant, 2),  # type: ignore[arg-type]
    ]


def main() -> None:
    lignes, detail = extraire()
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "annee",
                "decile",
                "borne_inferieure",
                "borne_superieure",
                "impot_moyen",
                "nombre_foyers",
            ]
        )
        w.writerows(lignes)
    with SORTIE_2024.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "segment",
                "borne_inferieure",
                "parts_moyen",
                "rfr_part_moyen",
                "impot_bareme_part_moyen",
            ]
        )
        w.writerows(detail)
    print(f"{SORTIE.relative_to(RACINE)} : {len(lignes)} lignes ; 2024 : {len(detail)} segments")


if __name__ == "__main__":
    main()
