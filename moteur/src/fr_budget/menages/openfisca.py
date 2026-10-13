"""Adaptateur OpenFisca-France : cascade du salaire d'un salarié du privé.

OpenFisca-France est utilisé comme bibliothèque. Le système socio-fiscal est chargé une
seule fois par processus (voir :func:`systeme_socio_fiscal`).

Les noms de variables et de paramètres utilisés ici ont été vérifiés dans le paquet
installé (openfisca-france 176.1.2, voir ``docs/variables_openfisca.md``).
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from functools import cache
from typing import Any

from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_core.taxbenefitsystems import TaxBenefitSystem
from openfisca_france import FranceTaxBenefitSystem

from fr_budget.menages.corrections import CorrectionsOpenFisca, charger_corrections


@dataclass(frozen=True)
class HypothesesEmploi:
    """Hypothèses sur l'employeur et le contrat, que la législation ne fixe pas.

    Aucune valeur par défaut : chaque cas type doit citer la source de ses hypothèses.
    """

    effectif_entreprise: int
    taux_accident_travail: float
    """Taux de la cotisation AT/MP, en fraction de l'assiette (0,02 pour 2 %)."""
    mutuelle_montant_mensuel: float
    """Montant total mensuel de la complémentaire santé collective, en euros."""
    mutuelle_part_employeur: float
    """Part de la complémentaire santé payée par l'employeur, en fraction."""


@dataclass(frozen=True)
class CascadeSalaire:
    """Les étapes du salaire pour un mois, en euros."""

    cout_employeur: float
    """Brut plus cotisations patronales, moins les allègements (``salaire_super_brut``)."""
    salaire_brut: float
    """Salaire de base (``salaire_de_base``)."""
    net_avant_impot: float
    """Net à payer avant impôt sur le revenu (``salaire_net_a_payer``)."""
    net_imposable: float
    """Salaire imposable (``salaire_imposable``)."""


@cache
def systeme_socio_fiscal(corrige: bool = True) -> TaxBenefitSystem:
    """Charge le système socio-fiscal français une seule fois par processus.

    Par défaut, les corrections de ``registres/corrections_openfisca.yaml`` sont appliquées.
    ``corrige=False`` donne OpenFisca tel que publié, pour mesurer l'effet des corrections.
    """
    systeme = FranceTaxBenefitSystem()
    if not corrige:
        return systeme
    return CorrectionsOpenFisca(systeme, charger_corrections())


def smic_mensuel_brut(mois: str) -> float:
    """SMIC mensuel brut à temps plein en vigueur le premier jour de ``mois`` (« AAAA-MM »).

    Source : paramètres OpenFisca ``marche_travail.salaire_minimum.smic.smic_b_horaire``
    (références Légifrance dans les métadonnées du paramètre) et
    ``marche_travail.salaire_minimum.smic.nb_heures_travail_mensuel``.
    """
    smic = systeme_socio_fiscal().parameters.marche_travail.salaire_minimum.smic
    instant = f"{mois}-01"
    return float(smic.smic_b_horaire(instant) * smic.nb_heures_travail_mensuel(instant))


def cascade_salaire_mensuelle(
    salaire_brut: float,
    mois: str,
    hypotheses: HypothesesEmploi,
    *,
    corrige: bool = True,
    apprentissage_debut: str | None = None,
) -> CascadeSalaire:
    """Calcule la cascade du salaire d'un salarié célibataire du privé, à temps plein.

    Le salarié est non cadre, en CDI (valeurs par défaut d'OpenFisca pour
    ``categorie_salarie`` et ``contrat_de_travail``), ou apprenti si ``apprentissage_debut``
    (date de début du contrat, « AAAA-MM-JJ ») est donné. Le net imposable est le salaire
    imposable moins la part exonérée d'impôt du salaire d'un apprenti
    (``exoneration_impot_apprenti``, correction ``apprenti_impot_revenu``).
    """
    individu: dict[str, Any] = {
        "salaire_de_base": {mois: salaire_brut},
        "effectif_entreprise": {mois: hypotheses.effectif_entreprise},
        "taux_accident_travail": {mois: hypotheses.taux_accident_travail},
        "complementaire_sante_montant": {mois: hypotheses.mutuelle_montant_mensuel},
        "complementaire_sante_part_employeur": {mois: hypotheses.mutuelle_part_employeur},
    }
    if apprentissage_debut is not None:
        individu["apprenti"] = {mois: True}
        individu["apprentissage_contrat_debut"] = {mois: apprentissage_debut}
        # Rémunération d'apprenti propre à OpenFisca, ajoutée au salaire de base : neutralisée,
        # le salaire brut est donné.
        individu["remuneration_apprenti"] = {mois: 0.0}
    situation = {
        "individus": {"salarie": individu},
        "foyers_fiscaux": {"foyer": {"declarants": ["salarie"]}},
        "familles": {"famille": {"parents": ["salarie"]}},
        "menages": {"menage": {"personne_de_reference": ["salarie"]}},
    }
    simulation = SimulationBuilder().build_from_entities(systeme_socio_fiscal(corrige), situation)

    def calcul(variable: str) -> float:
        # OpenFisca émet des avertissements numpy sur des divisions par zéro qu'il
        # neutralise lui-même (par exemple pour des taxes non applicables).
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return float(simulation.calculate(variable, mois)[0])

    return CascadeSalaire(
        cout_employeur=calcul("salaire_super_brut"),
        salaire_brut=calcul("salaire_de_base"),
        net_avant_impot=calcul("salaire_net_a_payer"),
        net_imposable=calcul("salaire_imposable")
        - (calcul("exoneration_impot_apprenti") if corrige else 0.0),
    )
