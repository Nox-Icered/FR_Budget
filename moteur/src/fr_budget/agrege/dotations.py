"""Dotations de l'État aux collectivités : assiette et effet sur le solde public (lot 2.6).

Données (``data/processed/dotations_collectivites/``) :

- prélèvements sur les recettes de l'État au profit des collectivités, par ligne, tomes I de
  Voies et moyens des PLF 2024 à 2026 (``pipelines/dotations_collectivites/extraire_psr.py``) ;
- agrégats des comptes consolidés des communes, groupements à fiscalité propre, départements
  et régions, OFGL (``pipelines/dotations_collectivites/extraire_ofgl.py``).

Leviers (décisions du mainteneur du 9 octobre 2026, options (a)) :

- dotation globale de fonctionnement (ligne 3101) ;
- compensations d'exonérations et de réformes fiscales (``LIGNES_COMPENSATIONS``), hors fonds
  de compensation de la TVA (remboursement proportionnel à l'investissement) et hors fonds de
  compensation des nuisances aéroportuaires.

Effet sur le solde des administrations publiques : une dotation est un transfert de l'État aux
collectivités, toutes deux dans les administrations publiques. Le solde public ne change que
par la réaction des collectivités ; le modèle retient la baisse (ou la hausse) de leur
investissement, estimée par niveau de collectivité :

    variation de l'investissement = élasticité * investissement / dotations * variation des
    dotations

avec l'élasticité de court terme de la Caisse des Dépôts (hypothèses
``dotations_elasticite_investissement_<niveau>``), l'investissement hors remboursements et les
concours de l'État de l'OFGL (exercice ``ANNEE_OFGL``). La variation est répartie entre niveaux
au prorata de ce que chacun reçoit : DGF de l'OFGL (plus, pour les régions, la DGF réintégrée en
2026), ou péréquations et compensations fiscales de l'OFGL pour les compensations. Le taux de
répercussion de chaque niveau est plafonné à 1.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage, hypothese
from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "dotations_collectivites"
LIGNE_DGF = "3101"
LIGNES_COMPENSATIONS = (
    "3104",
    "3107",
    "3119",
    "3120",
    "3121",
    "3122",
    "3123",
    "3130",
    "3135",
    "3145",
    "3146",
    "3159",
    "3163",
    "3165",
)
DGF = "dgf"
COMPENSATIONS = "compensations"
LIGNES = {DGF: (LIGNE_DGF,), COMPENSATIONS: LIGNES_COMPENSATIONS}
PLF_LEVIER = 2026
NIVEAUX = ("communes", "gfp", "departements", "regions")
ANNEE_OFGL = 2024
INVESTISSEMENT = "Dépenses d'investissement hors remb"
CONCOURS = "Concours de l'Etat"
AGREGAT_DGF = "Dotation globale de fonctionnement"
AGREGAT_COMPENSATIONS = "Péréquations et compensations fiscales"
CHIFFRAGE_DGF_REGIONS = "dotations_dgf_regions_reintegree_2026"
MILLIERS_PAR_MILLIARD = 1e6
EUROS_PAR_MILLIARD = 1e9
EUROS_PAR_MILLION = 1e6


@cache
def _psr() -> list[dict[str, str]]:
    with (DOSSIER / "psr_collectivites.csv").open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@cache
def _ofgl() -> dict[tuple[str, int, str], float]:
    with (DOSSIER / "ofgl_agregats.csv").open(encoding="utf-8") as f:
        return {
            (r["niveau"], int(r["annee"]), r["agregat"]): float(r["euros"])
            for r in csv.DictReader(f)
        }


def montant_psr(plf: int, colonne: str, codes: tuple[str, ...]) -> float:
    """Somme des lignes ``codes`` d'une colonne du tableau d'un PLF, en Md€.

    Colonnes : « execution » (N-2), « lfi » et « revise » (N-1), « plf » (N).
    """
    milliers = sum(
        float(r["milliers_euros"])
        for r in _psr()
        if int(r["plf"]) == plf and r["colonne"] == colonne and r["code"] in codes
    )
    return milliers / MILLIERS_PAR_MILLIARD


def total_publie(plf: int, colonne: str) -> float:
    """Ligne de total du tableau (contrôle de l'extraction), en Md€."""
    return montant_psr(plf, colonne, ("total",))


def montant_levier(dotation: str) -> float:
    """Montant proposé par le PLF 2026 pour une dotation du levier, en Md€ de 2026."""
    return montant_psr(PLF_LEVIER, "plf", LIGNES[dotation])


def ofgl(niveau: str, agregat: str, annee: int = ANNEE_OFGL) -> float:
    """Agrégat de l'OFGL pour un niveau de collectivité, en euros."""
    return _ofgl()[(niveau, annee, agregat)]


def _dgf_regions_reintegree() -> float:
    return chiffrage(CHIFFRAGE_DGF_REGIONS) * EUROS_PAR_MILLION


def parts(dotation: str) -> dict[str, float]:
    """Part de chaque niveau de collectivité dans une dotation du levier."""
    agregat = AGREGAT_DGF if dotation == DGF else AGREGAT_COMPENSATIONS
    montants = {n: ofgl(n, agregat) for n in NIVEAUX}
    if dotation == DGF:
        montants["regions"] += _dgf_regions_reintegree()
    total = sum(montants.values())
    return {n: v / total for n, v in montants.items()}


def ratio_investissement(niveau: str) -> float:
    """Investissement hors remboursements rapporté aux concours de l'État (OFGL).

    Pour les régions, les concours incluent la DGF réintégrée en 2026, qui remplace des
    fractions de TVA : sans elle, le ratio décrirait des régions presque sans dotation.
    """
    concours = ofgl(niveau, CONCOURS)
    if niveau == "regions":
        concours += _dgf_regions_reintegree()
    return ofgl(niveau, INVESTISSEMENT) / concours


def _elasticites(borne: str) -> dict[str, float]:
    resultat = {}
    for n in NIVEAUX:
        h = hypothese(f"dotations_elasticite_investissement_{n}")
        resultat[n] = {
            "bas": h.plage.basse,
            "central": h.valeur_centrale,
            "haut": h.plage.haute,
        }[borne]
    return resultat


def taux_repercussion(dotation: str) -> Fourchette:
    """Part d'une variation de la dotation qui devient une variation de l'investissement local.

    Somme sur les niveaux de part * min(1, élasticité * investissement / dotations).
    """
    p = parts(dotation)
    valeurs = {
        borne: sum(
            p[n] * min(1.0, e * ratio_investissement(n)) for n, e in _elasticites(borne).items()
        )
        for borne in ("bas", "central", "haut")
    }
    return encadrer(valeurs["central"], [valeurs["bas"], valeurs["haut"]])


@dataclass(frozen=True)
class Execution:
    lfi: float
    execution: float


def execution(dotation: str, annee: int) -> Execution:
    """Montant voté en LFI (PLF de l'année suivante) et exécuté (PLF de N+2), en Md€."""
    codes = LIGNES[dotation]
    return Execution(
        lfi=montant_psr(annee + 1, "lfi", codes),
        execution=montant_psr(annee + 2, "execution", codes),
    )
