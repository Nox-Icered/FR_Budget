"""Dépenses fiscales (niches fiscales) : coût, catalogue du levier et écarts de prévision (lot 2.4).

Données : fiches des tomes II de Voies et moyens des PLF 2024, 2025 et 2026
(``data/processed/niches_fiscales/depenses_fiscales.csv``, script
``pipelines/niches_fiscales/extraire_tome2.py``). Chaque PLF de l'année N donne le coût réalisé
en N-2 et prévu en N-1 et N, en M€.

Conventions :

- coût agrégé : convention du tome II (sous-partie V, « Méthodologie ») : une dépense non
  chiffrée (« nc ») reprend le dernier montant chiffré du même tome lorsqu'il existe ; « ε »
  (moins de 0,5 M€) et « - » (sans incidence) valent zéro ;
- levier (décisions du mainteneur du 9 octobre 2026) : réduction de 0 à 100 % d'une dépense
  fiscale ou de toutes celles d'un impôt, rendement égal à la part correspondante du coût prévu
  pour 2026 par le PLF 2026 (option 3 (a) : aucun effet de comportement) ; les dépenses fiscales
  de TVA et d'accise sur les énergies sont exclues (option 2 (a) : elles recouvrent les leviers
  TVA et accises) ;
- incertitude : écarts constatés entre le coût prévu par un PLF et le coût réalisé publié deux
  ans plus tard (hypothèses ``depenses_fiscales_ecart_*``).
"""

from __future__ import annotations

import csv
import statistics
from dataclasses import dataclass
from functools import cache

from fr_budget.registres.verification import RACINE_DEPOT

FICHIER = RACINE_DEPOT / "data" / "processed" / "niches_fiscales" / "depenses_fiscales.csv"
FICHIER_FICHES = RACINE_DEPOT / "data" / "processed" / "niches_fiscales" / "fiches_descriptives.csv"
PLF_LEVIER = 2026
ANNEE_COUT_LEVIER = 2026
IMPOTS_EXCLUS = ("tva", "accise_energies")
IMPOTS_LEVIER = (
    "impot_revenu",
    "impot_revenu_et_societes",
    "impot_societes",
    "autres_impots_directs",
    "enregistrement_timbre",
    "autres_droits",
    "impots_locaux",
)
CHIFFRE = "chiffre"
NON_CHIFFRE = "nc"
MILLIONS_PAR_MILLIARD = 1000.0
# Quantiles des écarts par dépense fiscale retenus pour la plage (10e et 90e centiles).
DECILES = 10
DECILE_BAS = 0
DECILE_HAUT = 8


@dataclass(frozen=True)
class Ligne:
    """Montant d'une fiche pour une année : statut (« chiffre », « nc », « ε », « - »)."""

    code: str
    impot: str
    libelle: str
    statut: str
    cout: float | None
    """M€ ; ``None`` sauf statut « chiffre »."""
    fiabilite: str


@cache
def _lignes() -> dict[tuple[int, int, str], Ligne]:
    with FICHIER.open(encoding="utf-8") as f:
        return {
            (int(r["plf"]), int(r["annee"]), r["code"]): Ligne(
                code=r["code"],
                impot=r["impot"],
                libelle=r["libelle"],
                statut=r["statut"],
                cout=float(r["cout_meur"]) if r["cout_meur"] else None,
                fiabilite=r["fiabilite"],
            )
            for r in csv.DictReader(f)
        }


def codes(plf: int) -> list[str]:
    """Numéros des dépenses fiscales d'un tome, dans l'ordre du document."""
    return list(dict.fromkeys(c for (p, _, c) in _lignes() if p == plf))


def ligne(plf: int, annee: int, code: str) -> Ligne | None:
    return _lignes().get((plf, annee, code))


@dataclass(frozen=True)
class Cout:
    """Coût retenu d'une dépense fiscale (M€) et année du montant chiffré repris."""

    valeur: float
    annee_chiffrage: int | None
    """Année du montant repris pour une dépense « nc » ; ``None`` si le montant est de l'année."""


def cout(plf: int, annee: int, code: str) -> Cout | None:
    """Coût d'une dépense fiscale selon la convention du tome II ; ``None`` si jamais chiffrée.

    Une dépense « nc » reprend le dernier montant chiffré du même tome (années antérieures).
    """
    courante = ligne(plf, annee, code)
    if courante is None:
        return None
    if courante.statut == CHIFFRE:
        return Cout(courante.cout or 0.0, None)
    if courante.statut != NON_CHIFFRE:
        return Cout(0.0, None)
    for precedente in range(annee - 1, plf - 3, -1):
        fiche = ligne(plf, precedente, code)
        if fiche is not None and fiche.statut == CHIFFRE:
            return Cout(fiche.cout or 0.0, precedente)
    return None


