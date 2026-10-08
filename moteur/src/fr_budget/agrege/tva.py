"""Levier TVA : assiette par taux et rendement statique d'un point de TVA.

Méthode : modèle de la TVA théorique décrit par la DG Trésor (Cahier n° 2016-02,
« Le modèle d'estimation de la TVA théorique », parties 2.1 à 2.3), appliqué aux données
publiques de l'INSEE (comptes nationaux annuels base 2020) :

1. consommation finale des ménages, des APU (individuelle) et des ISBLSM au niveau le plus
   fin publié, chaque produit étant rattaché à un régime de TVA
   (``registres/tva/correspondance_produits.csv``) ;
2. consommation collective des APU, consommations intermédiaires et investissement au niveau
   A38 du TES, avec un régime par produit (``registres/tva/regimes_a38.csv``) ;
3. investissement diminué de la production pour emploi final propre (P12), qui n'est pas
   vendue et ne porte pas de TVA ;
4. TVA non déductible (rémanente) des producteurs : prorata de non-déductibilité de chaque
   branche égal à la part exonérée ou hors champ de la consommation finale de son produit
   (assimilation produit-branche, Cahier 2016-02 § 2.2.3) ;
5. produits relevant de plusieurs taux : répartis à l'aide du coût des taux réduits publié dans
   le tome II de Voies et Moyens (``registres/tva/depenses_fiscales.yaml``) ;
6. recette : diminuée de l'écart dû aux taux d'outre-mer et de Corse, chiffré dans le même
   tome II (le modèle applique les taux de la France métropolitaine à toute la consommation).

Les montants des comptes nationaux sont aux prix d'acquisition, TVA non déductible comprise :
l'assiette hors taxe s'obtient en divisant par (1 + taux * part non déductible).

Les taux de TVA viennent des paramètres d'OpenFisca-France
(``taxation_indirecte.tva``), qui citent leurs textes.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import yaml

from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.schemas import DepenseFiscaleTva, UsageDepenseFiscale
from fr_budget.registres.verification import RACINE_DEPOT

DONNEES = RACINE_DEPOT / "data" / "processed" / "tva"
REGISTRES = RACINE_DEPOT / "registres"

TAUX_TAXES = ("super_reduit", "reduit", "intermediaire", "normal")
NON_TAXES = ("exonere", "hors_champ")
CLES_POINT = {
    "super_reduit": "taux_2_1",
    "reduit": "taux_5_5",
    "intermediaire": "taux_10",
    "normal": "taux_20",
}
PARAMETRES_OPENFISCA = {
    "super_reduit": "taux_particulier_super_reduit",
    "reduit": "taux_reduit",
    "intermediaire": "taux_intermediaire",
    "normal": "taux_normal",
}
PAYEURS = ("menages", "apu", "isblsm", "entreprises")
SECTEURS_FINALS = ("menages", "apu", "isblsm")
MILLIONS_PAR_MILLIARD = 1000
UN_POINT = 0.01


@dataclass(frozen=True)
class Assiette:
    """Assiette hors taxe portant de la TVA, en millions d'euros, par régime et par payeur."""

    montants: Mapping[tuple[str, str], float]

    def par_regime(self, regime: str, payeurs: Iterable[str] = PAYEURS) -> float:
        return sum(self.montants.get((regime, p), 0.0) for p in payeurs)


@dataclass(frozen=True)
class Repartition:
    """Parts de la consommation (TTC) d'un produit par régime de TVA.

    ``exces`` : part de l'assiette des taux réduits qui dépasse la consommation du produit
    (0 si elle y tient). Un excès signale que la dépense fiscale couvre aussi d'autres emplois
    que la consommation finale (par exemple l'investissement des ménages).
    """

    parts: Mapping[str, float]
    exces: float


@dataclass(frozen=True)
class PointTva:
    """Rendement statique d'une hausse d'un point de TVA, en milliards d'euros.

    Clés : ``ensemble``, ``taux_2_1``, ``taux_5_5``, ``taux_10``, ``taux_20``.
    ``net`` retranche la TVA supplémentaire payée par les administrations publiques
    (Trésor-Éco n° 371, tableau 2).
    """

    brut: Mapping[str, float]
    net: Mapping[str, float]


# --- Paramètres et données -------------------------------------------------------------


def taux_tva(annee: int) -> dict[str, float]:
    """Taux de TVA en vigueur au 1er juillet de ``annee`` (paramètres OpenFisca-France)."""
    tva = systeme_socio_fiscal().parameters.taxation_indirecte.tva
    return {
        r: float(getattr(tva, nom)(f"{annee}-07-01")) for r, nom in PARAMETRES_OPENFISCA.items()
    }


