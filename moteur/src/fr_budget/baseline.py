"""Baseline des administrations publiques de 2025 à 2046 (lot 1.3 du plan).

Deux segments, raccordés en 2030 (décision du mainteneur du 8 octobre 2026, option B) :

- 2025-2030 : trajectoire du RESF du PLF 2027 (``data/processed/baseline/resf_2027.csv``),
  reprise telle que publiée ; seuls la charge d'intérêts 2028-2030 et l'ajustement stock-flux
  implicite sont déduits (voir ``charge_interets_resf`` et ``trajectoire_resf``) ;
- 2031-2046 : projection par la formule de ``fr_budget.dette``, avec les hypothèses de
  l'Ageing Report 2024 de la Commission européenne pour la France
  (``data/processed/baseline/ageing_report_2024_fr.csv``) :

  - croissance en volume : croissance potentielle de l'Ageing Report ;
  - prix : la fiche France indique que le déflateur du PIB suit l'indice des prix à la
    consommation à partir de 2027 (fiche pays France, section pensions, « the GDP deflator
    evolves in line with the CPI as of 2027 ») ; on reprend donc l'IPCH de l'Ageing Report ;
  - taux de marché : taux d'intérêt nominal de l'Ageing Report ;
  - taux apparent : refinancement progressif (``taux_apparent_suivant``), à partir du taux
    apparent 2030 du RESF, avec la part refinancée de l'hypothèse ``baseline_part_refinancee`` ;
  - solde primaire, méthode (a) (décision du mainteneur du 8 octobre 2026) : solde primaire
    2030 du RESF, diminué de la variation du coût du vieillissement (retraites, santé,
    dépendance, éducation) depuis 2030 selon l'Ageing Report ;
  - ajustement stock-flux : hypothèse ``baseline_ajustement_stock_flux``.

Variantes de la fourchette sur la croissance et le taux (décision du mainteneur du 9 octobre
2026, options (i)) : croissance en volume maintenue au niveau de la croissance potentielle 2030
du RESF (``baseline_croissance_volume``) ; taux de marché maintenu au niveau du taux à 10 ans
2027 du RESF (``baseline_taux_marche``).

Unités : pourcentages et points de PIB, comme dans les sources (3,0 pour 3 %).
Fourchette : chaque hypothèse varie seule dans sa plage ; les bornes sont les extrêmes.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache

from fr_budget.dette import dette_suivante, part_refinancee, taux_apparent_suivant
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage, hypothese
from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "baseline"
ANNEE_DEBUT = 2025
ANNEE_RACCORD = 2030
ANNEE_FIN = 2046
POURCENT = 100.0

HYPOTHESE_PART = "baseline_part_refinancee"
HYPOTHESE_STOCK_FLUX = "baseline_ajustement_stock_flux"
HYPOTHESE_VIEILLISSEMENT = "baseline_cout_vieillissement_variantes"
HYPOTHESE_CROISSANCE = "baseline_croissance_volume"
HYPOTHESE_TAUX = "baseline_taux_marche"
SOURCES = ("plf2027_resf", "ce_ageing_report_2024")
HYPOTHESES = (
    HYPOTHESE_PART,
    HYPOTHESE_STOCK_FLUX,
    HYPOTHESE_VIEILLISSEMENT,
    HYPOTHESE_CROISSANCE,
    HYPOTHESE_TAUX,
)

# Variantes de l'Ageing Report 2024 sur le coût total du vieillissement (tableau FRc, écarts au
# scénario de référence ; définitions dans le rapport principal, Institutional Paper 279).
VARIANTES_VIEILLISSEMENT = (
    "risque_sante_dependance",
    "esperance_vie_haute",
    "migration_haute",
    "migration_basse",
    "fecondite_basse",
    "emploi_seniors_haut",
    "pgf_haute",
    "pgf_basse",
)


def _lire(nom: str) -> dict[tuple[int, str], float]:
    with (DOSSIER / nom).open(encoding="utf-8") as f:
        return {(int(r["annee"]), r["indicateur"]): float(r["valeur"]) for r in csv.DictReader(f)}


@cache
def resf() -> dict[tuple[int, str], float]:
    """Séries du RESF 2027, clé (année, indicateur), valeurs telles que publiées."""
    return _lire("resf_2027.csv")


@cache
def ageing_report() -> dict[tuple[int, str], float]:
    """Séries françaises de l'Ageing Report 2024, clé (année, indicateur)."""
    return _lire("ageing_report_2024_fr.csv")


def croissance_nominale(volume: float, prix: float) -> float:
    """Croissance nominale à partir des croissances en volume et des prix (fractions ou %)."""
    return (1 + volume) * (1 + prix) - 1


