"""Indexation des pensions et prestations : effet d'un écart à la revalorisation légale (lot 2.8).

Données :

- prestations des administrations publiques par code de la nomenclature des comptes de la
  protection sociale, DREES, édition 2025, année 2024
  (``data/processed/indexation/prestations_apu.csv``, ``pipelines/indexation/extraire_drees.py``) ;
- distribution de la pension mensuelle brute totale des retraités, DREES, EIR 2020, tableau 5
  (``data/processed/indexation/distribution_pensions_2020.csv``) ;
- législation d'OpenFisca-France : dates de revalorisation des prestations (date de la dernière
  valeur du paramètre de référence de chaque bloc), CSG, CRDS, CASA et impôt sur le revenu.

Périmètre (décision du mainteneur du 12 octobre 2026, option (a)) : pensions de retraite de base
et pensions de l'État, minimum vieillesse, pensions d'invalidité, AAH, ASI, prestations
familiales (hors complément de libre choix du mode de garde), AEEH, AJPP, rentes d'accidents du
travail, RSA et prime d'activité. Exclus : pensions complémentaires et supplémentaires (fixées par
les partenaires sociaux ou les régimes), aides au logement, allocations chômage, retraite du
combattant et pensions militaires d'invalidité (règles de revalorisation propres), et prestations
de santé, de dépendance ou d'action sociale (``CODES_EXCLUS`` en garde la trace des plus
proches).

Coût d'une revalorisation supérieure de ``taux`` à la revalorisation légale, l'année ``annee`` :

    somme sur les blocs de taux * montant du bloc * (1 - retour)

avec, pour la première année civile, le montant multiplié par la part de l'année qui suit la
date de revalorisation. Les montants de 2024 sont tenus constants en part du PIB nominal (INSEE
pour 2025, croissance nominale du RESF 2027 ensuite).

Retours aux administrations publiques (décision du mainteneur, option (a)) :

- pensions de retraite et d'invalidité : CSG, CRDS et CASA (lecture « net des prélèvements
  sociaux ») et impôt sur le revenu (lecture « net total »), calculés avec OpenFisca pour des
  retraités de chaque tranche de 100 euros de la distribution de l'EIR 2020 (législation 2020,
  année des pensions), en moyenne pondérée par la masse de pension de chaque tranche ; foyer
  d'une personne seule ou couple de deux retraités à la même pension (bornes de la fourchette),
  valeur centrale à mi-chemin ;
- prestations familiales : CRDS (paramètre d'OpenFisca) ;
- autres prestations : aucun prélèvement modélisé par OpenFisca.
"""

from __future__ import annotations

import csv
import warnings
from dataclasses import dataclass
from functools import cache
from typing import Any

import numpy as np
from openfisca_core.simulation_builder import SimulationBuilder

from fr_budget import baseline as module_baseline
from fr_budget.apu import comptes_apu
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage
from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "indexation"
ANNEE_COMPTES = 2024
ANNEE_REFERENCE = 2025
ANNEE_DISTRIBUTION = 2020
ANNEES_RFR = 2
"""La CSG sur les pensions dépend du revenu fiscal de référence de l'année N-2."""
MOIS_PAR_AN = 12
MILLIONS_PAR_MILLIARD = 1000.0
POURCENT = 100.0
HAUSSE_TEST = 0.01
DATE_NAISSANCE = "1950-01-01"

PENSIONS = "pensions"
FAMILLE = "famille"
AAH = "aah"
RETOUR_PENSION = "pension"
RETOUR_CRDS = "crds"
AUCUN_RETOUR = "aucun"

BRUT = "brut"
NET_PRELEVEMENTS_SOCIAUX = "net_prelevements_sociaux"
NET_TOTAL = "net_total"

SEUL = "personne_seule"
COUPLE = "couple"
FOYERS = (SEUL, COUPLE)

CHIFFRAGE_MOIS_PENSIONS = "indexation_mois_revalorisation_pensions"
PRELEVEMENTS_PENSIONS = (
    "csg_deductible_retraite",
    "csg_imposable_retraite",
    "crds_retraite",
    "casa",
)


