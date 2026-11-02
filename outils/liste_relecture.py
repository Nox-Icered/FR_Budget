"""Liste de relecture des valeurs saisies à la main (CLAUDE.md : « Je relis moi-même chaque
modification du modèle de calcul et chaque valeur de référence saisie »).

Produit ``docs/validation/liste_relecture.md`` à partir des registres : chaque chiffrage encore
« à relire », rangé par levier, avec sa valeur, son document, sa page et le fichier téléchargé ;
puis chaque hypothèse avec sa plage. Un chiffrage est classé « entrée du calcul » quand son
identifiant apparaît dans le code du moteur hors validation, « référence de validation » quand
il n'apparaît que dans la validation, « non repéré » sinon (identifiant construit dans le code,
ou valeur de contexte).

Usage : ``python outils/liste_relecture.py`` depuis la racine du dépôt.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "docs" / "validation" / "liste_relecture.md"
CODE = RACINE / "moteur" / "src" / "fr_budget"
VALIDATION = (CODE / "validation.py", RACINE / "moteur" / "tests" / "validation")
ENTREE, REFERENCE, NON_REPERE = "entrée du calcul", "référence de validation", "non repéré"


def _lire(chemin: str, cle: str) -> list[dict]:
    return yaml.safe_load((RACINE / chemin).read_text(encoding="utf-8"))[cle]


def _textes(fichiers: list[Path]) -> str:
    return "\n".join(f.read_text(encoding="utf-8") for f in fichiers)


def _fichiers_python(*racines: Path) -> list[Path]:
    fichiers: list[Path] = []
    for r in racines:
        fichiers += [r] if r.is_file() else sorted(r.rglob("*.py"))
    return fichiers


FSTRING = re.compile(r"""\bf(["'])([a-z0-9_{}.\[\]'"]*\{[^"'\n]*?)\1""")


def _motifs_construits(texte: str) -> list[re.Pattern[str]]:
    """Identifiants construits dans le code (f-strings comme ``f"tva_point_net_2025_{taux}"``) :
    chaque partie entre accolades devient « n'importe quelle suite de caractères »."""
    motifs = []
    for m in FSTRING.finditer(texte):
        morceaux = re.split(r"\{[^}]*\}", m.group(2))
        if sum(len(x) for x in morceaux) >= 4:  # noqa: PLR2004
            motifs.append(re.compile("^" + "[a-z0-9_]+".join(map(re.escape, morceaux)) + "$"))
    return motifs


def _present(identifiant: str, texte: str, motifs: list[re.Pattern[str]]) -> bool:
    if re.search(rf"[\"']{re.escape(identifiant)}[\"']", texte):
        return True
    return any(m.match(identifiant) for m in motifs)


def _usage(identifiant: str, calcul: tuple[str, list], validation: tuple[str, list]) -> str:
    if _present(identifiant, *calcul):
        return ENTREE
    if _present(identifiant, *validation):
        return REFERENCE
    return NON_REPERE


def _nombre(v: float) -> str:
    texte = f"{v:,.4f}".rstrip("0").rstrip(".")
    return texte.replace(",", " ").replace(".", ",")


def main() -> int:
    chiffrages = _lire("registres/references/chiffrages.yaml", "chiffrages")
    hypotheses = _lire("registres/hypotheses.yaml", "hypotheses")
    sources = {s["id"]: s for s in _lire("registres/sources.yaml", "sources")}
    leviers = [lv["id"] for lv in _lire("registres/leviers.yaml", "leviers")]
    fichiers: dict[str, list[str]] = defaultdict(list)
    for d in _lire("registres/datasets.yaml", "datasets"):
        fichiers[d["source"]].append(d["fichier"])

    tous = _fichiers_python(CODE)
    exclus = {p.resolve() for p in _fichiers_python(*VALIDATION)}
    texte_calcul = _textes([f for f in tous if f.resolve() not in exclus])
    texte_validation = _textes(_fichiers_python(*VALIDATION))
    calcul = (texte_calcul, _motifs_construits(texte_calcul))
    validation = (texte_validation, _motifs_construits(texte_validation))

    a_relire = [c for c in chiffrages if c["relecture"] == "a_relire"]
    par_levier: dict[str, list[dict]] = defaultdict(list)
    for c in a_relire:
        par_levier[c.get("levier") or c.get("module")].append(c)
    ordre = [lv for lv in leviers if lv in par_levier]
    ordre += sorted(set(par_levier) - set(ordre))

    usages = {c["id"]: _usage(c["id"], calcul, validation) for c in a_relire}
    lignes = [
        "# Liste de relecture",
        "",
        f"Générée le {date.today().isoformat()} par `outils/liste_relecture.py` à partir des "
        "registres ; ne pas modifier à la main, relancer le script.",
        "",
        "Pour chaque ligne : ouvrir le document à la page indiquée, vérifier la valeur, l'unité "
        "et ce qu'elle mesure. Cocher la case quand la valeur est conforme, ou noter l'écart. "
        "Les lignes cochées passent ensuite à `relecture: relu` dans "
        "`registres/references/chiffrages.yaml`. Le classement entre entrées du calcul et "
        "références de validation est repéré automatiquement dans le code : il est indicatif.",
        "",
        f"**{len(a_relire)} chiffrages à relire** sur {len(chiffrages)}, dont "
        f"{sum(u == ENTREE for u in usages.values())} entrées du calcul (à relire en premier : "
        f"elles changent les résultats affichés), "
        f"{sum(u == REFERENCE for u in usages.values())} références de validation et "
        f"{sum(u == NON_REPERE for u in usages.values())} non repérés automatiquement. "
        f"Puis **{len(hypotheses)} hypothèses** (valeur centrale et plage).",
        "",
        "## Sommaire",
        "",
        "| Levier ou module | À relire | Entrées du calcul |",
        "|---|---|---|",
    ]
    for lv in ordre:
        n_entree = sum(usages[c["id"]] == ENTREE for c in par_levier[lv])
        lignes.append(f"| [{lv}](#{lv}) | {len(par_levier[lv])} | {n_entree} |")
    lignes.append("")

    for lv in ordre:
        lignes += [f"## {lv}", ""]
        for usage in (ENTREE, REFERENCE, NON_REPERE):
            groupe = [c for c in par_levier[lv] if usages[c["id"]] == usage]
            if not groupe:
                continue
            lignes += [f"### {usage.capitalize()} ({len(groupe)})", ""]
            for c in groupe:
                s = sources.get(c["source"], {})
                docs = ", ".join(f"`{f}`" for f in fichiers.get(c["source"], [])) or "aucun"
                lignes += [
                    f"- [ ] `{c['id']}` : **{_nombre(float(c['valeur']))} {c['unite']}** "
                    f"({c['millesime']})",
                    f"  - Mesure : {c['mesure']}",
                    f"  - Où : {s.get('nom', c['source'])}, {c['localisation']}",
                    f"  - Document : {s.get('url', '')} ; fichier : {docs}",
                ]
            lignes.append("")

    lignes += ["## Hypothèses", ""]
    for h in hypotheses:
        plage = h["plage"]
        lignes += [
            f"- [ ] `{h['id']}` : **{_nombre(h['valeur_centrale'])} {h['unite']}**, plage "
            f"{_nombre(plage['basse'])} à {_nombre(plage['haute'])}",
            f"  - {h['libelle']}",
            f"  - Sources : {', '.join(h['sources'])} ; instruments : "
            f"{', '.join(h['instruments'])}",
        ]
    lignes.append("")
    SORTIE.write_text("\n".join(lignes), encoding="utf-8")
    print(
        f"{SORTIE.relative_to(RACINE)} : {len(a_relire)} chiffrages, {len(hypotheses)} hypothèses"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
