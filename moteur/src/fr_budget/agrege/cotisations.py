"""Cotisations patronales du secteur privé et allègements généraux (lot 2.10).

Données (``registres/references/chiffrages.yaml``) : rapports à la Commission des comptes de la
sécurité sociale (CCSS) d'octobre 2026, d'octobre 2025, d'octobre 2024 et de septembre 2018.

Leviers (choix faits en autonomie, signalés dans ``docs/fiches/cotisations_patronales.md``) :

- taux de cotisation patronale déplafonnée du secteur privé, en points : rendement d'un point =
  valeur de point de la CCSS (secteur privé, régimes de base). La CCSS suppose compensée la
  hausse des exonérations qu'entraîne la hausse de taux ; pour les administrations publiques,
  cela revient à supposer la hausse hors du champ des allègements généraux ;
- allègements généraux de cotisations des salariés (réduction générale dégressive unique et
  réductions de taux maladie et famille, tous attributaires, hors réductions de taux des
  travailleurs non salariés), variation en % du coût.

Les cotisations des employeurs publics sont exclues : elles circulent entre administrations
publiques et ne changent pas leur solde.

Rendements bruts : l'effet sur l'impôt sur les sociétés et l'impôt sur le revenu (charges
déductibles, salaires) n'est pas compté, comme dans les chiffrages de la CCSS.
"""

from __future__ import annotations

from fr_budget.agrege.indexation import facteur_pib
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage

ANNEE_REFERENCE = 2025
ANNEE_POINT = 2026
ANNEES_ALLEGEMENTS = (2024, 2025, 2027)
MILLIONS_PAR_MILLIARD = 1000.0
POURCENT = 100.0


def valeur_point_prive(annee: int) -> float:
    """Valeur d'un point de cotisation déplafonnée du secteur privé publiée par la CCSS, Md€."""
    return chiffrage(f"cotisations_point_prive_{annee}") / MILLIONS_PAR_MILLIARD


def _en_2025(montant: float, annee: int) -> float:
    """Montant de ``annee`` tenu constant en part du PIB nominal, en Md€ de 2025."""
    return montant * facteur_pib(ANNEE_REFERENCE) / facteur_pib(annee)


def rendement_point_taux() -> Fourchette:
    """Rendement d'une hausse d'un point du taux, en Md€ de 2025.

    Valeur centrale : valeur de point la plus récente (2026), ramenée en 2025 par le PIB nominal.
    Bornes : la même et la valeur de point publiée pour 2025 (CCSS d'octobre 2025).
    """
    central = _en_2025(valeur_point_prive(ANNEE_POINT), ANNEE_POINT)
    return encadrer(central, [valeur_point_prive(ANNEE_REFERENCE)])


def valeur_point_modele(annee: int) -> float:
    """Valeur centrale d'un point en ``annee`` (validation), en Md€ courants."""
    return rendement_point_taux().central * facteur_pib(annee) / facteur_pib(ANNEE_REFERENCE)


def cout_allegements(annee: int) -> float:
    """Coût des allègements généraux des salariés, tous attributaires, en Md€ (CCSS 2026).

    Ligne « allègements généraux et mesures de modulation des taux » moins les réductions de
    taux des travailleurs non salariés.
    """
    millions = (
        chiffrage(f"allegements_generaux_total_{annee}")
        - chiffrage(f"allegements_tns_famille_{annee}")
        - chiffrage(f"allegements_tns_maladie_{annee}")
    )
    return millions / MILLIONS_PAR_MILLIARD


def cout_un_pourcent_allegements() -> Fourchette:
    """Coût d'une hausse de 1 % des allègements généraux, en Md€ de 2025.

    Valeur centrale : coût constaté de 2025. Bornes : coûts de 2024 (constaté) et de 2027
    (prévu, après le gel du barème de la RGDU), tenus constants en part du PIB.
    """
    valeurs = [_en_2025(cout_allegements(a), a) / POURCENT for a in ANNEES_ALLEGEMENTS]
    return encadrer(cout_allegements(ANNEE_REFERENCE) / POURCENT, valeurs)