def cout_par_impot(plf: int, annee: int, perimetre: set[str] | None = None) -> dict[str, float]:
    """Coût total par impôt (partie du tome II), en M€, selon la convention du tome II.

    ``perimetre`` : numéros retenus (tous ceux du tome par défaut).
    """
    totaux: dict[str, float] = {}
    for code in codes(plf):
        if perimetre is not None and code not in perimetre:
            continue
        c = cout(plf, annee, code)
        fiche = ligne(plf, annee, code)
        if c is not None and fiche is not None:
            totaux[fiche.impot] = totaux.get(fiche.impot, 0.0) + c.valeur
    return totaux


@dataclass(frozen=True)
class DepenseFiscale:
    """Dépense fiscale proposée au levier : coût prévu pour 2026 par le PLF 2026."""

    code: str
    impot: str
    libelle: str
    cout: float
    """M€."""
    annee_chiffrage: int
    fiabilite: str


@cache
def catalogue() -> list[DepenseFiscale]:
    """Dépenses fiscales du levier : coût 2026 positif, hors TVA et accise sur les énergies."""
    resultat = []
    for code in codes(PLF_LEVIER):
        fiche = ligne(PLF_LEVIER, ANNEE_COUT_LEVIER, code)
        c = cout(PLF_LEVIER, ANNEE_COUT_LEVIER, code)
        if fiche is None or c is None or c.valeur <= 0 or fiche.impot in IMPOTS_EXCLUS:
            continue
        resultat.append(
            DepenseFiscale(
                code=code,
                impot=fiche.impot,
                libelle=fiche.libelle,
                cout=c.valeur,
                annee_chiffrage=c.annee_chiffrage or ANNEE_COUT_LEVIER,
                fiabilite=fiche.fiabilite,
            )
        )
    return resultat


@dataclass(frozen=True)
class FicheDescriptive:
    """Fiche descriptive d'une dépense fiscale, telle que publiée dans le tome II de Voies et
    moyens (PLF 2026) ; un champ absent de la fiche est vide."""

    finalite: str
    beneficiaires: str
    creation: str
    modification: str
    reference: str
    mission: str


@cache
def fiches_descriptives() -> dict[str, FicheDescriptive]:
    """Fiches descriptives du tome II, par numéro de dépense
    (``data/processed/niches_fiscales/fiches_descriptives.csv``)."""
    with FICHIER_FICHES.open(encoding="utf-8") as f:
        return {
            r["code"]: FicheDescriptive(
                finalite=r["finalite"],
                beneficiaires=r["beneficiaires"],
                creation=r["creation"],
                modification=r["modification"],
                reference=r["reference"],
                mission=r["mission"],
            )
            for r in csv.DictReader(f)
            if int(r["plf"]) == PLF_LEVIER
        }


def depense(code: str) -> DepenseFiscale:
    for d in catalogue():
        if d.code == code:
            return d
    msg = f"dépense fiscale absente du levier : {code}"
    raise ValueError(msg)


def cout_impot_levier(impot: str) -> float:
    """Coût 2026 (M€) des dépenses fiscales d'un impôt proposées au levier."""
    if impot not in IMPOTS_LEVIER:
        msg = f"impôt hors du levier : {impot}"
        raise ValueError(msg)
    return sum(d.cout for d in catalogue() if d.impot == impot)


def ecarts_prevision(plf_prevision: int, plf_realisation: int, annee: int) -> dict[str, float]:
    """Écart relatif (réalisé - prévu) / prévu par dépense fiscale chiffrée dans les deux tomes.

    Seules les dépenses dont la prévision est un montant chiffré strictement positif et la
    réalisation un montant chiffré sont retenues (pas de convention de reprise).
    """
    resultat = {}
    for code in codes(plf_prevision):
        prevue = ligne(plf_prevision, annee, code)
        realisee = ligne(plf_realisation, annee, code)
        if (
            prevue is None
            or realisee is None
            or prevue.statut != CHIFFRE
            or realisee.statut != CHIFFRE
            or not prevue.cout
            or prevue.cout <= 0
        ):
            continue
        resultat[code] = ((realisee.cout or 0.0) - prevue.cout) / prevue.cout
    return resultat


def plage_ecart_par_depense(
    plf_prevision: int, plf_realisation: int, annee: int
) -> tuple[float, float]:
    """10e et 90e centiles des écarts de prévision par dépense fiscale."""
    q = statistics.quantiles(
        ecarts_prevision(plf_prevision, plf_realisation, annee).values(), n=DECILES
    )
    return q[DECILE_BAS], q[DECILE_HAUT]


def ecart_par_impot(plf_prevision: int, plf_realisation: int, annee: int) -> dict[str, float]:
    """Écart relatif du coût total par impôt, prévu puis réalisé, convention du tome II.

    Périmètre commun : dépenses fiscales présentes dans les deux tomes et dont la prévision a
    un coût (une dépense créée entre les deux, ou non chiffrable lors de la prévision, n'est
    pas une erreur de prévision).
    """
    commun = {
        c
        for c in set(codes(plf_prevision)) & set(codes(plf_realisation))
        if cout(plf_prevision, annee, c) is not None
    }
    prevu = cout_par_impot(plf_prevision, annee, commun)
    realise = cout_par_impot(plf_realisation, annee, commun)
    return {i: (realise[i] - prevu[i]) / prevu[i] for i in prevu if i in realise and prevu[i]}