def _lire_csv(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def regimes_produits() -> dict[str, str]:
    return {
        r["code"]: r["regime"] for r in _lire_csv(REGISTRES / "tva" / "correspondance_produits.csv")
    }


def regimes_a38() -> dict[str, str]:
    return {r["a38"]: r["regime"] for r in _lire_csv(REGISTRES / "tva" / "regimes_a38.csv")}


def consommation_fine(secteur: str, annee: int) -> list[tuple[str, str, float]]:
    """(code produit, code A38, montant TTC en M€) de la consommation finale d'un secteur."""
    lignes = _lire_csv(DONNEES / f"consommation_{secteur}_{annee}.csv")
    return [(r["code"], r["a38"], float(r["millions_euros"])) for r in lignes]


def tes(annee: int, table: str) -> dict[tuple[str, str], float]:
    lignes = _lire_csv(DONNEES / f"tes_{annee}_{table}.csv")
    colonnes = list(lignes[0].keys())
    return {(r[colonnes[0]], r[colonnes[1]]): float(r["millions_euros"]) for r in lignes}


def depenses_fiscales() -> list[DepenseFiscaleTva]:
    contenu = yaml.safe_load(
        (REGISTRES / "tva" / "depenses_fiscales.yaml").read_text(encoding="utf-8")
    )
    return [DepenseFiscaleTva.model_validate(d) for d in contenu["depenses_fiscales"]]


def chiffrage(identifiant: str) -> float:
    contenu = yaml.safe_load(
        (REGISTRES / "references" / "chiffrages.yaml").read_text(encoding="utf-8")
    )
    return float(next(c["valeur"] for c in contenu["chiffrages"] if c["id"] == identifiant))


# --- Calculs (fonctions pures) ---------------------------------------------------------


def base_hors_taxe(montant_ttc: float, taux: float, part_non_deductible: float = 1.0) -> float:
    """Assiette hors taxe d'un achat aux prix d'acquisition (TVA non déductible comprise)."""
    return montant_ttc / (1 + taux * part_non_deductible)


def prorata_non_deductibilite(
    consommations: Iterable[tuple[str, str, float]],
    regime_produit: Mapping[str, str],
    regime_a38: Mapping[str, str],
) -> dict[str, float]:
    """Part non déductible de chaque branche A38 (Cahier DG Trésor 2016-02, § 2.2.3).

    Égale à la part exonérée ou hors champ de la consommation finale du produit de la branche.
    Une branche dont le produit n'a pas de consommation finale prend la valeur de son régime A38.
    """
    total: dict[str, float] = defaultdict(float)
    non_taxe: dict[str, float] = defaultdict(float)
    for code, a38, montant in consommations:
        total[a38] += montant
        if regime_produit[code] in NON_TAXES:
            non_taxe[a38] += montant
    return {
        a38: (non_taxe[a38] / total[a38]) if total[a38] > 0 else float(regime in NON_TAXES)
        for a38, regime in regime_a38.items()
    }


def assiette_depense_fiscale(cout: float, taux_reduit: float, taux_norme: float) -> float:
    """Assiette hors taxe d'un taux réduit, déduite de son coût : coût / (norme - taux réduit).

    Le tome II de Voies et Moyens chiffre le coût d'un taux réduit par rapport à une norme (le
    taux normal pour les dépenses utilisées ici). Le chiffrage est statique : la même assiette
    est taxée au taux réduit et à la norme.
    """
    return cout / (taux_norme - taux_reduit)


def repartition_par_taux(
    consommation_ttc: float,
    assiettes_reduites: Mapping[str, float],
    taux: Mapping[str, float],
) -> Repartition:
    """Parts de la consommation TTC d'un produit aux taux réduits et au taux normal.

    Chaque assiette hors taxe au taux réduit est convertie en montant TTC. Si leur total tient
    dans la consommation, le reste est au taux normal ; sinon toute la consommation est aux
    taux réduits, au prorata, et l'excès est renvoyé.
    """
    ttc = {r: a * (1 + taux[r]) for r, a in assiettes_reduites.items()}
    total = sum(ttc.values())
    if total >= consommation_ttc:
        return Repartition({r: v / total for r, v in ttc.items()}, total / consommation_ttc - 1)
    parts = {r: v / consommation_ttc for r, v in ttc.items()}
    parts["normal"] = 1 - total / consommation_ttc
    return Repartition(parts, 0.0)


def assiette_consommation_finale(
    consommations: Iterable[tuple[str, str, float]],
    regime_produit: Mapping[str, str],
    taux: Mapping[str, float],
    payeur: str,
    repartitions: Mapping[str, Mapping[str, float]] | None = None,
) -> dict[tuple[str, str], float]:
    """Assiette hors taxe de la consommation finale d'un secteur non assujetti.

    ``repartitions`` donne, pour les produits relevant de plusieurs taux, la part de chaque
    régime ; les autres produits suivent ``regime_produit``.
    """
    assiette: dict[tuple[str, str], float] = defaultdict(float)
    for code, _, montant in consommations:
        parts = (repartitions or {}).get(code, {regime_produit[code]: 1.0})
        for regime, part in parts.items():
            if regime in TAUX_TAXES:
                assiette[(regime, payeur)] += base_hors_taxe(montant * part, taux[regime])
    return assiette


def assiette_remanente(
    achats: Mapping[str, float],
    regime_a38: Mapping[str, str],
    taux: Mapping[str, float],
    part_non_deductible: float,
) -> dict[str, float]:
    """Assiette hors taxe non déductible d'achats par produit A38, par régime."""
    assiette: dict[str, float] = defaultdict(float)
    if part_non_deductible <= 0:
        return assiette
    for produit, montant in achats.items():
        regime = regime_a38[produit]
        if regime in TAUX_TAXES and montant > 0:
            base = base_hors_taxe(montant, taux[regime], part_non_deductible)
            assiette[regime] += base * part_non_deductible
    return assiette


@cache
def repartitions_produits_mixtes() -> dict[str, Repartition]:
    """Répartition par taux des produits relevant de plusieurs taux.

    Calculée sur la consommation de l'année des dépenses fiscales (tous secteurs), puis
    appliquée telle quelle aux autres années (hypothèse ``tva_repartition_produits_mixtes_stable``).
    """
    par_produit: dict[tuple[str, int], dict[str, float]] = defaultdict(dict)
    for df in depenses_fiscales():
        if df.usage == UsageDepenseFiscale.REPARTITION:
            assert df.produit is not None and df.regime is not None  # garanti par le schéma
            taux = taux_tva(df.annee)
            par_produit[(df.produit, df.annee)][df.regime.value] = assiette_depense_fiscale(
                chiffrage(df.chiffrage), taux[df.regime.value], taux["normal"]
            )
    repartitions = {}
    for (produit, annee), assiettes in par_produit.items():
        consommation = sum(
            montant
            for secteur in SECTEURS_FINALS
            for code, _, montant in consommation_fine(secteur, annee)
            if code == produit
        )
        repartitions[produit] = repartition_par_taux(consommation, assiettes, taux_tva(annee))
    return repartitions


def ecart_territorial() -> float:
    """Écart de TVA dû aux taux d'outre-mer et de Corse, en Md€ (année des chiffrages).

    Retranché de la recette de chaque année (hypothèse ``tva_ecart_territorial_stable``).
    """
    return (
        sum(
            chiffrage(df.chiffrage)
            for df in depenses_fiscales()
            if df.usage == UsageDepenseFiscale.ECART_TERRITORIAL
        )
        / MILLIONS_PAR_MILLIARD
    )


def estimer_assiette(annee_comptes: int) -> Assiette:
    """Assiette hors taxe portant de la TVA, par régime et par payeur, pour une année de comptes."""
    taux = taux_tva(annee_comptes)
    regime_produit = regimes_produits()
    regime_a38 = regimes_a38()
    repartitions = {p: r.parts for p, r in repartitions_produits_mixtes().items()}
    fines = {s: consommation_fine(s, annee_comptes) for s in SECTEURS_FINALS}
    tef = tes(annee_comptes, "tef")
    tei = tes(annee_comptes, "tei")
    cpr = tes(annee_comptes, "cpr")
    produits = list(regime_a38)

    montants: dict[tuple[str, str], float] = defaultdict(float)
    for secteur, consommations in fines.items():
        for cle, valeur in assiette_consommation_finale(
            consommations, regime_produit, taux, secteur, repartitions
        ).items():
            montants[cle] += valeur

    # Consommation collective des APU : régime A38, entièrement non déductible.
    collective = {p: tef.get((p, "CF Collective APU"), 0.0) for p in produits}
    for regime, valeur in assiette_remanente(collective, regime_a38, taux, 1.0).items():
        montants[(regime, "apu")] += valeur

    # Prorata de non-déductibilité par branche.
    consommations_finales = [c for liste in fines.values() for c in liste]
    collective_lignes = [(f"A38_{p}", p, v) for p, v in collective.items()]
    regime_etendu = {**regime_produit, **{f"A38_{p}": regime_a38[p] for p in produits}}
    pnd = prorata_non_deductibilite(
        [*consommations_finales, *collective_lignes], regime_etendu, regime_a38
    )

    # Consommations intermédiaires : part de chaque branche payée par les APU et les ISBLSM,
    # égale à la part de sa production consommée par eux (assimilation produit-branche).
    for branche in produits:
        production = cpr.get(("P1", branche), 0.0)
        part_apu = (
            min(1.0, tef.get((branche, "CF Total APU"), 0.0) / production) if production else 0.0
        )
        part_isblsm = (
            min(1.0 - part_apu, tef.get((branche, "CF ISBLSM"), 0.0) / production)
            if production
            else 0.0
        )
        achats = {p: tei.get((p, branche), 0.0) for p in produits}
        for regime, valeur in assiette_remanente(achats, regime_a38, taux, pnd[branche]).items():
            montants[(regime, "apu")] += valeur * part_apu
            montants[(regime, "isblsm")] += valeur * part_isblsm
            montants[(regime, "entreprises")] += valeur * (1 - part_apu - part_isblsm)

    # Investissement : ménages hors entrepreneurs individuels, APU et ISBLSM ne déduisent pas ;
    # les sociétés supportent le prorata moyen de leurs branches (pondéré par leurs consommations
    # intermédiaires), les sociétés financières celui de la branche KZ.
    ci_branche = {b: sum(tei.get((p, b), 0.0) for p in produits) for b in produits}
    marchandes = [b for b in produits if pnd[b] < 1 and b != "KZ"]
    pnd_snfei = sum(pnd[b] * ci_branche[b] for b in marchandes) / sum(
        ci_branche[b] for b in marchandes
    )
    fbcf_secteurs = {
        "FBCF Ménages hors EI": ("menages", 1.0),
        "FBCF APU": ("apu", 1.0),
        "FBCF ISBLSM": ("isblsm", 1.0),
        "FBCF SNFEI": ("entreprises", pnd_snfei),
        "FBCF SFEI": ("entreprises", pnd["KZ"]),
    }
    # La production pour emploi final propre (P12 : R&D, logiciels, constructions réalisées
    # en interne) entre dans la FBCF sans transaction, donc sans TVA : elle est retirée de la
    # FBCF du produit correspondant, au prorata des secteurs (assimilation produit-branche).
    fbcf_totale = {p: sum(tef.get((p, c), 0.0) for c in fbcf_secteurs) for p in produits}
    part_achetee = {
        p: max(0.0, 1 - cpr.get(("P12", p), 0.0) / fbcf_totale[p]) if fbcf_totale[p] > 0 else 0.0
        for p in produits
    }
    for colonne, (payeur, part) in fbcf_secteurs.items():
        achats = {p: tef.get((p, colonne), 0.0) * part_achetee[p] for p in produits}
        for regime, valeur in assiette_remanente(achats, regime_a38, taux, part).items():
            montants[(regime, payeur)] += valeur

    return Assiette(montants=dict(montants))


def point_tva(assiette: Assiette, coefficient: float = 1.0) -> PointTva:
    """Rendement d'un point sur chaque taux, en Md€, multiplié par ``coefficient``."""
    brut = {
        CLES_POINT[r]: assiette.par_regime(r) * UN_POINT * coefficient / MILLIONS_PAR_MILLIARD
        for r in TAUX_TAXES
    }
    net = {
        CLES_POINT[r]: (assiette.par_regime(r) - assiette.par_regime(r, ["apu"]))
        * UN_POINT
        * coefficient
        / MILLIONS_PAR_MILLIARD
        for r in TAUX_TAXES
    }
    brut["ensemble"] = sum(brut.values())
    net["ensemble"] = sum(net.values())
    return PointTva(brut=brut, net=net)


def recette(assiette: Assiette, taux: Mapping[str, float]) -> float:
    """TVA théorique totale, en Md€."""
    return sum(assiette.par_regime(r) * taux[r] for r in TAUX_TAXES) / MILLIONS_PAR_MILLIARD


# --- Points d'entrée ------------------------------------------------------------------

# Vieillissement : la DG Trésor vieillit le point TVA avec l'évolution des recettes de TVA
# (Trésor-Éco n° 371, note 5). On utilise les recettes budgétaires publiées.
RECETTES_VIEILLISSEMENT = {
    2022: "tva_nette_totale_2022_dgtresor",
    2025: "tva_nette_totale_prevision_2025",
}


@cache
def estimer_point_tva(annee_comptes: int, annee_cible: int) -> PointTva:
    coefficient = 1.0
    if annee_cible != annee_comptes:
        coefficient = chiffrage(RECETTES_VIEILLISSEMENT[annee_cible]) / chiffrage(
            RECETTES_VIEILLISSEMENT[annee_comptes]
        )
    return point_tva(estimer_assiette(annee_comptes), coefficient)


@cache
def estimer_recette_totale(annee_comptes: int) -> float:
    """Recette de TVA reconstituée, diminuée de l'écart dû aux taux d'outre-mer et de Corse."""
    return recette(estimer_assiette(annee_comptes), taux_tva(annee_comptes)) - ecart_territorial()
