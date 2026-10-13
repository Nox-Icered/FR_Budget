"""Corrections d'OpenFisca-France qui demandent une formule (``type: formule`` dans
``registres/corrections_openfisca.yaml``).

Chaque fonction de ``FORMULES`` reçoit la réforme et l'entrée du registre. Les taux et les
dates sont lus dans l'entrée (rubrique ``valeurs``), qui cite leurs sources ; le SMIC vient
des paramètres d'OpenFisca (``marche_travail.salaire_minimum.smic``).

Apprentis (OpenFisca-France 176.1.2 exonère l'apprenti de toutes ses cotisations salariales,
sans plafond, mais pas de CSG, de CRDS ni d'impôt sur le revenu) :

- cotisations salariales exonérées sur la part du salaire inférieure à 79 % du SMIC (contrat
  conclu avant le 1er mars 2025) ou à 50 % du SMIC (contrat conclu depuis) ;
- CSG et CRDS : exonération totale (contrat conclu avant le 1er mars 2025) ou sur la part
  inférieure à 50 % du SMIC (depuis) ;
- impôt sur le revenu : salaire exonéré dans la limite du SMIC, appliquée mois par mois
  comme dans le modèle de calcul de l'Urssaf.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import numpy as np
from openfisca_core.model_api import ADD, MONTH
from openfisca_core.reforms import Reform
from openfisca_core.variables import Variable
from openfisca_france.entities import Individu

from fr_budget.menages.corrections import _remplacer

Formule = Callable[[Reform, dict[str, Any]], None]


def _smic_mensuel(parameters: Any, period: Any) -> Any:
    smic = parameters(period).marche_travail.salaire_minimum.smic
    return smic.smic_b_horaire * smic.nb_heures_travail_mensuel


def _contrat_recent(individu: Any, period: Any, valeurs: dict[str, Any]) -> Any:
    """Contrat conclu depuis la date du nouveau régime (``date_nouveau_regime``)."""
    debut = individu("apprentissage_contrat_debut", period)
    return debut >= np.datetime64(str(valeurs["date_nouveau_regime"]))


def _avant(period: Any, date_effet: str) -> bool:
    return str(period.start) < date_effet


def apprenti_cotisations_salariales(reforme: Reform, correction: dict[str, Any]) -> None:
    """Plafonne l'exonération de cotisations salariales de l'apprenti.

    Approximation : l'exonération est la part du salaire sous le plafond, appliquée à toutes
    les cotisations salariales. Elle est exacte tant que ces cotisations sont proportionnelles
    au salaire, c'est-à-dire sous le plafond de la Sécurité sociale.
    """
    valeurs = correction["valeurs"]
    date_effet = str(correction["date_effet"])

    def fabrique(nom_origine: str) -> Any:
        def formule(individu: Any, period: Any, parameters: Any) -> Any:
            if _avant(period, date_effet):
                return individu(nom_origine, period)
            apprenti = individu("apprenti", period)
            cotisations = individu("cotisations_salariales_contributives", period) + individu(
                "cotisations_salariales_non_contributives", period
            )
            part_smic = np.where(
                _contrat_recent(individu, period, valeurs),
                valeurs["part_smic_cotisations_depuis"],
                valeurs["part_smic_cotisations_avant"],
            )
            plafond = part_smic * _smic_mensuel(parameters, period)
            assiette = individu("assiette_cotisations_sociales", period)
            part_exoneree = np.where(
                assiette > plafond, plafond / np.maximum(assiette, plafond), 1.0
            )
            return -cotisations * apprenti * part_exoneree

        return formule

    for variable in _remplacer(
        reforme, "exoneration_cotisations_salariales_apprenti", fabrique, correction["id"]
    ):
        _ajouter_ou_remplacer(reforme, variable)


def apprenti_csg_crds(reforme: Reform, correction: dict[str, Any]) -> None:
    """Exonère de CSG et de CRDS le salaire de l'apprenti, en corrigeant les deux assiettes
    de la CSG (qui servent aussi à la CRDS)."""
    valeurs = correction["valeurs"]
    date_effet = str(correction["date_effet"])

    def fabrique_abattue(nom_origine: str) -> Any:
        def formule(individu: Any, period: Any, parameters: Any) -> Any:
            assiette = individu(nom_origine, period)
            if _avant(period, date_effet):
                return assiette
            plafond = valeurs["part_smic_csg_crds_depuis"] * _smic_mensuel(parameters, period)
            reduite = np.where(
                _contrat_recent(individu, period, valeurs), np.maximum(assiette - plafond, 0), 0
            )
            return np.where(individu("apprenti", period), reduite, assiette)

        return formule

    def fabrique_non_abattue(nom_origine: str) -> Any:
        def formule(individu: Any, period: Any, parameters: Any) -> Any:
            assiette = individu(nom_origine, period)
            if _avant(period, date_effet):
                return assiette
            # Part patronale de la prévoyance : exonérée avec le salaire, sauf pour un contrat
            # récent dont le salaire dépasse le plafond.
            plafond = valeurs["part_smic_csg_crds_depuis"] * _smic_mensuel(parameters, period)
            salaire = individu("assiette_cotisations_sociales", period)
            soumise = _contrat_recent(individu, period, valeurs) & (salaire > plafond)
            return np.where(individu("apprenti", period) & ~soumise, 0, assiette)

        return formule

    for nom, fabrique in (
        ("assiette_csg_abattue", fabrique_abattue),
        ("assiette_csg_non_abattue", fabrique_non_abattue),
    ):
        for variable in _remplacer(reforme, nom, fabrique, correction["id"]):
            _ajouter_ou_remplacer(reforme, variable)


def apprenti_impot_revenu(reforme: Reform, correction: dict[str, Any]) -> None:
    """Retire du revenu imposé comme des salaires la part exonérée du salaire de l'apprenti."""
    date_effet = str(correction["date_effet"])

    def exoneration(individu: Any, period: Any, parameters: Any) -> Any:
        imposable = np.maximum(individu("salaire_imposable", period), 0)
        if _avant(period, date_effet):
            return imposable * 0
        plafond = _smic_mensuel(parameters, period)
        return individu("apprenti", period) * np.minimum(imposable, plafond)

    # Variable ajoutée par la correction (construite par type(), comme les variables
    # corrigées) ; nulle avant la date d'effet, comme la correction du revenu imposable.
    reforme.add_variable(
        type(
            "exoneration_impot_apprenti",
            (Variable,),
            {
                "value_type": float,
                "entity": Individu,
                "label": "Salaire de l'apprenti exonéré d'impôt (limite : SMIC)",
                "definition_period": MONTH,
                "formula": exoneration,
            },
        )
    )

    def fabrique(nom_origine: str) -> Any:
        def formule(individu: Any, period: Any) -> Any:
            valeur = individu(nom_origine, period)
            if _avant(period, date_effet):
                return valeur
            return valeur - individu("exoneration_impot_apprenti", period, options=[ADD])

        return formule

    for variable in _remplacer(reforme, "revenu_assimile_salaire", fabrique, correction["id"]):
        _ajouter_ou_remplacer(reforme, variable)


def _ajouter_ou_remplacer(reforme: Reform, variable: type[Variable]) -> None:
    if variable.__name__ in reforme.variables:
        reforme.update_variable(variable)
    else:
        reforme.add_variable(variable)


FORMULES: dict[str, Formule] = {
    "apprenti_cotisations_salariales": apprenti_cotisations_salariales,
    "apprenti_csg_crds": apprenti_csg_crds,
    "apprenti_impot_revenu": apprenti_impot_revenu,
}
