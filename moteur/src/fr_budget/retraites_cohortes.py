"""Retraites, deuxième étape : relèvement de l'âge légal d'ouverture des droits, modèle par
cohortes (fiche ``docs/fiches/retraites.md``, § 8).

Pour chaque année t et chaque âge a, la génération g = t - a voit son âge de départ décalé de
s(g) : le relèvement choisi, atteint à raison du rythme de la réforme de 2023 (hypothèse
``retraites_duree_montee_en_charge`` : un an de relèvement en quatre générations), à partir de
la première génération qui atteint l'âge légal l'année d'entrée en vigueur.

Données :

- population au 1er janvier par âge, Insee, projections 2021, scénario central
  (``data/processed/retraites/cohortes_population.csv``) ;
- taux de retraités par âge en 2023, DREES, fiche 15 (``cohortes_taux_retraites.csv``) ;
- âge légal et âge d'annulation de la décote par génération, DREES, fiche 14
  (``cohortes_ages_legaux.csv``) ;
- dépenses du système de retraite en part du PIB, COR, juin 2026 (``fr_budget.retraites``) ;
- prélèvements sur un salaire (coût employeur moins revenu après impôt du célibataire au salaire
  médian, OpenFisca, ``fr_budget.menages.types``) et PIB nominal (INSEE).

Calcul, en points de PIB :

- taux de retraités de la génération décalée : r(a - s) (interpolation linéaire), sans dépasser
  r(a), et inchangé à partir de l'âge d'annulation de la décote, qui ne bouge pas ;
- retraités en moins : somme sur les âges de population * (r(a) - r décalé) * (1 - part des
  départs non décalés, hypothèse ``retraites_part_departs_non_decales``) ;
- moindres pensions : retraités en moins ÷ retraités de l'année * dépenses du COR * (1 + écart
  de pension des nouveaux retraités, hypothèse ``retraites_ecart_pension_liquidants``) ;
- recettes : retraités en moins * part en emploi (hypothèse
  ``retraites_part_emploi_avant_liquidation``) * prélèvements par salarié ÷ PIB ; les
  prélèvements par salarié suivent le PIB par personne de 20 à 64 ans.

Non comptés : prestations des personnes décalées sans emploi (chômage, invalidité, minima),
pensions plus élevées après des carrières plus longues, effets sur l'emploi et l'activité.
"""

from __future__ import annotations

import csv
from functools import cache

import numpy as np

from fr_budget.apu import comptes_apu
from fr_budget.fourchette import Fourchette
from fr_budget.menages import types as menages
from fr_budget.registres.acces import hypothese
from fr_budget.registres.verification import RACINE_DEPOT
from fr_budget.retraites import duree_montee_en_charge, reference

DOSSIER = RACINE_DEPOT / "data" / "processed" / "retraites"
HYPOTHESE_NON_DECALES = "retraites_part_departs_non_decales"
HYPOTHESE_EMPLOI = "retraites_part_emploi_avant_liquidation"
HYPOTHESE_PENSION = "retraites_ecart_pension_liquidants"
MENAGE_SALAIRE = "celibataire_median"
ANNEE_SALAIRE = menages.ANNEE
AGE_ACTIF_MIN = 20
AGE_ACTIF_MAX = 64
POURCENT = 100.0
EUROS_PAR_MILLIARD = 1e9
BORNES = ("bas", "central", "haut")


@cache
def population() -> dict[tuple[int, int], float]:
    with (DOSSIER / "cohortes_population.csv").open(encoding="utf-8") as f:
        return {(int(r["annee"]), int(r["age"])): float(r["effectif"]) for r in csv.DictReader(f)}


@cache
def taux_retraites() -> tuple[np.ndarray, np.ndarray]:
    with (DOSSIER / "cohortes_taux_retraites.csv").open(encoding="utf-8") as f:
        lignes = [(int(r["age"]), float(r["taux"])) for r in csv.DictReader(f)]
    ages, taux = zip(*sorted(lignes), strict=True)
    return np.array(ages, dtype=float), np.array(taux)


@cache
def ages_legaux() -> dict[int, tuple[float, float]]:
    with (DOSSIER / "cohortes_ages_legaux.csv").open(encoding="utf-8") as f:
        return {
            int(r["generation"]): (float(r["age_ouverture"]), float(r["age_annulation_decote"]))
            for r in csv.DictReader(f)
        }


