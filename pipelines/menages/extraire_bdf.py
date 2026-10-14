"""Extrait les dépenses par poste de l'enquête Budget de famille 2017 (lot « dépense des ménages »).

Sources (registres/datasets.yaml) :

- INSEE, Budget de famille 2017, tableaux TF105 (type de ménage) et TF106 (décile de niveau de
  vie), dans data/raw/menages/insee_bdf2017/ ; libellés dans ``metadonnees_bdf2017.csv`` ;
- INSEE, comptes nationaux annuels base 2020, consommation des ménages par produit
  (``T_CONSO_EFF_PRODUITS_MENAGES.xlsx``, déjà au dépôt pour le levier TVA) : dépense de
  consommation individuelle des ménages (P31, euros courants) et consommation de produits de la
  cokéfaction et du raffinage (17_C2) en volume (euros chaînés de 2020).

Transformation :

- postes les plus fins publiés (aucun poste plus détaillé ne commence par le même code), hors
  postes 13 (impôts, remboursements de prêts, gros travaux, transferts), qui ne sont pas de la
  consommation ; le script vérifie que leur somme redonne le total publié (``CTOTALE``) à
  l'arrondi près, pour chaque classe ;
- comptes nationaux : lignes P31 (ménages) et 17_C2, toutes les années.

Sorties :

- data/processed/menages/bdf2017_depenses.csv (nomenclature, classe, poste, libelle, euros) ;
- data/processed/menages/consommation_nationale.csv (annee, p31_millions_courants,
  carburants_volume_millions_2020).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/menages/extraire_bdf.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from python_calamine import CalamineWorkbook

RACINE = Path(__file__).parents[2]
BRUT = RACINE / "data" / "raw" / "menages" / "insee_bdf2017"
COMPTES = RACINE / "data" / "raw" / "tva" / "insee" / "T_CONSO_EFF_PRODUITS_MENAGES.xlsx"
SORTIES = RACINE / "data" / "processed" / "menages"
TABLEAUX = {"type_menage": ("tf105.csv", "TYPMEN"), "decile": ("tf106.csv", "DECUC")}
TOTAL = "CTOTALE"
HORS_CONSOMMATION = "13"
TOLERANCE_ARRONDI = 0.5
"""Écart admis, en euros par poste, entre la somme des postes et le total publié (arrondis)."""
LIGNE_P31 = "Dépense de consommation individuelle des ménages"
LIGNE_CARBURANTS = "17_C2"


def libelles() -> dict[str, str]:
    resultat = {}
    with (BRUT / "metadonnees_bdf2017.csv").open(encoding="utf-8") as f:
        for ligne in csv.reader(f, delimiter=";"):
            if ligne and ligne[0] == "NOMENCLATURE":
                code, _, libelle = ligne[3].partition(" - ")
                resultat[code.strip()] = libelle.strip()
    return resultat


def postes(codes: list[str]) -> list[str]:
    """Postes les plus fins, hors postes 13 et hors total."""
    return [
        c
        for c in codes
        if c != TOTAL
        and not c.startswith(HORS_CONSOMMATION)
        and not any(autre != c and autre.startswith(c) for autre in codes)
    ]


def depenses() -> list[dict[str, object]]:
    noms = libelles()
    lignes: list[dict[str, object]] = []
    for nomenclature, (fichier, colonne) in TABLEAUX.items():
        with (BRUT / fichier).open(encoding="utf-8") as f:
            brut = list(csv.DictReader(f, delimiter=";"))
        classes = dict.fromkeys(r[colonne] for r in brut)
        for classe in classes:
            valeurs = {r["NOMENCLATURE"]: float(r["CONSO"]) for r in brut if r[colonne] == classe}
            retenus = postes(list(valeurs))
            ecart = abs(sum(valeurs[p] for p in retenus) - valeurs[TOTAL])
            if ecart > TOLERANCE_ARRONDI * len(retenus):
                msg = f"{fichier}, classe {classe} : écart de {ecart} € au total publié"
                raise ValueError(msg)
            lignes.extend(
                {
                    "nomenclature": nomenclature,
                    "classe": classe,
                    "poste": p,
                    "libelle": noms[p],
                    "euros": valeurs[p],
                }
                for p in retenus
            )
    return lignes


def consommation_nationale() -> list[dict[str, object]]:
    classeur = CalamineWorkbook.from_path(str(COMPTES))

    def ligne(feuille: str, test: str) -> dict[int, float]:
        lignes = classeur.get_sheet_by_name(feuille).to_python()
        entete = next(r for r in lignes if "2017" in [str(c) for c in r])
        annees = {i: int(c) for i, c in enumerate(entete) if str(c).isdigit()}
        trouvee = [r for r in lignes if test in (str(r[0]), str(r[1]).strip())]
        valeurs = trouvee[-1]
        return {a: float(valeurs[i]) for i, a in annees.items() if valeurs[i] not in ("", None)}

    p31 = ligne("MEURcour", LIGNE_P31)
    volume = ligne("MEUR2020", LIGNE_CARBURANTS)
    return [
        {
            "annee": a,
            "p31_millions_courants": p31[a],
            "carburants_volume_millions_2020": volume[a],
        }
        for a in sorted(set(p31) & set(volume))
    ]


def ecrire(chemin: Path, lignes: list[dict[str, object]]) -> None:
    with chemin.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def main() -> None:
    SORTIES.mkdir(parents=True, exist_ok=True)
    ecrire(SORTIES / "bdf2017_depenses.csv", depenses())
    ecrire(SORTIES / "consommation_nationale.csv", consommation_nationale())


if __name__ == "__main__":
    main()
