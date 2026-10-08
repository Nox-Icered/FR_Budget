"""Corrections apportées à OpenFisca-France en attendant leur prise en compte en amont.

Les corrections et leurs sources sont décrites dans ``registres/corrections_openfisca.yaml``.
Elles sont appliquées sous forme de réforme OpenFisca : le paquet installé n'est pas modifié.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from openfisca_core.periods import period as periode
from openfisca_core.reforms import Reform
from openfisca_core.taxbenefitsystems import TaxBenefitSystem
from openfisca_core.variables import Variable

NOM_REGISTRE = "corrections_openfisca.yaml"
# Dans le dépôt, le registre est à la racine ; un paquet installé en embarque une copie.
REGISTRE_DEPOT = Path(__file__).parents[4] / "registres" / NOM_REGISTRE


def charger_corrections(fichier: Path | None = None) -> dict[str, Any]:
    """Lit le registre des corrections : celui du dépôt s'il existe, sinon celui du paquet."""
    if fichier is not None:
        texte = fichier.read_text(encoding="utf-8")
    elif REGISTRE_DEPOT.is_file():
        texte = REGISTRE_DEPOT.read_text(encoding="utf-8")
    else:
        texte = files("fr_budget").joinpath("registres", NOM_REGISTRE).read_text(encoding="utf-8")
    contenu: dict[str, Any] = yaml.safe_load(texte)
    return contenu


def _noeud(parametres: Any, chemin: str) -> Any:
    noeud = parametres
    for nom in chemin.split("."):
        noeud = getattr(noeud, nom)
    return noeud


def _corriger_parametre(correction: dict[str, Any]) -> Any:
    def modifier(parametres: Any) -> Any:
        noeud = _noeud(parametres, correction["parametre"])
        if "tranche" in correction:
            noeud = noeud.brackets[correction["tranche"]].rate
        date_effet = correction["date_effet"]
        posterieures = [v.instant_str for v in noeud.values_list if v.instant_str > date_effet]
        if posterieures:
            # Écraser une valeur plus récente fixée en amont serait une erreur silencieuse.
            msg = f"{correction['id']} : OpenFisca a des valeurs postérieures {posterieures}"
            raise ValueError(msg)
        noeud.update(start=periode(date_effet), value=correction["valeur"])
        return parametres

    return modifier


def _envelopper(
    systeme: TaxBenefitSystem, nom: str, terme: str, signe: int, date_effet: str
) -> tuple[type[Variable], type[Variable]]:
    """Ajoute ``signe * terme`` à la variable ``nom`` à partir de ``date_effet``.

    Les formules d'OpenFisca sont conservées telles quelles sous le nom ``{nom}_openfisca`` ;
    la nouvelle variable ``nom`` vaut ``{nom}_openfisca`` plus la correction.
    """
    origine = systeme.get_variable(nom)
    formules = {
        "formula" if date == "0001-01-01" else f"formula_{date.replace('-', '_')}": formule
        for date, formule in origine.formulas.items()
    }
    attributs = {
        "value_type": origine.value_type,
        "entity": type(origine).entity,
        "definition_period": origine.definition_period,
        "set_input": origine.set_input,
    }
    nom_openfisca = f"{nom}_openfisca"
    sans_correction = type(
        nom_openfisca,
        (Variable,),
        {
            **attributs,
            "label": f"{origine.label} (formule d'OpenFisca sans correction)",
            **formules,
        },
    )

    def formule_corrigee(individu: Any, period: Any) -> Any:
        valeur = individu(nom_openfisca, period)
        if str(period.start) < date_effet:
            return valeur
        return valeur + signe * individu(terme, period)

    corrigee = type(
        nom,
        (Variable,),
        {
            **attributs,
            "label": origine.label,
            "reference": origine.reference,
            "formula": formule_corrigee,
        },
    )
    return sans_correction, corrigee


class CorrectionsOpenFisca(Reform):  # type: ignore[misc]
    """Réforme qui applique les corrections du registre."""

    name = "Corrections du projet FR_Budget"

    def __init__(self, systeme: TaxBenefitSystem, corrections: dict[str, Any]) -> None:
        self._corrections = corrections
        super().__init__(systeme)

    def apply(self) -> None:
        for correction in self._corrections["corrections"]:
            if correction["type"] == "parametre":
                self.modify_parameters(modifier_function=_corriger_parametre(correction))
            elif correction["type"] == "variable":
                for nom, signe in correction["ajouter"].items():
                    sans_correction, corrigee = _envelopper(
                        self, nom, correction["terme"], signe, correction["date_effet"]
                    )
                    self.add_variable(sans_correction)
                    self.update_variable(corrigee)
            else:
                msg = f"Correction inconnue : {correction['id']}"
                raise ValueError(msg)