def taux(age: float) -> float:
    """Taux de retraités de 2023 à ``age`` (interpolation ; au-delà du dernier âge publié, taux
    du dernier âge ; avant le premier, nul)."""
    ages, valeurs = taux_retraites()
    return float(np.interp(age, ages, valeurs, left=0.0, right=valeurs[-1]))


def premiere_generation(entree: int) -> int:
    """Première génération concernée : la première qui atteint l'âge légal l'année
    d'entrée en vigueur ou après."""
    return min(g for g, (ouverture, _) in ages_legaux().items() if g + ouverture >= entree)


def decalage(valeur: float, generation: int, entree: int) -> float:
    """Relèvement de l'âge de départ de ``generation``, en années."""
    rang = generation - premiere_generation(entree) + 1
    if rang <= 0:
        return 0.0
    return valeur * min(1.0, rang / duree_montee_en_charge())


def retraites_en_moins(valeur: float, annee: int, entree: int, non_decales: float) -> float:
    """Nombre de retraités en moins en ``annee``."""
    total = 0.0
    for (a, age), effectif in population().items():
        if a != annee:
            continue
        generation = annee - age
        if generation not in ages_legaux():
            continue
        s = decalage(valeur, generation, entree)
        if s == 0 or age >= ages_legaux()[generation][1]:
            continue
        reference_ = taux(age)
        decale = taux(age - s)
        ecart = reference_ - min(reference_, decale) if s > 0 else reference_ - decale
        total += effectif * ecart * (1 - non_decales)
    return total


def retraites(annee: int) -> float:
    """Retraités de droit direct de ``annee`` selon le taux de retraités de 2023."""
    return sum(e * taux(age) for (a, age), e in population().items() if a == annee)


def actifs(annee: int) -> float:
    """Population de 20 à 64 ans de ``annee``."""
    return sum(
        e
        for (a, age), e in population().items()
        if a == annee and AGE_ACTIF_MIN <= age <= AGE_ACTIF_MAX
    )


@cache
def prelevements_par_salarie_pib() -> float:
    """Prélèvements sur un salarié au salaire médian (coût employeur moins revenu après impôt,
    hors prestations), en part du PIB de la même année."""
    cascade = menages.cascade_annuelle(MENAGE_SALAIRE, ANNEE_SALAIRE)
    prelevements = cascade.cout_employeur - (cascade.net_avant_impot - cascade.impot_revenu)
    pib = comptes_apu().valeur(ANNEE_SALAIRE, "S1", "pib") * EUROS_PAR_MILLIARD
    return prelevements / pib


def _parametres(borne: str) -> tuple[float, float, float]:
    """(part non décalée, part en emploi, écart de pension) qui donnent l'effet bas, central ou
    haut sur le solde pour un relèvement."""
    hypotheses = [
        hypothese(h) for h in (HYPOTHESE_NON_DECALES, HYPOTHESE_EMPLOI, HYPOTHESE_PENSION)
    ]
    if borne == "central":
        return tuple(h.valeur_centrale for h in hypotheses)  # type: ignore[return-value]
    non_decales, emploi, pension = hypotheses
    if borne == "bas":
        return non_decales.plage.haute, emploi.plage.basse, pension.plage.basse
    return non_decales.plage.basse, emploi.plage.haute, pension.plage.haute


@cache
def effet_annee(valeur: float, annee: int, entree: int, borne: str) -> float:
    """Effet sur le solde primaire des administrations publiques, en points de PIB, d'un
    relèvement de ``valeur`` années de l'âge légal entré en ``entree``."""
    if annee < entree:
        return 0.0
    non_decales, emploi, pension = _parametres(borne)
    en_moins = retraites_en_moins(valeur, annee, entree, non_decales)
    depenses = reference()[annee].depenses_pib
    economie = en_moins / retraites(annee) * depenses * (1 + pension)
    salaire = prelevements_par_salarie_pib()
    recettes = en_moins * emploi * salaire * _facteur_salaire(annee)
    return POURCENT * (economie + recettes)


def _facteur_salaire(annee: int) -> float:
    """Prélèvements par salarié en part du PIB : constants en part du PIB par personne de 20 à
    64 ans (le salaire suit le PIB par personne d'âge actif)."""
    return actifs(ANNEE_SALAIRE) / actifs(annee)


def effet(valeur: float, annee: int, entree: int) -> Fourchette:
    valeurs = sorted(effet_annee(valeur, annee, entree, b) for b in BORNES)
    return Fourchette(
        bas=valeurs[0], central=effet_annee(valeur, annee, entree, "central"), haut=valeurs[2]
    )
