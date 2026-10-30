"""Accise sur les produits énergétiques (ex-TICPE) : recette et assiette du levier (lot 2.2).

Recette brute = somme, sur les produits, des ventes converties en hectolitres (ou en 100 kg)
multipliées par le tarif d'accise. Périmètre : France métropolitaine, comme la référence (tome I
de Voies et Moyens, ligne 1501, « brute totale », avant transferts et remboursements).

Données et paramètres :

- ventes en tonnes : SDES (``data/processed/accises/ventes_produits_petroliers.csv``) ;
- masses volumiques : Base Carbone de l'ADEME (hypothèse ``accises_masses_volumiques``) ;
- tarifs par hectolitre ou par 100 kg : paramètres OpenFisca-France
  (``taxation_indirecte.produits_energetiques.ticpe``), sauf le gazole non routier en 2024
  (chiffrage ``accises_tarif_gnr_non_agricole_2024``, hypothèse ``accises_tarif_moyen_gnr_2024``) ;
- carburéacteurs : non comptés (tarif nul pour la navigation aérienne commerciale, CIBS
  L. 312-58 ; guide 2026 sur la fiscalité des énergies, page 24) ;
- GPL : tarif combustible ou carburant selon l'hypothèse ``accises_gpl_part_carburant``.

Assiette du levier (décision du mainteneur du 9 octobre 2026, options (a)) : gazole routier et
essences (SP95, SP95-E10, SP98). Pour le gazole, les volumes des transporteurs routiers, du
transport collectif et des taxis sont retirés : leur tarif réduit est fixe, une hausse du tarif
normal leur est remboursée. Ces volumes sont déduits des dépenses fiscales 800221, 800222 et
800220 (tome II de Voies et Moyens) divisées par l'écart entre le tarif normal et le tarif réduit.
Ces dépenses fiscales sont les prévisions 2025 du PLF 2026 (décision du mainteneur du 9 octobre
2026 ; le PLF 2025 prévoyait 1 272, 183 et 50 M€).
"""

from __future__ import annotations

import csv
from functools import cache

from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage, hypothese
from fr_budget.registres.verification import RACINE_DEPOT

FICHIER_VENTES = RACINE_DEPOT / "data" / "processed" / "accises" / "ventes_produits_petroliers.csv"
HYPOTHESE_MASSES = "accises_masses_volumiques"
HYPOTHESE_GPL = "accises_gpl_part_carburant"
HYPOTHESE_GNR_2024 = "accises_tarif_moyen_gnr_2024"
ANNEE_GNR_CHIFFREE = 2024

# Base Carbone de l'ADEME, « PCI et masse volumique » (kg/m³), saisies au registre des chiffrages
# (registres/references/chiffrages.yaml) : gazole (« gasoil »), essence, fioul domestique. Le
# gazole non routier prend la valeur du gazole, l'E85 celle de l'essence.
CHIFFRAGES_MASSES = {
    "gazole": "ademe_masse_volumique_gazole",
    "essence": "ademe_masse_volumique_essence",
    "fod": "ademe_masse_volumique_fioul_domestique",
}
MASSES_VOLUMIQUES = {famille: chiffrage(cle) for famille, cle in CHIFFRAGES_MASSES.items()}


HECTOLITRES_PAR_M3 = 10.0
TONNES_PAR_100KG = 0.1
EUROS_PAR_MILLIARD = 1e9
MILLIONS = 1e6

# Paramètres OpenFisca-France (taxation_indirecte.produits_energetiques.ticpe), €/hl ou €/100 kg.
PARAMETRES = {
    "gazole": "gazole.gazole",
    "gnr": "gazole.carburants_sous_conditions_hectolitre",
    "fod": "gazole.fioul_domestique_hectolitre",
    "sp95": "super.super_95_98",
    "sp98": "super.super_95_98",
    "e10": "super.super_e10",
    "e85": "super.super_e_85_utilise_comme_carburant_hectolitre",
    "gpl_combustible": "propane_carburants.usages_autres_que_comme_carburant_100kg_nets",
    "gpl_carburant": "propane_carburants.autres_100kg_nets",
    "fol": "fioul.fioul_lourd_100kg_net",
}
# Produits du SDES, masse volumique et clé de tarif (en hl) ; GPL et fioul lourd, taxés par
# 100 kg, sont traités à part.
PRODUITS_HL = {
    "gazole": ("gazole", "gazole"),
    "gnr": ("gazole", "gnr"),
    "fod": ("fod", "fod"),
    "super_sans_plomb_95": ("essence", "sp95"),
    "super_sans_plomb_98": ("essence", "sp98"),
    "super_sans_plomb_95_e10": ("essence", "e10"),
    "super_eth_e85": ("essence", "e85"),
}
ESSENCES_LEVIER = ("super_sans_plomb_95", "super_sans_plomb_98", "super_sans_plomb_95_e10")
REMBOURSEMENTS = {
    "transport_routier_marchandises": (
        "accises_remboursement_trm_2025",
        "accises_tarif_trm_2025",
    ),
    "transport_collectif": (
        "accises_remboursement_transport_collectif_2025",
        "accises_tarif_transport_collectif_2025",
    ),
    "taxis": ("accises_remboursement_taxis_2025", "accises_tarif_taxis_gazole_2025"),
}
ANNEE_REMBOURSEMENTS = 2025