def charge_interets_resf(annee: int) -> float:
    """Charge d'intérêts des APU, en % du PIB.

    2025-2027 : RESF, annexe finances publiques, tableau 13, ligne 6. 2028-2030 : non publiée ;
    déduite du tableau 21, où l'ajustement structurel primaire est l'ajustement structurel plus
    la variation de la charge d'intérêts (tableau 6, ligne 7 = 5 + 6). Les deux termes sont
    arrondis au dixième et exprimés en points de PIB potentiel (écart au PIB effectif inférieur
    à 1 % en 2028-2030, tableau 21).
    """
    donnees = resf()
    if (annee, "charge_interets") in donnees:
        return donnees[(annee, "charge_interets")]
    variation = (
        donnees[(annee, "ajustement_structurel_primaire")]
        - donnees[(annee, "ajustement_structurel")]
    )
    return charge_interets_resf(annee - 1) + variation


@dataclass(frozen=True)
class AnneeBaseline:
    """Une année de trajectoire, en % du PIB (dette, soldes) et en % (taux, croissance)."""

    annee: int
    dette: float
    solde_primaire: float
    taux_apparent: float
    croissance_nominale: float
    ajustement_stock_flux: float


def trajectoire_resf() -> list[AnneeBaseline]:
    """Trajectoire 2025-2030 du RESF 2027.

    Dette, solde public, croissance en volume et déflateur : tableau 21 et fiche 7. Solde
    primaire = solde public + charge d'intérêts. Taux apparent = charge d'intérêts de l'année
    rapportée à la dette de l'année précédente (définition du RESF, tableau 14). Ajustement
    stock-flux : valeur qui referme la formule de la dette, pour 2025 la valeur publiée
    (tableau 14, flux de créances).
    """
    donnees = resf()
    lignes: list[AnneeBaseline] = []
    for annee in range(ANNEE_DEBUT, ANNEE_RACCORD + 1):
        dette = donnees[(annee, "dette")]
        charge = charge_interets_resf(annee)
        solde_primaire = donnees[(annee, "solde_public")] + charge
        g = POURCENT * croissance_nominale(
            donnees[(annee, "croissance_volume")] / POURCENT,
            donnees[(annee, "deflateur")] / POURCENT,
        )
        if lignes:
            precedente = lignes[-1].dette
            # Charge de l'année et dette de l'année précédente, chacune en % de son propre PIB :
            # le rapport donne r / (1 + g) ; le taux apparent (intérêts / dette de l'année
            # précédente, en euros) le multiplie par (1 + g). Vérifié sur 2026-2027, où le RESF
            # publie les deux : 2,6 / 115,7 * 1,020 = 2,29 % contre 2,3 % publié.
            r = POURCENT * charge / precedente * (1 + g / POURCENT)
            sfa = dette - precedente * (1 + r / POURCENT) / (1 + g / POURCENT) + solde_primaire
        else:
            r = donnees[(annee, "taux_apparent")]
            sfa = donnees[(annee, "flux_creances")]
        lignes.append(AnneeBaseline(annee, dette, solde_primaire, r, g, sfa))
    return lignes


def dette_resf_reproduite(annee: int) -> float:
    """Dette de ``annee`` recalculée par la formule avec les seules entrées publiées du RESF.

    Entrées : dette de l'année précédente, taux apparent et flux de créances (tableau 14),
    croissance nominale (tableau 4), solde primaire (tableau 13).
    """
    donnees = resf()
    return dette_suivante(
        donnees[(annee - 1, "dette")],
        donnees[(annee, "taux_apparent")] / POURCENT,
        donnees[(annee, "croissance_nominale")] / POURCENT,
        donnees[(annee, "solde_primaire")],
        donnees[(annee, "flux_creances")],
    )


def part_refinancee_etat(annee: int) -> float:
    """Part de la dette négociable de l'État refinancée en ``annee`` (2026 ou 2027).

    PLF 2027, PAP « Engagements financiers de l'État » (chiffrages ``dette_etat_*``) : émissions
    à moyen et long terme de l'année, plus encours des titres courts en début d'année et leur
    variation, rapportés à l'encours de début d'année.
    """
    encours_2025 = chiffrage("dette_etat_negociable_nominal_fin_2025")
    btf_2025 = chiffrage("dette_etat_btf_fin_2025")
    variation_btf_2026 = chiffrage("dette_etat_variation_btf_2026")
    if annee == ANNEE_DEBUT + 1:
        return part_refinancee(
            chiffrage("dette_etat_emissions_mlt_2026"), btf_2025, variation_btf_2026, encours_2025
        )
    if annee == ANNEE_DEBUT + 2:
        encours_2026 = (
            encours_2025
            + chiffrage("dette_etat_emissions_mlt_2026")
            - chiffrage("dette_etat_amortissements_mlt_nominal_2026")
            + variation_btf_2026
        )
        return part_refinancee(
            chiffrage("dette_etat_emissions_mlt_2027"),
            btf_2025 + variation_btf_2026,
            chiffrage("dette_etat_variation_btf_2027"),
            encours_2026,
        )
    msg = f"part refinancée de l'État disponible pour 2026 et 2027 seulement : {annee}"
    raise ValueError(msg)


