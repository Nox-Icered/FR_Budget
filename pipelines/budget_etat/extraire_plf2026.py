"""Extrait du projet de loi de finances pour 2026 les flux du budget de l'État (diagramme).

Sources, dans data/raw/ (voir registres/datasets.yaml) :

- projet de loi de finances pour 2026, n° 1906 (``plf2026_projet_loi_pdf``) : équilibre général
  du budget (article 48, en millions d'euros) et état B, crédits de paiement par mission du
  budget général (en euros) ;
- annexe « Évaluation des voies et moyens », tome I (``plf2026_voies_et_moyens_tome1_pdf``) :
  recettes fiscales nettes par impôt (milliards d'euros, au dixième) et prélèvements sur
  recettes au profit des collectivités territoriales et de l'Union européenne (milliers d'euros).

Valeurs reprises telles que publiées. Seul calcul : la mission « Remboursements et
dégrèvements » est réduite à son programme « impôts locaux » (201), car les recettes fiscales
et les dépenses de l'article 48 sont déjà nettes des remboursements et dégrèvements d'impôts
d'État (programme 200). Contrôles : la somme des missions redonne les dépenses nettes de
l'article 48, les deux prélèvements leur total, les impôts les recettes fiscales nettes (au
million ou au dixième de milliard près).

Sorties dans data/processed/budget_etat/ : equilibre_2026.csv, missions_2026.csv,
recettes_2026.csv.

Usage (depuis la racine du dépôt) :
    uv run --directory moteur python ../pipelines/budget_etat/extraire_plf2026.py
"""

from __future__ import annotations

import csv
import re
import subprocess
from pathlib import Path

RACINE = Path(__file__).parents[2]
PLF = RACINE / "data" / "raw" / "budget_etat" / "plf2026_projet_loi_1906.pdf"
VM1 = RACINE / "data" / "raw" / "tva" / "plf2026_voies_et_moyens_tome1.pdf"
SORTIE = RACINE / "data" / "processed" / "budget_etat"
MISSION_RD = "Remboursements et dégrèvements"
PROGRAMME_RD_ETAT = "Remboursements et dégrèvements d'impôts d'État (crédits évaluatifs)"
MILLIONS = 1e6
COLONNES_SYNTHESE = 6
"""Tableau de synthèse des recettes du tome I : 2024, LFI 2025, révisé 2025, écart, PLF 2026,
écart."""
COLONNES_PRELEVEMENTS = 4
"""Tableaux des prélèvements : 2024, LFI 2025, révisé 2025, PLF 2026."""
# Nombres en groupes de trois chiffres séparés par une espace simple ; colonnes séparées par
# au moins deux espaces.
NOMBRE = r"[-+]?\d{1,3}(?: \d{3})*(?:,\d+)?"
DEUX_NOMBRES = re.compile(rf"^(.*?\S)\s{{2,}}({NOMBRE})\s{{2,}}({NOMBRE})\s*$")
EQUILIBRE = {
    "recettes_fiscales_nettes": "Recettes fiscales** / dépenses***",
    "recettes_non_fiscales": "Recettes non fiscales",
    "prelevements_sur_recettes": "À déduire : Prélèvements sur recettes au profit des",
    "solde_general": "Solde général",
}
IMPOTS = {
    "impot_revenu": "Impôt net sur le revenu",
    "impot_societes": "Impôt net sur les sociétés",
    "accises_energies": "Accises sur les énergies nettes",
    "tva": "Taxe sur la valeur ajoutée nette",
    "autres_impots": "Autres recettes fiscales nettes",
    "recettes_non_fiscales": "Recettes non fiscales",
}
PRELEVEMENTS = {
    "collectivites": (
        "Prélèvements sur les recettes de l'État au profit des collectivités territoriales"
    ),
    "union_europeenne": "Prélèvement sur les recettes de l'État au profit de l'Union européenne",
}


def _texte(pdf: Path) -> list[str]:
    sortie = subprocess.run(
        ["pdftotext", "-layout", str(pdf), "-"], check=True, capture_output=True, text=True
    )
    return sortie.stdout.splitlines()


def _nombre(texte: str) -> float:
    return float(texte.replace(" ", "").replace(",", "."))


def _nombres(ligne: str) -> list[float]:
    return [_nombre(n) for n in re.findall(rf"(?<!\S){NOMBRE}(?!\S)", ligne)]


def equilibre(lignes: list[str]) -> dict[str, float]:
    """Article 48, en millions d'euros : recettes, prélèvements, dépenses nettes, soldes."""
    debut = next(i for i, lg in enumerate(lignes) if "Équilibre général du budget" in lg)
    resultat: dict[str, float] = {}
    for cle, libelle in EQUILIBRE.items():
        ligne = next(lg for lg in lignes[debut:] if lg.strip().startswith(libelle))
        resultat[cle] = _nombres(ligne)[0] if cle != "solde_general" else _nombres(ligne)[-1]
    ligne = next(
        lg for lg in lignes[debut:] if lg.strip().startswith("Montants nets pour le budget")
    )
    valeurs = _nombres(ligne)
    resultat["depenses_nettes"] = valeurs[3]
    resultat["solde_budget_general"] = valeurs[-1]
    return resultat