@cache
def _ventes() -> dict[tuple[int, str], float]:
    with FICHIER_VENTES.open(encoding="utf-8") as f:
        return {(int(r["annee"]), r["produit"]): float(r["tonnes"]) for r in csv.DictReader(f)}


def ventes(annee: int) -> dict[str, float]:
    """Ventes de l'année, en tonnes, par produit (noms du SDES en minuscules)."""
    return {p: v for (a, p), v in _ventes().items() if a == annee}


def hectolitres(tonnes: float, masse_volumique: float) -> float:
    """Volume en hectolitres d'une masse en tonnes, masse volumique en kg/m³."""
    return tonnes / (masse_volumique / 1000.0) * HECTOLITRES_PAR_M3


@cache
def tarifs(annee: int) -> dict[str, float]:
    """Tarifs d'accise au 1er janvier de ``annee`` (€/hl ; €/100 kg pour le GPL et le fioul lourd).

    Source : paramètres OpenFisca-France ; gazole non routier 2024 : hypothèse
    ``accises_tarif_moyen_gnr_2024`` (valeur centrale égale au chiffrage du guide 2026).
    """
    ticpe = systeme_socio_fiscal().parameters.taxation_indirecte.produits_energetiques.ticpe
    resultat = {}
    for cle, chemin in PARAMETRES.items():
        noeud = ticpe
        for partie in chemin.split("."):
            noeud = getattr(noeud, partie)
        resultat[cle] = float(noeud(f"{annee}-01-01"))
    if annee == ANNEE_GNR_CHIFFREE:
        resultat["gnr"] = hypothese(HYPOTHESE_GNR_2024).valeur_centrale
    return resultat


def recette_brute(
    annee: int,
    ecart_masses: float | None = None,
    part_gpl_carburant: float | None = None,
    tarif_gnr: float | None = None,
    hausse_gazole: float = 0.0,
    hausse_essences: float = 0.0,
) -> float:
    """Recette brute de l'accise sur les produits énergétiques, en Md€.

    ``hausse_gazole`` et ``hausse_essences`` (€/hl, soit centimes par litre) s'ajoutent aux
    tarifs du gazole routier et des essences SP95, SP95-E10 et SP98. Les autres arguments
    remplacent la valeur centrale des hypothèses correspondantes.
    """
    ecart = hypothese(HYPOTHESE_MASSES).valeur_centrale if ecart_masses is None else ecart_masses
    part = (
        hypothese(HYPOTHESE_GPL).valeur_centrale
        if part_gpl_carburant is None
        else part_gpl_carburant
    )
    t = dict(tarifs(annee))
    if tarif_gnr is not None:
        t["gnr"] = tarif_gnr
    t["gazole"] += hausse_gazole
    for cle in ("sp95", "sp98", "e10"):
        t[cle] += hausse_essences
    v = ventes(annee)
    total = sum(
        hectolitres(v[produit], MASSES_VOLUMIQUES[famille] * (1 + ecart)) * t[cle]
        for produit, (famille, cle) in PRODUITS_HL.items()
    )
    gpl = v["gpl"] / TONNES_PAR_100KG
    total += gpl * ((1 - part) * t["gpl_combustible"] + part * t["gpl_carburant"])
    total += v["fol"] / TONNES_PAR_100KG * t["fol"]
    return total / EUROS_PAR_MILLIARD


def volumes_rembourses(annee: int = ANNEE_REMBOURSEMENTS) -> dict[str, float]:
    """Volumes de gazole (hl) dont la hausse du tarif normal serait remboursée.

    Dépense fiscale (M€, prévision 2025 du PLF 2026) divisée par l'écart entre le tarif normal
    du gazole au 1er janvier de ``annee`` et le tarif réduit de l'activité (€/hl).
    """
    gazole = tarifs(annee)["gazole"]
    return {
        activite: chiffrage(depense) * MILLIONS / (gazole - chiffrage(tarif))
        for activite, (depense, tarif) in REMBOURSEMENTS.items()
    }


def assiette_levier(annee: int, ecart_masses: float | None = None) -> dict[str, float]:
    """Assiette (hl) d'une hausse du tarif : gazole routier net des volumes remboursés,
    essences SP95, SP95-E10 et SP98."""
    ecart = hypothese(HYPOTHESE_MASSES).valeur_centrale if ecart_masses is None else ecart_masses
    v = ventes(annee)
    gazole = hectolitres(v["gazole"], MASSES_VOLUMIQUES["gazole"] * (1 + ecart))
    essences = sum(
        hectolitres(v[p], MASSES_VOLUMIQUES["essence"] * (1 + ecart)) for p in ESSENCES_LEVIER
    )
    return {"gazole": gazole - sum(volumes_rembourses(annee).values()), "essences": essences}
