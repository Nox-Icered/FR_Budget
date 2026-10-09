"""Extrait les fiches des dépenses fiscales des tomes II de Voies et moyens (lot 2.4).

Sources (voir registres/datasets.yaml) : annexe « Évaluation des voies et moyens », tome II,
des PLF 2024, 2025 et 2026. Chaque fiche donne le numéro, le libellé, le coût réalisé l'année
N-2 et prévu les années N-1 et N (PLF de l'année N), en M€, et la fiabilité du réalisé.

Le texte est obtenu par ``pdftotext -layout`` (poppler-utils). Les montants sont repris tels
que publiés : « nc » (non chiffré), « ε » (inférieur à 0,5 M€) et « - » sont gardés en texte ;
les espaces des milliers sont retirés. L'impôt est la partie de la « Liste des dépenses
fiscales » où figure la fiche (titres du sommaire).

Contrôle : les tests ``moteur/tests/unitaires/test_depenses_fiscales.py`` vérifient que les
fiches, avec la convention du tome II pour les dépenses non chiffrées, redonnent le total
publié de chaque tome et le nombre de dépenses annoncé.

Sortie : data/processed/niches_fiscales/depenses_fiscales.csv (plf, code, impot, libelle,
annee, statut, cout_meur, fiabilite).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/niches_fiscales/extraire_tome2.py
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

RACINE = Path(__file__).parents[2]
SOURCES = {
    2024: RACINE / "data" / "raw" / "niches_fiscales" / "plf2024_voies_et_moyens_tome2.pdf",
    2025: RACINE / "data" / "raw" / "tva" / "plf2025_voies_et_moyens_tome2.pdf",
    2026: RACINE / "data" / "raw" / "niches_fiscales" / "plf2026_voies_et_moyens_tome2.pdf",
}
SORTIE = RACINE / "data" / "processed" / "niches_fiscales" / "depenses_fiscales.csv"
# Parties de la « Liste des dépenses fiscales » (sommaire des trois tomes) et identifiant.
IMPOTS = {
    "Impôt sur le revenu": "impot_revenu",
    "Impôt sur le revenu et impôt sur les sociétés": "impot_revenu_et_societes",
    "Impôt sur les sociétés": "impot_societes",
    "Autres impôts directs": "autres_impots_directs",
    "Droits d'enregistrement et de timbre": "enregistrement_timbre",
    "Taxe sur la valeur ajoutée": "tva",
    "Accise sur les énergies": "accise_energies",
    "Autres droits": "autres_droits",
    "Impôts locaux": "impots_locaux",
}
TIRET_DEMI_CADRATIN = chr(0x2013)
EN_TETE_FICHE = re.compile(rf"^\s+(\d{{6}}) {TIRET_DEMI_CADRATIN} (.*)$")
ANNEES = re.compile(r"^\s*(20\d\d)\s+(20\d\d)\s+(20\d\d)\b")
COLONNES = re.compile(r"\s{2,}")
MONTANT = re.compile(r"^-?\d{1,3}( \d{3})*$")
TEXTES = {"nc", "ε", "-"}
FIABILITE = "Fiabilité du réalisé"


def texte_pdf(chemin: Path) -> list[str]:
    sortie = subprocess.run(
        ["pdftotext", "-layout", str(chemin), "-"], check=True, capture_output=True, text=True
    )
    return sortie.stdout.splitlines()


def montant(cellule: str) -> tuple[str, float | None]:
    """Statut (« chiffre », « nc », « ε », « - ») et valeur en M€ d'une cellule."""
    cellule = cellule.strip()
    if MONTANT.match(cellule):
        return "chiffre", float(cellule.replace(" ", ""))
    if cellule in TEXTES:
        return cellule, None
    msg = f"montant illisible : {cellule!r}"
    raise ValueError(msg)


def _fin_libelle(lignes: list[str], i: int) -> tuple[str, int]:
    """Libellé d'une fiche : ligne d'en-tête et lignes de suite indentées."""
    parties = [EN_TETE_FICHE.match(lignes[i]).group(2).strip()]  # type: ignore[union-attr]
    j = i + 1
    while j < len(lignes) and lignes[j].startswith(" " * 10) and lignes[j].strip():
        if ANNEES.match(lignes[j]) or "Impact budgétaire" in lignes[j]:
            break
        parties.append(lignes[j].strip())
        j += 1
    return " ".join(parties), j


def extraire(plf: int, lignes: list[str]) -> list[dict[str, object]]:
    debut = next(i for i, ligne in enumerate(lignes) if ligne == "Impôt sur le revenu")
    impot = None
    fiches = []
    i = debut
    while i < len(lignes):
        ligne = lignes[i]
        if ligne in IMPOTS:
            impot = IMPOTS[ligne]
        if ligne == "Annexes":
            break
        entete = EN_TETE_FICHE.match(ligne)
        if not entete:
            i += 1
            continue
        code = entete.group(1)
        libelle, j = _fin_libelle(lignes, i)
        k = next(k for k in range(j, j + 15) if ANNEES.match(lignes[k]))
        annees = [int(a) for a in ANNEES.match(lignes[k]).groups()]  # type: ignore[union-attr]
        if annees != [plf - 2, plf - 1, plf]:
            msg = f"PLF {plf}, fiche {code} : années inattendues {annees}"
            raise ValueError(msg)
        v = next(k2 for k2 in range(k + 1, k + 5) if lignes[k2].strip())
        cellules = COLONNES.split(lignes[v].strip())[:3]
        fiabilite = next(
            (
                lignes[f][len(FIABILITE) :].strip()
                for f in range(v, v + 12)
                if lignes[f].startswith(FIABILITE)
            ),
            "",
        )
        for annee, cellule in zip(annees, cellules, strict=True):
            statut, valeur = montant(cellule)
            fiches.append(
                {
                    "plf": plf,
                    "code": code,
                    "impot": impot,
                    "libelle": libelle,
                    "annee": annee,
                    "statut": statut,
                    "cout_meur": "" if valeur is None else valeur,
                    "fiabilite": fiabilite,
                }
            )
        i = v + 1
    return fiches


def main() -> None:
    resultat = []
    for plf, chemin in SOURCES.items():
        fiches = extraire(plf, texte_pdf(chemin))
        codes = {f["code"] for f in fiches}
        print(f"PLF {plf} : {len(codes)} fiches")
        for annee in (plf - 2, plf - 1, plf):
            total = sum(
                float(f["cout_meur"])  # type: ignore[arg-type]
                for f in fiches
                if f["annee"] == annee and f["statut"] == "chiffre"
            )
            print(f"  {annee} : {total:,.0f} M€ (montants chiffrés, sans reprise des « nc »)")
        resultat += fiches
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(resultat[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(resultat)


if __name__ == "__main__":
    main()
