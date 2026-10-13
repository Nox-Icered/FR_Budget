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
    """Chiffrage officiel ou académique d'un levier ou d'un module, saisi pour la validation.

    Exactement l'un de ``levier`` (registre des leviers) ou ``module`` (module documenté par
    une fiche, par exemple ``dynamique_dette``).
    """

    id: Identifiant
    levier: Identifiant | None = None
    module: Identifiant | None = None
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

    @model_validator(mode="after")
    def un_levier_ou_un_module(self) -> Self:
        if (self.levier is None) == (self.module is None):
            msg = f"{self.id} : renseigner exactement l'un de levier ou module"
            raise ValueError(msg)
        return self


class UsageDepenseFiscale(StrEnum):
    REPARTITION = "repartition"
    """Répartit un produit des comptes nationaux entre taux réduits et taux normal."""
    ECART_TERRITORIAL = "ecart_territorial"
    """Écart dû aux taux particuliers d'outre-mer et de Corse, retranché de la recette."""


class RegimeReduit(StrEnum):
    SUPER_REDUIT = "super_reduit"
    REDUIT = "reduit"
    INTERMEDIAIRE = "intermediaire"


class DepenseFiscaleTva(Strict):
    """Dépense fiscale de TVA utilisée par le modèle (``registres/tva/depenses_fiscales.yaml``).

    La valeur est celle du chiffrage désigné (``registres/references/chiffrages.yaml``).
    """

    chiffrage: Identifiant
    usage: UsageDepenseFiscale
    annee: int
    """Année du chiffrage, qui fixe l'année des comptes utilisée pour la répartition."""
    produit: Texte | None = None
    """Code produit de la consommation finale (usage « repartition »)."""
    regime: RegimeReduit | None = None
    """Taux réduit concerné (usage « repartition »)."""

    @model_validator(mode="after")
    def produit_et_regime_selon_l_usage(self) -> Self:
        renseignes = self.produit is not None and self.regime is not None
        vides = self.produit is None and self.regime is None
        if self.usage == UsageDepenseFiscale.REPARTITION and not renseignes:
            msg = f"{self.chiffrage} : produit et regime obligatoires pour une répartition"
            raise ValueError(msg)
        if self.usage == UsageDepenseFiscale.ECART_TERRITORIAL and not vides:
            msg = f"{self.chiffrage} : produit et regime sans objet pour un écart territorial"
            raise ValueError(msg)
        return self


class Correction(Strict):
    """Correction appliquée à OpenFisca-France (``registres/corrections_openfisca.yaml``)."""

    id: Identifiant
    type: Annotated[str, StringConstraints(pattern=r"^(parametre|variable|formule)$")]
    libelle: Texte
    constat: Texte
    date_effet: date
    sources: Annotated[list[Identifiant], Field(min_length=1)]
    parametre: Texte | None = None
    tranche: int | None = None
    valeur: float | None = None
    terme: Identifiant | None = None
    ajouter: dict[Identifiant, int] | None = None
    valeurs: dict[Identifiant, float | date] | None = None
    """Taux et dates d'une correction de type ``formule``, lus par sa fonction Python
    (``fr_budget.menages.corrections_formules``)."""

    @model_validator(mode="after")
    def champs_selon_le_type(self) -> Self:
        attendus: dict[str, object] = {}
        if self.type == "parametre":
            attendus = {"parametre": self.parametre, "valeur": self.valeur}
        elif self.type == "variable":
            attendus = {"terme": self.terme, "ajouter": self.ajouter}
        manquants = [nom for nom, valeur in attendus.items() if valeur is None]
        if manquants:
            msg = f"{self.id} : champs manquants pour le type {self.type} : {manquants}"
            raise ValueError(msg)
        return self


class RegistreCorrections(Strict):
    openfisca_france_version: Texte
    corrections: list[Correction]


class Relecture(Strict):
    """Entité « review » : retour d'un relecteur externe, publié tel quel avec la réponse."""

    id: Identifiant
    date: date
    relecteur: Texte
    """Institution ou personne, avec son accord pour être nommée."""
    objet: Annotated[list[Identifiant], Field(min_length=1)]
    """Leviers ou modules relus (identifiants du registre des leviers ou des fiches)."""
    retour: Texte
    reponse: Texte
    lien: Texte | None = None
