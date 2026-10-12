"""Module retraites, première étape : relèvement de l'âge effectif moyen de départ (lot 3.1).

Données : projections du COR de juin 2026, scénario de référence
(``data/processed/retraites/cor_2026_reference.csv``, ``pipelines/retraites/extraire_cor.py``).

Effet d'un an d'âge effectif sur le solde du système de retraite, l'année t (en points de PIB),
déduit de la figure 2.24 du COR, où chacun des trois leviers rétablit seul l'équilibre :
le relèvement d'âge Δa(t) qui équilibre le système fait le même effet que

- la baisse de pension relative Δp(t) : dépenses(t) * Δp(t) / p(t) (voie « pension ») ;
- la hausse du taux de prélèvement Δτ(t) : ressources(t) * Δτ(t) / τ(t) (voie
  « prélèvement », égale au déficit publié).

Rapportées à Δa(t), les deux voies donnent les bornes de l'effet d'un an ; la valeur centrale
est leur moyenne. Choix du lot 3.1, à relire (``docs/fiches/retraites.md``) : calcul mécanique
du COR, sans interaction entre leviers ni bouclage macroéconomique.

Montée en charge : linéaire sur ``duree_montee_en_charge()`` ans (rythme de trois mois par
génération de la réforme de 2023), quel que soit l'écart choisi.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from functools import cache

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import hypothese
from fr_budget.registres.verification import RACINE_DEPOT

FICHIER = RACINE_DEPOT / "data" / "processed" / "retraites" / "cor_2026_reference.csv"
HYPOTHESE_MONTEE = "retraites_duree_montee_en_charge"
POURCENT = 100.0


@dataclass(frozen=True)
class AnneeCor:
    annee: int
    depenses_pib: float
    ressources_pib: float
    pension_relative_ref: float
    pension_relative_equilibre: float
    age_ref: float
    age_equilibre: float
    taux_ref: float
    taux_equilibre: float


@cache
def reference() -> dict[int, AnneeCor]:
    """Scénario de référence du COR (juin 2026), par année."""
    with FICHIER.open(encoding="utf-8") as f:
        lignes = [
            AnneeCor(int(r.pop("annee")), **{k: float(v) for k, v in r.items()})
            for r in csv.DictReader(f)
        ]
    return {a.annee: a for a in lignes}


@cache
def effet_un_an(annee: int) -> Fourchette:
    """Effet sur le solde, l'année ``annee``, d'un âge effectif plus élevé d'un an, en points
    de PIB (voies « pension » et « prélèvement » de la figure 2.24 du COR)."""
    a = reference()[annee]
    ecart_age = a.age_equilibre - a.age_ref
    pension = (
        a.depenses_pib
        * (a.pension_relative_ref - a.pension_relative_equilibre)
        / a.pension_relative_ref
    )
    prelevement = a.ressources_pib * (a.taux_equilibre - a.taux_ref) / a.taux_ref
    voies = [POURCENT * v / ecart_age for v in (pension, prelevement)]
    return encadrer(sum(voies) / len(voies), voies)


def duree_montee_en_charge() -> float:
    """Durée de la montée en charge, en années (registre d'hypothèses)."""
    return hypothese(HYPOTHESE_MONTEE).valeur_centrale


def part_montee(annee: int, entree: int) -> float:
    """Part de l'écart d'âge atteinte en ``annee`` pour une mesure entrée en ``entree``."""
    if annee < entree:
        return 0.0
    return min(1.0, (annee - entree + 1) / duree_montee_en_charge())


def effet(valeur: float, annee: int, entree: int, borne: str) -> float:
    """Effet sur le solde primaire, en points de PIB, d'un écart d'âge effectif de ``valeur``
    années entré en ``entree`` ; ``borne`` : bas, central ou haut (bornes ordonnées quel que
    soit le signe de ``valeur``)."""
    f = effet_un_an(annee)
    part = part_montee(annee, entree)
    if borne == "central":
        return valeur * part * f.central
    extremes = sorted(valeur * part * x for x in (f.bas, f.haut))
    return extremes[0] if borne == "bas" else extremes[1]


def effet_a_horizon(horizon: int, entree: int) -> float:
    """Effet central d'un an d'âge effectif sur le solde la ``horizon``-ième année après
    l'entrée en vigueur (première année = 1), en points de PIB (validation)."""
    return effet(1.0, entree + horizon - 1, entree, "central")