@dataclass(frozen=True)
class Bloc:
    codes: tuple[str, ...]
    """Codes des prestations (ps_code des comptes de la protection sociale)."""
    date: str
    """Paramètre d'OpenFisca dont la dernière valeur donne la date de revalorisation, ou
    identifiant d'un chiffrage du mois de revalorisation."""
    retour: str


_PRESTATIONS = "prestations_sociales."
_INVALIDITE = _PRESTATIONS + "prestations_etat_de_sante.invalidite."
_MINIMA = _PRESTATIONS + "solidarite_insertion.minima_sociaux."
_BMAF = _PRESTATIONS + "prestations_familiales.bmaf.bmaf"

BLOCS: dict[str, Bloc] = {
    PENSIONS: Bloc(
        codes=(
            "E11-21.1.11",  # pensions normales
            "E11-21.1.12",  # pensions d'inaptitude
            "E11-21.1.13",  # pensions d'invalidité des retraités
            "E11-21.1.41",  # majorations sur pensions de base : enfant
            "E11-21.1.42",  # tierce personne
            "E11-21.1.43",  # conjoint à charge
            "E11-21.1.44",  # assurés handicapés
            "E11-21.1.45",  # autres
            "E11-21.1.99",  # autres pensions vieillesse
            "E11-22.1.11",  # réversion sans condition de ressources
            "E11-22.1.12",  # réversion avec condition de ressources
            "E11-22.1.16",  # pensions de conjoint survivant, d'orphelins (fonction publique)
            "E11-22.1.19",  # autres droits dérivés
            "E11-22.1.20",  # majorations sur pensions de réversion de base
        ),
        date=CHIFFRAGE_MOIS_PENSIONS,
        retour=RETOUR_PENSION,
    ),
    "minimum_vieillesse": Bloc(
        codes=(
            "E11-21.2.01",
            "E11-21.2.02",
            "E11-21.2.03",
            "E11-21.2.04",
            "E11-21.2.06",
            "E11-21.2.99",
        ),
        date=_PRESTATIONS
        + "solidarite_insertion.minimum_vieillesse.aspa.montant_maximum_annuel.personnes_seules",
        retour=AUCUN_RETOUR,
    ),
    "invalidite": Bloc(
        codes=("E11-12.1.21", "E11-22.1.14"),
        date=_INVALIDITE + "pensions_invalidite.revalorisations_invalidite",
        retour=RETOUR_PENSION,
    ),
    AAH: Bloc(codes=("E11-12.2.11",), date=_INVALIDITE + "aah.montant", retour=AUCUN_RETOUR),
    "asi": Bloc(codes=("E11-12.2.13",), date=_INVALIDITE + "asi.montant_seul", retour=AUCUN_RETOUR),
    FAMILLE: Bloc(
        codes=(
            "E11-30.1.01",  # allocations familiales
            "E11-30.1.02",  # complément familial
            "E11-30.1.03",  # allocation de soutien familial
            "E11-30.1.06",  # PAJE, prime d'adoption
            "E11-30.1.07",  # PAJE, allocation de base
            "E11-30.1.08",  # PAJE, allocation d'adoption
            "E11-30.2.02",  # allocation de rentrée scolaire
            "E11-30.3.08",  # PAJE, PreParE
            "E11-30.6.05",  # PAJE, prime de naissance
        ),
        date=_BMAF,
        retour=RETOUR_CRDS,
    ),
    "handicap_enfant": Bloc(
        codes=("E11-12.3.33", "E11-12.3.31"),  # AEEH, AJPP
        date=_BMAF,
        retour=AUCUN_RETOUR,
    ),
    "rentes_accidents_travail": Bloc(
        codes=("E11-13.2.11", "E11-22.1.13"),
        date=_MINIMA + "accident_travail.rente.salaire_net.salaire_minimum",
        retour=AUCUN_RETOUR,
    ),
    "rsa": Bloc(
        codes=("E11-60.1.02",),
        date=_MINIMA + "rsa.rsa_m.montant_de_base_du_rsa",
        retour=AUCUN_RETOUR,
    ),
    "prime_activite": Bloc(
        codes=("E11-60.2.01",), date=_MINIMA + "ppa.pa_m.montant_de_base", retour=AUCUN_RETOUR
    ),
}

