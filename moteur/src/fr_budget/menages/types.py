"""Ménages types : cascade annuelle du salaire jusqu'au net après impôt et prestations.

Profils salariés de la spécification (lot « ménages types », choix à relire,
``docs/fiches/menages_types.md``) :

- niveaux de salaire : SMIC à temps plein ; salaire net médian et 95e centile du secteur privé
  en équivalent temps plein (Insee Première n° 2079, 2024), portés à l'année simulée en gardant
  leur rapport au SMIC net (hypothèse ``menages_ecart_evolution_salaire_smic``) ;
- hypothèses d'emploi : celles du cas validé contre le modèle Urssaf (effectif, taux AT/MP,
  sans mutuelle d'entreprise) ;
- année : revenus de 2025 ; l'impôt est celui dû sur ces revenus (impôt 2026), les prestations
  celles versées en 2025. Les salaires de 2024 sont supposés égaux (ressources de référence
  des prestations).

Non comptés : aides au logement (le loyer n'est pas fixé), taxe d'habitation, revenus du
patrimoine.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from functools import cache
from typing import Any

from openfisca_core.simulation_builder import SimulationBuilder

from fr_budget.menages.openfisca import HypothesesEmploi, smic_mensuel_brut, systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage, hypothese

ANNEE = 2025
ANNEE_INSEE = 2024
SMIC = "smic"
MEDIAN = "median"
P95 = "p95"
HYPOTHESE_EVOLUTION = "menages_ecart_evolution_salaire_smic"
NIVEAUX_INSEE = {MEDIAN: "insee_salaire_net_median_2024", P95: "insee_salaire_net_p95_2024"}
# Hypothèses d'emploi du cas validé contre le modèle Urssaf (valeurs par défaut du modèle,
# registres/references/menages/urssaf_modele_social.json), sans mutuelle d'entreprise.
EMPLOI = HypothesesEmploi(
    effectif_entreprise=4,
    taux_accident_travail=0.0208,
    mutuelle_montant_mensuel=0.0,
    mutuelle_part_employeur=0.5,
)
CADRE = "prive_cadre"
MOIS_REPERE = 6
PRECISION_EUROS = 0.005
ITERATIONS_MAX = 60
PRESTATIONS_MENSUELLES = ("ppa", "af", "cf", "asf", "rsa")
PRESTATIONS_ANNUELLES = ("ars",)


@dataclass(frozen=True)
class Adulte:
    naissance: str
    niveau: str
    cadre: bool = False
    """Salarié cadre (cotisations des cadres) ; sinon non cadre, valeur par défaut d'OpenFisca."""


@dataclass(frozen=True)
class Profil:
    libelle: str
    adultes: tuple[Adulte, ...]
    enfants: tuple[str, ...] = ()
    """Dates de naissance des enfants à charge."""
    parent_isole: bool = False
    """Case T de la déclaration (parent qui vit seul avec ses enfants)."""


PROFILS: dict[str, Profil] = {
    "celibataire_smic": Profil("Célibataire au SMIC", (Adulte("1995-01-01", SMIC),)),
    "celibataire_median": Profil("Célibataire, salaire médian", (Adulte("1985-01-01", MEDIAN),)),
    "cadre_p95": Profil(
        "Cadre célibataire, 95e centile des salaires", (Adulte("1980-01-01", P95, cadre=True),)
    ),
    "couple_2_enfants": Profil(
        "Couple marié, deux salaires (médian et SMIC), deux enfants",
        (Adulte("1985-01-01", MEDIAN), Adulte("1987-01-01", SMIC)),
        ("2016-03-01", "2019-03-01"),
    ),
    "parent_isole_1_enfant": Profil(
        "Parent seul au SMIC, un enfant",
        (Adulte("1990-01-01", SMIC),),
        ("2019-03-01",),
        parent_isole=True,
    ),
}


