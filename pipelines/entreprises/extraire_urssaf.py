"""Met en table la masse salariale et les allègements généraux du secteur privé, par tranche de
taille d'entreprise et par grand secteur (module « entreprises »).

Sources (voir registres/datasets.yaml) : exports CSV des jeux open data de l'Urssaf (licence
ODbL), conservés tels que téléchargés dans data/raw/entreprises/urssaf/ :

- exos-secteur-prive-tranche-ent.csv : exonérations par tranche de taille et catégorie ;
- nombre-etab-effectifs-salaries-et-masse-salariale-secteur-prive-tranche-ent.csv : entreprises,
  effectifs salariés moyens et masse salariale annuels par tranche de taille ;
- exos-secteur-na38i-grandes-categories.csv : exonérations par secteur et catégorie ;
- effectifs-salaries-et-masse-salariale-du-secteur-prive-france-entiere-x-na88.csv : effectifs
  et masse salariale trimestriels par secteur.

Allègements généraux retenus : catégories 11 (réduction générale), 15 (réduction des
cotisations famille) et 16 (réduction des cotisations maladie), le périmètre du levier
« allègements généraux » (fr_budget.agrege.cotisations). Grands secteurs : code GS1 à GS7 (le
libellé diffère d'un jeu à l'autre pour l'intérim) ; libellé du jeu de la masse salariale.

Sorties (base dérivée, sous licence ODbL comme les jeux d'origine) :

- data/processed/entreprises/taille.csv (annee, tranche, entreprises, effectifs,
  masse_salariale, allegements) ;
- data/processed/entreprises/secteur.csv (annee, code, secteur, effectifs, masse_salariale,
  allegements) : effectifs moyens des quatre trimestres, masse salariale annuelle ;
- data/processed/entreprises/masse_salariale_annuelle.csv (annee, masse_salariale) : total
  annuel (somme des tranches, ou des quatre trimestres par secteur pour une année absente du
  jeu par tranche).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/entreprises/extraire_urssaf.py
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).parents[2]
BRUT = RACINE / "data" / "raw" / "entreprises" / "urssaf"
SORTIE = RACINE / "data" / "processed" / "entreprises"
ANNEE = "2024"
"""Dernière année commune aux quatre jeux (la masse salariale par tranche s'arrête en 2024)."""
CATEGORIES_ALLEGEMENTS = {"11", "15", "16"}
TRIMESTRES = 4


def _lire(nom: str) -> list[dict[str, str]]:
    with (BRUT / nom).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _ecrire(nom: str, colonnes: list[str], lignes: list[dict[str, object]]) -> None:
    SORTIE.mkdir(parents=True, exist_ok=True)
    with (SORTIE / nom).open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=colonnes, lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)
    print(f"{nom} : {len(lignes)} lignes")


def taille() -> None:
    masse = _lire("nombre-etab-effectifs-salaries-et-masse-salariale-secteur-prive-tranche-ent.csv")
    exos = _lire("exos-secteur-prive-tranche-ent.csv")
    allegements: dict[str, float] = defaultdict(float)
    for r in exos:
        if r["annee"] == ANNEE and r["code_categorie_de_mesures"] in CATEGORIES_ALLEGEMENTS:
            allegements[r["tranche_d_effectif"]] += float(r["montant_des_exonerations"])
    lignes = [
        {
            "annee": ANNEE,
            "tranche": r["tranche_d_effectif"],
            "entreprises": int(r["nombre_d_entreprises"]),
            "effectifs": int(r["effectifs_salaries_moyens"]),
            "masse_salariale": float(r["masse_salariale"]),
            "allegements": allegements[r["tranche_d_effectif"]],
        }
        for r in sorted(masse, key=lambda r: r["tranche_d_effectif"])
        if r["annee"] == ANNEE
    ]
    if set(allegements) != {str(ligne["tranche"]) for ligne in lignes}:
        msg = "tranches différentes entre exonérations et masse salariale"
        raise ValueError(msg)
    colonnes = ["annee", "tranche", "entreprises", "effectifs", "masse_salariale", "allegements"]
    _ecrire("taille.csv", colonnes, lignes)


def _code(grand_secteur: str) -> str:
    return grand_secteur.split(" ", 1)[0]


def secteur() -> None:
    trimestriel = _lire(
        "effectifs-salaries-et-masse-salariale-du-secteur-prive-france-entiere-x-na88.csv"
    )
    exos = _lire("exos-secteur-na38i-grandes-categories.csv")
    libelles: dict[str, str] = {}
    masse: dict[str, float] = defaultdict(float)
    effectifs: dict[str, float] = defaultdict(float)
    trimestres: dict[str, set[str]] = defaultdict(set)
    for r in trimestriel:
        if r["annee"] != ANNEE:
            continue
        code = _code(r["grand_secteur_d_activite"])
        libelles[code] = r["grand_secteur_d_activite"].split(" ", 1)[1]
        masse[code] += float(r["masse_salariale_brut"])
        effectifs[code] += float(r["effectifs_salaries_brut"]) / TRIMESTRES
        trimestres[code].add(r["trimestre"])
    if any(len(t) != TRIMESTRES for t in trimestres.values()):
        msg = f"{ANNEE} : année incomplète dans le jeu trimestriel"
        raise ValueError(msg)
    allegements: dict[str, float] = defaultdict(float)
    for r in exos:
        if r["annee"] == ANNEE and r["code_categorie_detail_ag"] in CATEGORIES_ALLEGEMENTS:
            allegements[_code(r["grand_secteur_d_activite"])] += float(r["montant_des_exonerations"])
    if set(allegements) - set(libelles):
        msg = "secteurs d'exonérations absents du jeu de la masse salariale"
        raise ValueError(msg)
    lignes = [
        {
            "annee": ANNEE,
            "code": code,
            "secteur": libelles[code],
            "effectifs": round(effectifs[code]),
            "masse_salariale": masse[code],
            "allegements": allegements[code],
        }
        for code in sorted(libelles)
    ]
    colonnes = ["annee", "code", "secteur", "effectifs", "masse_salariale", "allegements"]
    _ecrire("secteur.csv", colonnes, lignes)


def masse_annuelle() -> None:
    par_annee: dict[str, float] = defaultdict(float)
    for r in _lire("nombre-etab-effectifs-salaries-et-masse-salariale-secteur-prive-tranche-ent.csv"):
        par_annee[r["annee"]] += float(r["masse_salariale"])
    trimestriel: dict[str, float] = defaultdict(float)
    nombre: dict[str, set[str]] = defaultdict(set)
    for r in _lire(
        "effectifs-salaries-et-masse-salariale-du-secteur-prive-france-entiere-x-na88.csv"
    ):
        trimestriel[r["annee"]] += float(r["masse_salariale_brut"])
        nombre[r["annee"]].add(r["trimestre"])
    for annee, total in trimestriel.items():
        if annee not in par_annee and len(nombre[annee]) == TRIMESTRES:
            par_annee[annee] = total
    lignes = [{"annee": a, "masse_salariale": par_annee[a]} for a in sorted(par_annee)]
    _ecrire("masse_salariale_annuelle.csv", ["annee", "masse_salariale"], lignes)


def main() -> None:
    taille()
    secteur()
    masse_annuelle()


if __name__ == "__main__":
    main()