CODES_EXCLUS = (
    "E11-21.1.14",  # retraite du combattant
    "E11-21.1.21",  # indemnités temporaires de la fonction publique
    "E11-21.1.31",  # pensions de vieillesse complémentaires
    "E11-21.1.32",  # pensions de vieillesse supplémentaires
    "E11-22.1.15",  # pensions militaires d'invalidité (ayants droit)
    "E11-22.1.21",  # indemnités temporaires de la fonction publique (ayants cause)
    "E11-22.1.31",  # pensions complémentaires obligatoires (droits dérivés)
    "E11-30.3.04",  # PAJE, complément de libre choix du mode de garde (assistante maternelle)
    "E11-30.3.05",  # PAJE, complément de libre choix du mode de garde (employée à domicile)
)


PREFIXE_DROIT_DIRECT = "E11-21"
"""Codes des prestations de droit direct du risque vieillesse."""
CODE_COMPLEMENTAIRES_DROIT_DIRECT = "E11-21.1.31"


def part_base_droit_direct(annee: int = ANNEE_COMPTES) -> float:
    """Part des pensions de base dans les pensions de retraite de droit direct de ``annee`` :
    codes de droit direct du bloc des pensions (pensions de base et de l'État, périmètre du
    levier) rapportés à ces codes plus les pensions de vieillesse complémentaires
    (``E11-21.1.31``). Comptes de la protection sociale, DREES, édition 2025."""
    prestations = _prestations()
    base = sum(
        prestations.get((annee, c), 0.0)
        for c in BLOCS[PENSIONS].codes
        if c.startswith(PREFIXE_DROIT_DIRECT)
    )
    return base / (base + prestations[(annee, CODE_COMPLEMENTAIRES_DROIT_DIRECT)])