@dataclass(frozen=True)
class CascadeMenage:
    """Montants annuels du ménage, en euros."""

    cout_employeur: float
    salaire_brut: float
    net_avant_impot: float
    net_imposable: float
    impot_revenu: float
    """Impôt sur le revenu dû sur les revenus de l'année (positif)."""
    prestations: dict[str, float] = field(default_factory=dict)

    @property
    def net_apres_impot(self) -> float:
        return self.net_avant_impot - self.impot_revenu + sum(self.prestations.values())


def _mois(annee: int) -> list[str]:
    return [f"{annee}-{m:02d}" for m in range(1, 13)]


def _categorie(cadre: bool, mois: list[str]) -> dict[str, Any]:
    if not cadre:
        return {}
    return {"categorie_salarie": dict.fromkeys(mois, CADRE)}


def _salaire_net_mensuel(brut: float, mois: str, cadre: bool = False) -> float:
    """Salaire net de cotisations, CSG et CRDS (``salaire_net``), notion de l'Insee."""
    simulation = SimulationBuilder().build_from_entities(
        systeme_socio_fiscal(),
        {
            "individus": {
                "s": {"salaire_de_base": {mois: brut}, **_emploi(mois), **_categorie(cadre, [mois])}
            },
            "foyers_fiscaux": {"f": {"declarants": ["s"]}},
            "familles": {"fa": {"parents": ["s"]}},
            "menages": {"m": {"personne_de_reference": ["s"]}},
        },
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(simulation.calculate("salaire_net", mois)[0])


def _emploi(mois: str) -> dict[str, Any]:
    return _emploi_sur([mois])


def _emploi_sur(mois: list[str]) -> dict[str, Any]:
    """Hypothèses d'emploi (``EMPLOI``) pour chacun des ``mois``."""
    return {
        "effectif_entreprise": dict.fromkeys(mois, EMPLOI.effectif_entreprise),
        "taux_accident_travail": dict.fromkeys(mois, EMPLOI.taux_accident_travail),
        "complementaire_sante_montant": dict.fromkeys(mois, EMPLOI.mutuelle_montant_mensuel),
        "complementaire_sante_part_employeur": dict.fromkeys(mois, EMPLOI.mutuelle_part_employeur),
    }


def _mois_repere(annee: int) -> str:
    return f"{annee}-{MOIS_REPERE:02d}"


def brut_pour_net(net: float, mois: str, cadre: bool = False) -> float:
    """Salaire brut mensuel dont le salaire net (``salaire_net``) vaut ``net`` (dichotomie)."""
    bas, haut = net, 3 * net
    for _ in range(ITERATIONS_MAX):
        milieu = (bas + haut) / 2
        if _salaire_net_mensuel(milieu, mois, cadre) < net:
            bas = milieu
        else:
            haut = milieu
        if haut - bas < PRECISION_EUROS:
            break
    return (bas + haut) / 2


@cache
def brut_mensuel(niveau: str, annee: int = ANNEE, cadre: bool = False) -> float:
    """Salaire brut mensuel d'un niveau, pour l'année simulée.

    SMIC : SMIC brut à temps plein du mois repère. Médiane et 95e centile : salaire net de
    l'Insee (2024) multiplié par le rapport du SMIC net de l'année à celui de 2024, puis
    converti en brut avec la législation de l'année.
    """
    mois = _mois_repere(annee)
    if niveau == SMIC:
        return smic_mensuel_brut(mois)
    smic_net = _salaire_net_mensuel(smic_mensuel_brut(mois), mois)
    mois_insee = _mois_repere(ANNEE_INSEE)
    smic_net_insee = _salaire_net_mensuel(smic_mensuel_brut(mois_insee), mois_insee)
    ecart = hypothese(HYPOTHESE_EVOLUTION).valeur_centrale
    net = chiffrage(NIVEAUX_INSEE[niveau]) * smic_net / smic_net_insee * (1 + ecart)
    return brut_pour_net(net, mois, cadre)


def situation(profil: Profil, annee: int = ANNEE) -> dict[str, Any]:
    """Situation OpenFisca du ménage : salaires de l'année et de la précédente, déclaration
    commune pour un couple (marié), enfants à charge."""
    mois = _mois(annee - 1) + _mois(annee)
    individus: dict[str, Any] = {}
    adultes = []
    for i, a in enumerate(profil.adultes):
        brut = brut_mensuel(a.niveau, annee, a.cadre)
        nom = f"adulte_{i + 1}"
        adultes.append(nom)
        individus[nom] = {
            "date_naissance": {"ETERNITY": a.naissance},
            "salaire_de_base": dict.fromkeys(mois, brut),
            **_emploi_sur(mois),
            **_categorie(a.cadre, mois),
        }
        if len(profil.adultes) > 1:
            individus[nom]["statut_marital"] = dict.fromkeys(mois, "marie")
    enfants = []
    for j, naissance in enumerate(profil.enfants):
        nom = f"enfant_{j + 1}"
        enfants.append(nom)
        individus[nom] = {"date_naissance": {"ETERNITY": naissance}}
    foyer: dict[str, Any] = {"declarants": adultes, "personnes_a_charge": enfants}
    if profil.parent_isole:
        foyer["caseT"] = {str(annee): True}
    return {
        "individus": individus,
        "foyers_fiscaux": {"foyer": foyer},
        "familles": {"famille": {"parents": adultes, "enfants": enfants}},
        "menages": {
            "menage": {
                "personne_de_reference": adultes[:1],
                "conjoint": adultes[1:],
                "enfants": enfants,
            }
        },
    }


@cache
def cascade_annuelle(identifiant: str, annee: int = ANNEE) -> CascadeMenage:
    """Cascade annuelle d'un ménage type, en euros (revenus de ``annee``)."""
    profil = PROFILS[identifiant]
    simulation = SimulationBuilder().build_from_entities(
        systeme_socio_fiscal(), situation(profil, annee)
    )

    def total(variable: str, periodes: list[str]) -> float:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return float(sum(simulation.calculate(variable, p).sum() for p in periodes))

    mois = _mois(annee)
    prestations = {v: total(v, mois) for v in PRESTATIONS_MENSUELLES}
    prestations |= {v: total(v, [str(annee)]) for v in PRESTATIONS_ANNUELLES}
    return CascadeMenage(
        cout_employeur=total("salaire_super_brut", mois),
        salaire_brut=total("salaire_de_base", mois),
        net_avant_impot=total("salaire_net_a_payer", mois),
        net_imposable=total("salaire_imposable", mois),
        impot_revenu=-total("impot_revenu_restant_a_payer", [str(annee)]),
        prestations={k: v for k, v in prestations.items() if v},
    )


def declaration(identifiant: str, annee: int = ANNEE) -> dict[str, Any]:
    """Cases de la déclaration des revenus de ``annee`` pour le ménage type, au format du
    simulateur d'impots.gouv.fr (validation) : situation, années de naissance, enfants à
    charge, case T, salaires imposables arrondis à l'euro."""
    profil = PROFILS[identifiant]
    simulation = SimulationBuilder().build_from_entities(
        systeme_socio_fiscal(), situation(profil, annee)
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        salaires = sum(simulation.calculate("salaire_imposable", m) for m in _mois(annee))
    cases: dict[str, Any] = {
        "situation": "M" if len(profil.adultes) > 1 else "C",
        "0DA": profil.adultes[0].naissance[:4],
        "0CF": len(profil.enfants),
        "1AJ": round(float(salaires[0])),
    }
    if len(profil.adultes) > 1:
        cases["0DB"] = profil.adultes[1].naissance[:4]
        cases["1BJ"] = round(float(salaires[1]))
    if profil.parent_isole:
        cases["0BT"] = True
    return cases


def revenu_fiscal_et_parts(identifiant: str, annee: int = ANNEE) -> tuple[float, float]:
    """Revenu fiscal de référence (``rfr``) et nombre de parts (``nbptr``) du ménage type."""
    simulation = SimulationBuilder().build_from_entities(
        systeme_socio_fiscal(), situation(PROFILS[identifiant], annee)
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return (
            float(simulation.calculate("rfr", str(annee))[0]),
            float(simulation.calculate("nbptr", str(annee))[0]),
        )
