"""Schémas des registres (``registres/*.yaml``).

Chaque entité suit le modèle de données de la spécification (``docs/specification.md``,
section « Modèle de données »). Les schémas refusent les champs inconnus, pour qu'une
faute de frappe ne passe pas inaperçue.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

Identifiant = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9_]*$")]
Texte = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Acces(StrEnum):
    """Comment la source a été consultée."""

    DIRECT = "direct"
    """Document primaire consulté directement."""
    RECHERCHE_WEB = "recherche_web"
    """Cité d'après des résultats de recherche ; à confirmer sur le document primaire."""
    PAQUET = "paquet"
    """Paquet logiciel installé (OpenFisca, modèle Urssaf…)."""


class Source(Strict):
    """Entité « source » : un document ou un paquet publié."""

    id: Identifiant
    nom: Texte
    editeur: Texte
    url: Texte
    licence: Texte
    """Licence de réutilisation, ou « non précisée »."""
    date_publication: date | None = None
    millesime: Texte | None = None
    acces: Acces
    consulte_le: date


class Dataset(Strict):
    """Entité « dataset » : série ou tableau extrait d'une source."""

    id: Identifiant
    source: Identifiant
    description: Texte
    fichier: Texte
    """Chemin depuis la racine du dépôt (``data/raw/…``)."""
    empreinte_sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    methode_transformation: Texte
    """Script de ``pipelines/`` qui produit les tables à partir de ce fichier."""
    telecharge_le: date


class Plage(Strict):
    basse: float
    haute: float


class Hypothese(Strict):
    """Entité « assumption » : hypothèse avec valeur centrale et plage."""

    id: Identifiant
    libelle: Texte
    unite: Texte
    valeur_centrale: float
    plage: Plage
    sources: Annotated[list[Identifiant], Field(min_length=1)]
    justification: Texte
    instruments: Annotated[list[Identifiant], Field(min_length=1)]

    @model_validator(mode="after")
    def plage_encadre_la_valeur_centrale(self) -> Self:
        if not self.plage.basse <= self.valeur_centrale <= self.plage.haute:
            msg = f"{self.id} : la plage doit vérifier basse ≤ centrale ≤ haute"
            raise ValueError(msg)
        return self


class Moteur(StrEnum):
    OPENFISCA = "openfisca"
    AGREGE = "agrege"
    OPENFISCA_ET_AGREGE = "openfisca_et_agrege"
    STRUCTUREL = "structurel"


class Statut(StrEnum):
    VALIDE = "valide"
    BETA = "beta"
    NON_PUBLIE = "non_publie"


class Levier(Strict):
    """Entité « lever » : levier paramétrique et son statut de validation."""

    id: Identifiant
    libelle: Texte
    """Libellé descriptif et neutre, affiché sur le site."""
    parametres_reglables: Annotated[list[Texte], Field(min_length=1)]
    moteur: Moteur
    references_visees: Annotated[list[Texte], Field(min_length=1)]
    """Références de validation prévues par la spécification, en toutes lettres."""
    statut: Statut


class StatutRelecture(StrEnum):
    A_RELIRE = "a_relire"
    RELU = "relu"


class Chiffrage(Strict):
    """Chiffrage officiel ou académique d'un levier, saisi pour la validation."""

    id: Identifiant
    levier: Identifiant
    source: Identifiant
    millesime: Texte
    mesure: Texte
    """Mesure chiffrée, en toutes lettres (« hausse d'un point du taux normal »)."""
    valeur: float
    unite: Texte
    localisation: Texte
    """Page, tableau ou ligne du document où se trouve la valeur."""
    saisi_le: date
    relecture: StatutRelecture


class Correction(Strict):
    """Correction appliquée à OpenFisca-France (``registres/corrections_openfisca.yaml``)."""

    id: Identifiant
    type: Annotated[str, StringConstraints(pattern=r"^(parametre|variable)$")]
    libelle: Texte
    constat: Texte
    date_effet: date
    sources: Annotated[list[Identifiant], Field(min_length=1)]
    parametre: Texte | None = None
    tranche: int | None = None
    valeur: float | None = None
    terme: Identifiant | None = None
    ajouter: dict[Identifiant, int] | None = None

    @model_validator(mode="after")
    def champs_selon_le_type(self) -> Self:
        attendus = (
            {"parametre": self.parametre, "valeur": self.valeur}
            if self.type == "parametre"
            else {"terme": self.terme, "ajouter": self.ajouter}
        )
        manquants = [nom for nom, valeur in attendus.items() if valeur is None]
        if manquants:
            msg = f"{self.id} : champs manquants pour le type {self.type} : {manquants}"
            raise ValueError(msg)
        return self


class RegistreCorrections(Strict):
    openfisca_france_version: Texte
    corrections: list[Correction]