def missions(lignes: list[str]) -> list[tuple[str, float]]:
    """État B : crédits de paiement par mission (euros). Une ligne est une mission quand ses
    crédits égalent la somme des lignes de programme qui la suivent."""
    debut = next(i for i, lg in enumerate(lignes) if lg.startswith("Etat B - Répartition"))
    fin = next(i for i, lg in enumerate(lignes) if lg.startswith("Etat C - Répartition"))
    rangs: list[tuple[str, float]] = []
    for ligne in lignes[debut:fin]:
        m = DEUX_NOMBRES.match(ligne)
        if m and not m.group(1).strip().startswith("dont titre"):
            rangs.append((m.group(1).strip(), _nombre(m.group(3))))
    total = next(cp for libelle, cp in rangs if libelle == "Total")
    rangs = [r for r in rangs if r[0] != "Total"]
    resultat: list[tuple[str, float]] = []
    i = 0
    while i < len(rangs):
        libelle, cp = rangs[i]
        j, somme = i + 1, 0.0
        while j < len(rangs) and abs(somme - cp) > 1:
            somme += rangs[j][1]
            j += 1
        if abs(somme - cp) > 1:
            msg = f"état B : programmes de la mission « {libelle} » introuvables"
            raise ValueError(msg)
        if libelle == MISSION_RD:
            rd_etat = next(c for lib, c in rangs[i + 1 : j] if lib == PROGRAMME_RD_ETAT)
            cp -= rd_etat
        resultat.append((libelle, cp))
        i = j
    if abs(sum(c for _, c in resultat) + rd_etat - total) > len(resultat):
        msg = "état B : la somme des missions ne redonne pas le total"
        raise ValueError(msg)
    # Lignes sans crédits (programmes à zéro placés après une mission déjà complète, ou
    # missions sans crédits en 2026) : sans effet sur le diagramme, écartées.
    return [(libelle, cp) for libelle, cp in resultat if cp != 0]


def recettes(lignes: list[str]) -> dict[str, float]:
    """Voies et moyens, tome I : recettes 2026 par impôt (Md€) et prélèvements (k€)."""
    resultat: dict[str, float] = {}
    for cle, libelle in IMPOTS.items():
        # Ligne du tableau de synthèse (six colonnes), pas celle du sommaire.
        ligne = next(
            lg
            for lg in lignes
            if lg.strip().startswith(libelle) and len(_nombres(lg)) == COLONNES_SYNTHESE
        )
        resultat[cle] = _nombres(ligne)[4] * 1000  # colonne PLF 2026, en M€
    for cle, libelle in PRELEVEMENTS.items():
        # Ligne du tableau (quatre colonnes de montants), pas celle du sommaire.
        ligne = next(
            lg
            for lg in lignes
            if lg.strip().startswith(libelle) and len(_nombres(lg)) == COLONNES_PRELEVEMENTS
        )
        resultat[f"prelevement_{cle}"] = _nombres(ligne)[-1] / 1000  # k€ → M€
    return resultat


def main() -> None:
    plf = _texte(PLF)
    eq = equilibre(plf)
    ms = missions(plf)
    rc = recettes(_texte(VM1))
    somme_missions = sum(c for _, c in ms) / MILLIONS
    controles = {
        "missions = dépenses nettes": (somme_missions, eq["depenses_nettes"], 1.0),
        "prélèvements = total": (
            rc["prelevement_collectivites"] + rc["prelevement_union_europeenne"],
            eq["prelevements_sur_recettes"],
            1.0,
        ),
        "impôts = recettes fiscales nettes": (
            sum(rc[k] for k in IMPOTS if k != "recettes_non_fiscales"),
            eq["recettes_fiscales_nettes"],
            100.0,
        ),
    }
    for nom, (a, b, tolerance) in controles.items():
        if abs(a - b) > tolerance:
            msg = f"contrôle « {nom} » : {a} contre {b}"
            raise ValueError(msg)
    SORTIE.mkdir(parents=True, exist_ok=True)
    with (SORTIE / "equilibre_2026.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ligne", "montant_meur"])
        w.writerows(eq.items())
    with (SORTIE / "missions_2026.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["mission", "credits_paiement_meur"])
        w.writerows((m, round(c / MILLIONS, 3)) for m, c in ms)
    with (SORTIE / "recettes_2026.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["poste", "montant_meur"])
        w.writerows(rc.items())
    print(f"{len(ms)} missions ; somme {somme_missions:.0f} M€ ; équilibre {eq}")


if __name__ == "__main__":
    main()
