"""Extrait les prélèvements sur recettes au profit des collectivités (tome I de Voies et moyens).

Lot 2.6. Sources (voir registres/datasets.yaml) : annexe « Évaluation des voies et moyens »,
tome I, des PLF 2024, 2025 et 2026, tableau « Prélèvements sur les recettes de l'État au profit
des collectivités territoriales » (en milliers d'euros). Le PLF de l'année N donne quatre
colonnes : exécution N-2, évaluation initiale pour N-1 (LFI), évaluation révisée pour N-1,
évaluation proposée pour N.

Le texte est obtenu par ``pdftotext -layout``. Certaines cellules sont vides : chaque montant
est rattaché à la colonne dont il est le plus proche (fin du nombre). Les colonnes de chaque page
sont repérées par l'en-tête du tableau, calé sur la ligne 3101 (dotation globale de
fonctionnement), qui a ses quatre montants. Montants repris
sans arrondi, en milliers d'euros ; signe moins conservé.

La ligne de total du tableau est reprise avec le code « total » ; les tests vérifient que la
somme des lignes la redonne.

Sortie : data/processed/dotations_collectivites/psr_collectivites.csv (plf, code, libelle,
colonne, annee, milliers_euros).

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/dotations_collectivites/extraire_psr.py
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

RACINE = Path(__file__).parents[2]
SOURCES = {
    2024: RACINE / "data" / "raw" / "dotations_collectivites" / "plf2024_voies_et_moyens_tome1.pdf",
    2025: RACINE / "data" / "raw" / "tva" / "plf2025_voies_et_moyens_tome1.pdf",
    2026: RACINE / "data" / "raw" / "tva" / "plf2026_voies_et_moyens_tome1.pdf",
}
SORTIE = RACINE / "data" / "processed" / "dotations_collectivites" / "psr_collectivites.csv"
TIRET_DEMI_CADRATIN = chr(0x2013)
LIGNE = re.compile(rf"^\s*(31\d\d) {TIRET_DEMI_CADRATIN} (.*)$")
MONTANT = re.compile(r"-?\d{1,3}(?: \d{3})*(?=\s|$)")
COLONNES = ("execution", "lfi", "revise", "plf")
CODE_REFERENCE = "3101"
ECART_LIBELLE = 4
# Ligne de total du tableau, reprise pour contrôle (code « total »).
TITRE_TOTAL = "Prélèvements sur les recettes de l'État au profit des collectivités territoriales"
CODE_TOTAL = "total"
EN_TETE = re.compile(r"^\s+pour \d{4}\s+pour \d{4}\s+pour \d{4}\s*$")


def pages_pdf(chemin: Path) -> list[list[str]]:
    """Lignes de chaque page (``pdftotext`` sépare les pages par un saut de page)."""
    sortie = subprocess.run(
        ["pdftotext", "-layout", str(chemin), "-"], check=True, capture_output=True, text=True
    )
    return [page.split("\n") for page in sortie.stdout.split("\f")]


def _montants(reste: str, debut: int) -> list[tuple[int, float]]:
    """(position de fin, montant) des nombres d'une ligne, après le libellé.

    Les montants sont séparés du libellé et entre eux par au moins deux espaces.
    """
    resultat = []
    for bloc in re.finditer(r"(?:(?<=\s\s)|^)(-?\d{1,3}(?: \d{3})*)(?=\s\s|\s*$)", reste):
        resultat.append((debut + bloc.end(1), float(bloc.group(1).replace(" ", ""))))
    return resultat


def _entete(ligne: str) -> list[int] | None:
    """Fins des trois « pour AAAA » d'une ligne d'en-tête ; ``None`` pour une autre ligne."""
    if not EN_TETE.match(ligne):
        return None
    return [m.end() for m in re.finditer(r"pour \d{4}", ligne)]


def extraire(plf: int, pages: list[list[str]]) -> list[dict[str, object]]:
    """Montants de chaque ligne 31xx, rattachés aux colonnes de la page.

    Sur chaque page, les colonnes sont repérées par l'en-tête « pour AAAA » (trois dernières
    colonnes) ; l'écart entre ces repères et les fins de nombres est mesuré sur la ligne 3101,
    qui a ses quatre montants, puis appliqué aux autres pages.
    """
    reperes: list[list[int] | None] = []
    for page in pages:
        reperes.append(next((e for e in map(_entete, page) if e is not None), None))
    # Calage sur la ligne 3101 : quatre montants, colonnes de sa page.
    calage = None
    for page, repere in zip(pages, reperes, strict=True):
        for ligne in page:
            m = LIGNE.match(ligne)
            if m and m.group(1) == CODE_REFERENCE and repere is not None:
                fins = [p for p, _ in _montants(ligne, 0)][-len(COLONNES) :]
                if len(fins) == len(COLONNES):
                    # Première colonne : même écart à la deuxième que sur la ligne 3101.
                    ecarts = [f - r for f, r in zip(fins[1:], repere, strict=True)]
                    calage = (fins[1] - fins[0], ecarts)
                    break
        if calage:
            break
    if calage is None:
        msg = f"PLF {plf} : ligne {CODE_REFERENCE} ou en-tête introuvable"
        raise ValueError(msg)
    largeur, decalages = calage
    annees = (plf - 2, plf - 1, plf - 1, plf)
    resultat: list[dict[str, object]] = []
    vus: set[str] = set()
    for page, repere in zip(pages, reperes, strict=True):
        if repere is None:
            continue
        fins = [r + d for r, d in zip(repere, decalages, strict=True)]
        fins = [fins[0] - largeur, *fins]
        for i, ligne in enumerate(page):
            m = LIGNE.match(ligne)
            if ligne.startswith(TITRE_TOTAL) and CODE_TOTAL not in vus:
                vus.add(CODE_TOTAL)
                for fin, valeur in _montants(ligne[len(TITRE_TOTAL) :], len(TITRE_TOTAL)):
                    j = min(range(len(fins)), key=lambda k: abs(fins[k] - fin))
                    resultat.append(
                        {
                            "plf": plf,
                            "code": CODE_TOTAL,
                            "libelle": TITRE_TOTAL,
                            "colonne": COLONNES[j],
                            "annee": annees[j],
                            "milliers_euros": valeur,
                        }
                    )
                continue
            if m is None or m.group(1) in vus:
                continue
            code = m.group(1)
            vus.add(code)
            debut_libelle = ligne.index(TIRET_DEMI_CADRATIN) + 2
            coupe = re.search(r"\s{2,}-?\d", ligne[debut_libelle:])
            fin_libelle = debut_libelle + (coupe.start() if coupe else len(ligne) - debut_libelle)
            libelle = ligne[debut_libelle:fin_libelle].strip()
            suite = page[i + 1] if i + 1 < len(page) else ""
            if suite.startswith(" ") and suite.strip() and not LIGNE.match(suite):
                libelle += " " + suite.strip()
            for fin, valeur in _montants(ligne[fin_libelle:], fin_libelle):
                j = min(range(len(fins)), key=lambda k: abs(fins[k] - fin))
                if abs(fins[j] - fin) > ECART_LIBELLE:
                    msg = f"PLF {plf}, ligne {code} : montant hors colonne ({valeur} à {fin})"
                    raise ValueError(msg)
                resultat.append(
                    {
                        "plf": plf,
                        "code": code,
                        "libelle": libelle,
                        "colonne": COLONNES[j],
                        "annee": annees[j],
                        "milliers_euros": valeur,
                    }
                )
    return resultat


def main() -> None:
    lignes = [
        ligne for plf, chemin in SOURCES.items() for ligne in extraire(plf, pages_pdf(chemin))
    ]
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    with SORTIE.open("w", encoding="utf-8", newline="") as f:
        ecrivain = csv.DictWriter(f, fieldnames=list(lignes[0]), lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


if __name__ == "__main__":
    main()