@cache
def _prestations() -> dict[tuple[int, str], float]:
    resultat: dict[tuple[int, str], float] = {}
    with (DOSSIER / "prestations_apu.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cle = (int(r["annee"]), r["ps_code"])
            resultat[cle] = resultat.get(cle, 0.0) + float(r["millions"])
    return resultat


def facteur_pib(annee: int) -> float:
    """PIB nominal de ``annee`` rapporté à celui de l'année des comptes (2024).

    INSEE jusqu'à 2025, puis croissance nominale du RESF 2027.
    """
    pib = comptes_apu()
    if annee <= ANNEE_REFERENCE:
        return pib.valeur(annee, "S1", "pib") / pib.valeur(ANNEE_COMPTES, "S1", "pib")
    croissance = module_baseline.resf()[(annee, "croissance_nominale")]
    return facteur_pib(annee - 1) * (1 + croissance / POURCENT)


def montant(bloc: str, annee: int = ANNEE_REFERENCE) -> float:
    """Prestations du bloc versées par les administrations publiques, en Md€ de ``annee``.

    Montant de 2024 (DREES), tenu constant en part du PIB nominal.
    """
    millions = sum(_prestations().get((ANNEE_COMPTES, c), 0.0) for c in BLOCS[bloc].codes)
    return millions / MILLIONS_PAR_MILLIARD * facteur_pib(annee)


@cache
def mois_revalorisation(bloc: str) -> int:
    """Mois de la revalorisation légale du bloc."""
    date = BLOCS[bloc].date
    if date == CHIFFRAGE_MOIS_PENSIONS:
        return int(chiffrage(date))
    noeud: Any = systeme_socio_fiscal().parameters
    for nom in date.split("."):
        noeud = noeud.children[nom]
    return int(noeud.values_list[0].instant_str[5:7])


def part_premiere_annee(bloc: str) -> float:
    """Part de l'année civile qui suit la revalorisation (1 pour une revalorisation en janvier)."""
    return (MOIS_PAR_AN + 1 - mois_revalorisation(bloc)) / MOIS_PAR_AN


@dataclass(frozen=True)
class Retour:
    prelevements_sociaux: float
    """Part d'une hausse de pension brute reprise par la CSG, la CRDS et la CASA."""
    total: float
    """Même part, impôt sur le revenu compris."""


@cache
def distribution_pensions() -> tuple[np.ndarray, np.ndarray]:
    """Pension mensuelle de chaque tranche (milieu, ou borne basse pour la dernière) et part."""
    niveaux, parts = [], []
    with (DOSSIER / "distribution_pensions_2020.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            basse = float(r["borne_basse"])
            niveaux.append((basse + float(r["borne_haute"])) / 2 if r["borne_haute"] else basse)
            parts.append(float(r["part_pourcent"]))
    return np.array(niveaux), np.array(parts)


def situation_retraites(
    pensions: np.ndarray, foyer: str, annee: int = ANNEE_DISTRIBUTION
) -> dict[str, Any]:
    """Un foyer de retraités par pension mensuelle brute, versée de N-2 à N (la CSG dépend du
    revenu fiscal de référence de N-2) ; personne seule ou couple à la même pension."""
    annees = range(annee - ANNEES_RFR, annee + 1)
    mois = [f"{a}-{m:02d}" for a in annees for m in range(1, MOIS_PAR_AN + 1)]
    personnes = 2 if foyer == COUPLE else 1
    individus: dict[str, Any] = {}
    foyers: dict[str, Any] = {}
    familles: dict[str, Any] = {}
    menages: dict[str, Any] = {}
    for i, pension in enumerate(pensions):
        noms = [f"r{i}_{p}" for p in range(personnes)]
        for nom in noms:
            individus[nom] = {
                "retraite_brute": dict.fromkeys(mois, float(pension)),
                "date_naissance": {"ETERNITY": DATE_NAISSANCE},
            }
        foyers[f"f{i}"] = {"declarants": noms}
        familles[f"fa{i}"] = {"parents": noms}
        menages[f"m{i}"] = {"personne_de_reference": noms[:1], "conjoint": noms[1:]}
    return {
        "individus": individus,
        "foyers_fiscaux": foyers,
        "familles": familles,
        "menages": menages,
    }


@cache
def _revenus(foyer: str, facteur: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Pour chaque tranche : pension brute, pension après CSG, CRDS et CASA, impôt sur le revenu
    (par foyer, sur l'année)."""
    niveaux, _ = distribution_pensions()
    situation = situation_retraites(niveaux * facteur, foyer)
    simulation = SimulationBuilder().build_from_entities(systeme_socio_fiscal(), situation)
    annee = str(ANNEE_DISTRIBUTION)
    with warnings.catch_warnings():
        # Avertissements numpy neutralisés par OpenFisca lui-même (divisions par zéro).
        warnings.simplefilter("ignore", RuntimeWarning)
        brute = simulation.calculate_add("retraite_brute", annee)
        # Prélèvements sociaux : variables négatives d'OpenFisca.
        nette = brute + sum(simulation.calculate_add(v, annee) for v in PRELEVEMENTS_PENSIONS)
        # « impot_revenu_restant_a_payer » est négatif quand l'impôt est dû.
        impot = -simulation.calculate("impot_revenu_restant_a_payer", annee)
    personnes = 2 if foyer == COUPLE else 1
    par_foyer = np.repeat(np.arange(len(niveaux)), personnes)
    somme = np.bincount
    return (
        somme(par_foyer, weights=brute),
        somme(par_foyer, weights=nette),
        np.asarray(impot, dtype=float),
    )


@cache
def retour_pension(foyer: str) -> Retour:
    """Part d'une hausse des pensions reprise par les administrations publiques.

    Hausse de 1 % de la pension de chaque tranche de l'EIR 2020 (législation 2020), moyenne
    pondérée par la masse de pension de chaque tranche (part des retraités * pension).
    """
    niveaux, parts = distribution_pensions()
    brute0, nette0, impot0 = _revenus(foyer, 1.0)
    brute1, nette1, impot1 = _revenus(foyer, 1 + HAUSSE_TEST)
    hausse = brute1 - brute0
    poids = parts * niveaux
    nette = (nette1 - nette0) / hausse
    apres_impot = (nette1 - nette0 - (impot1 - impot0)) / hausse
    return Retour(
        prelevements_sociaux=float(np.average(1 - nette, weights=poids)),
        total=float(np.average(1 - apres_impot, weights=poids)),
    )


def taux_crds() -> float:
    """Taux de la CRDS sur les prestations familiales (OpenFisca, législation de 2024)."""
    parametres = systeme_socio_fiscal().parameters(str(ANNEE_COMPTES))
    return float(parametres.prelevements_sociaux.contributions_sociales.crds)


def _part_retour(bloc: str, lecture: str, foyer: str) -> float:
    if lecture == BRUT:
        return 0.0
    retour = BLOCS[bloc].retour
    if retour == RETOUR_PENSION:
        r = retour_pension(foyer)
        return r.prelevements_sociaux if lecture == NET_PRELEVEMENTS_SOCIAUX else r.total
    if retour == RETOUR_CRDS:
        return taux_crds()
    return 0.0


def _cout_foyer(
    taux: float, annee: int, blocs: tuple[str, ...], lecture: str, foyer: str, premiere: bool
) -> float:
    return sum(
        taux
        * montant(b, annee)
        * (part_premiere_annee(b) if premiere else 1.0)
        * (1 - _part_retour(b, lecture, foyer))
        for b in blocs
    )


def cout_mesure(
    taux: float,
    annee: int,
    blocs: tuple[str, ...],
    lecture: str = NET_PRELEVEMENTS_SOCIAUX,
    premiere_annee: bool = True,
) -> float:
    """Coût d'une revalorisation supérieure de ``taux`` (fraction) à la revalorisation légale.

    En Md€ de ``annee`` ; valeur centrale (à mi-chemin entre personne seule et couple). Le
    rendement d'un gel ou d'une sous-indexation est le même montant, de signe opposé.
    """
    return float(
        np.mean([_cout_foyer(taux, annee, blocs, lecture, f, premiere_annee) for f in FOYERS])
    )


def cout_brut_un_point() -> float:
    """Coût brut d'un point de revalorisation en plus, en année pleine, en Md€ de 2025."""
    return cout_mesure(1 / POURCENT, ANNEE_REFERENCE, tuple(BLOCS), BRUT, premiere_annee=False)


def cout_un_point() -> Fourchette:
    """Coût net (prélèvements sociaux et impôt sur le revenu déduits) d'un point de
    revalorisation en plus, en année pleine, en Md€ de 2025.

    Bornes : personne seule et couple de retraités ; valeur centrale à mi-chemin.
    """
    blocs = tuple(BLOCS)
    variantes = [
        _cout_foyer(1 / POURCENT, ANNEE_REFERENCE, blocs, NET_TOTAL, f, premiere=False)
        for f in FOYERS
    ]
    return encadrer(float(np.mean(variantes)), variantes)


@cache
def part_effet_premiere_annee() -> float:
    """Part du coût net en année pleine qui porte sur l'année d'entrée en vigueur.

    Les pensions sont revalorisées en janvier, la plupart des prestations en avril : la
    première année ne compte que les mois qui suivent la revalorisation de chaque bloc.
    """
    blocs = tuple(BLOCS)
    premiere = cout_mesure(1 / POURCENT, ANNEE_REFERENCE, blocs, NET_TOTAL)
    pleine = cout_mesure(1 / POURCENT, ANNEE_REFERENCE, blocs, NET_TOTAL, premiere_annee=False)
    return premiere / pleine