def cout_vieillissement(annee: int, variante: str | None) -> float:
    """Coût total du vieillissement de l'Ageing Report, en % du PIB, avec ou sans variante."""
    ar = ageing_report()
    cout = ar[(annee, "cout_vieillissement")]
    if variante is not None:
        cout += ar[(annee, f"cout_vieillissement_ecart_{variante}")]
    return cout


def solde_primaire_projete(depart: float, annee: int, variante: str | None) -> float:
    """Solde primaire de ``annee`` (méthode (a)) : départ 2030 moins la hausse du coût du
    vieillissement depuis 2030."""
    return depart - (
        cout_vieillissement(annee, variante) - cout_vieillissement(ANNEE_RACCORD, variante)
    )


def projection(
    part_refinancee: float | None = None,
    ajustement_stock_flux: float | None = None,
    variante: str | None = None,
    croissance_volume: float | None = None,
    taux_marche: float | None = None,
) -> list[AnneeBaseline]:
    """Projection 2031-2046 à partir du point 2030 du RESF.

    Par défaut, les valeurs centrales des hypothèses du registre et les séries de l'Ageing
    Report. ``croissance_volume`` et ``taux_marche`` (en %), s'ils sont donnés, remplacent les
    séries de l'Ageing Report par une valeur constante sur toute la période.
    """
    part = hypothese(HYPOTHESE_PART).valeur_centrale if part_refinancee is None else part_refinancee
    sfa = (
        hypothese(HYPOTHESE_STOCK_FLUX).valeur_centrale
        if ajustement_stock_flux is None
        else ajustement_stock_flux
    )
    ar = ageing_report()
    depart = trajectoire_resf()[-1]
    dette, taux = depart.dette, depart.taux_apparent
    lignes = []
    for annee in range(ANNEE_RACCORD + 1, ANNEE_FIN + 1):
        marche = ar[(annee, "taux_nominal")] if taux_marche is None else taux_marche
        volume = (
            ar[(annee, "croissance_potentielle")]
            if croissance_volume is None
            else croissance_volume
        )
        taux = taux_apparent_suivant(taux, marche, part)
        g = POURCENT * croissance_nominale(volume / POURCENT, ar[(annee, "ipc")] / POURCENT)
        pb = solde_primaire_projete(depart.solde_primaire, annee, variante)
        dette = dette_suivante(dette, taux / POURCENT, g / POURCENT, pb, sfa)
        lignes.append(AnneeBaseline(annee, dette, pb, taux, g, sfa))
    return lignes


@dataclass(frozen=True)
class AnneeFourchette:
    annee: int
    dette: Fourchette
    solde_primaire: Fourchette


@cache
def trajectoires() -> tuple[tuple[AnneeBaseline, ...], tuple[tuple[AnneeBaseline, ...], ...]]:
    """Trajectoires complètes 2025-2046 : la centrale, puis chaque variante de la fourchette.

    2025-2030 : RESF, identique dans toutes les trajectoires. 2031-2046 : projection centrale
    et variantes, chaque hypothèse variant seule dans sa plage : part refinancée et
    ajustement stock-flux (bornes de leur plage), coût du vieillissement (chaque variante de
    l'Ageing Report), croissance en volume et taux de marché (borne haute de leur plage,
    maintenue de 2031 à 2046).
    """
    part = hypothese(HYPOTHESE_PART)
    sfa = hypothese(HYPOTHESE_STOCK_FLUX)
    resf_lignes = tuple(trajectoire_resf())
    variantes = [
        projection(part_refinancee=part.plage.basse),
        projection(part_refinancee=part.plage.haute),
        projection(ajustement_stock_flux=sfa.plage.basse),
        projection(ajustement_stock_flux=sfa.plage.haute),
        *(projection(variante=v) for v in VARIANTES_VIEILLISSEMENT),
        projection(croissance_volume=hypothese(HYPOTHESE_CROISSANCE).plage.haute),
        projection(taux_marche=hypothese(HYPOTHESE_TAUX).plage.haute),
    ]
    return (
        resf_lignes + tuple(projection()),
        tuple(resf_lignes + tuple(v) for v in variantes),
    )


def baseline() -> list[AnneeFourchette]:
    """Baseline 2025-2046 en fourchette (dette et solde primaire, en % du PIB).

    Les bornes sont les extrêmes de la trajectoire centrale et des variantes
    (``trajectoires``). En 2025-2030, toutes coïncident : la fourchette est réduite au RESF.
    """
    centrale, variantes = trajectoires()
    return [
        AnneeFourchette(
            c.annee,
            encadrer(c.dette, [v[i].dette for v in variantes]),
            encadrer(c.solde_primaire, [v[i].solde_primaire for v in variantes]),
        )
        for i, c in enumerate(centrale)
    ]
