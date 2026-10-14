"""Retraites, deuxième étape : relèvement de l'âge légal d'ouverture des droits, modèle par
cohortes (fiche ``docs/fiches/retraites.md``, § 8).

Pour chaque année t et chaque âge a, la génération g = t - a voit son âge de départ décalé de
s(g) : le relèvement choisi, atteint au rythme de la réforme de 2023 quelle que soit son
ampleur (hypothèse ``retraites_duree_montee_en_charge`` : un an de relèvement en quatre
générations, soit trois mois par génération), à partir de la première génération qui atteint
l'âge légal l'année d'entrée en vigueur. Le calcul n'est donc pas linéaire dans le relèvement.

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
  de pension des nouveaux retraités, hypothèse ``retraites_ecart_pension_liquidants``), nettes
  des prélèvements qu'elles auraient rapportés (CSG, CRDS, CASA et impôt sur le revenu, taux
  moyen calculé avec OpenFisca, ``fr_budget.agrege.indexation.prelevements_moyens_pension`` ;
  personne seule ou couple de retraités, valeur centrale à mi-chemin) ;
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

from fr_budget.agrege import indexation
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
    """Relèvement de l'âge de départ de ``generation``, en années : un an en
    ``duree_montee_en_charge`` générations, plafonné au relèvement choisi (signe compris)."""
    rang = generation - premiere_generation(entree) + 1
    if rang <= 0:
        return 0.0
    return float(np.sign(valeur)) * min(abs(valeur), rang / duree_montee_en_charge())


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


def _prelevements_pension(borne: str) -> float:
    """Part moyenne de la pension reprise par les administrations publiques (impôt sur le revenu
    compris) : à mi-chemin entre personne seule et couple ; bornes : les deux foyers."""
    parts = [indexation.prelevements_moyens_pension(f).total for f in indexation.FOYERS]
    if borne == "central":
        return float(np.mean(parts))
    # Plus de prélèvements perdus, moins d'économie : borne basse de l'effet.
    return max(parts) if borne == "bas" else min(parts)


def _parametres(borne: str) -> tuple[float, float, float, float]:
    """(part non décalée, part en emploi, écart de pension, prélèvements sur la pension) qui
    donnent l'effet bas, central ou haut sur le solde pour un relèvement."""
    noms = (HYPOTHESE_NON_DECALES, HYPOTHESE_EMPLOI, HYPOTHESE_PENSION)
    non_decales, emploi, pension = (hypothese(h) for h in noms)
    prelevements = _prelevements_pension(borne)
    if borne == "central":
        return (
            non_decales.valeur_centrale,
            emploi.valeur_centrale,
            pension.valeur_centrale,
            prelevements,
        )
    if borne == "bas":
        return non_decales.plage.haute, emploi.plage.basse, pension.plage.basse, prelevements
    return non_decales.plage.basse, emploi.plage.haute, pension.plage.haute, prelevements


@cache
def effet_annee(valeur: float, annee: int, entree: int, borne: str) -> float:
    """Effet sur le solde primaire des administrations publiques, en points de PIB, d'un
    relèvement de ``valeur`` années de l'âge légal entré en ``entree``."""
    if annee < entree:
        return 0.0
    non_decales, emploi, pension, prelevements = _parametres(borne)
    en_moins = retraites_en_moins(valeur, annee, entree, non_decales)
    depenses = reference()[annee].depenses_pib
    economie = en_moins / retraites(annee) * depenses * (1 + pension) * (1 - prelevements)
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
