"""Prestations mensuelles des ménages types, pour la validation contre les barèmes publiés et
le simulateur officiel du RSA et de la prime d'activité (``docs/fiches/menages_types.md``, § 6).

Le simulateur de mesdroitssociaux.gouv.fr (source ``mesdroitssociaux_simulateur_rsa_pa``)
applique la législation du jour et demande les ressources des quatre derniers mois, ainsi
qu'un logement. Les cas de validation sont donc calculés :

- avec la législation de ``ANNEE_SIMULATEUR`` (situation des ménages types pour cette année) ;
- avec les salaires imposables des mois ``MOIS_RESSOURCES``, arrondis à l'euro comme dans le
  formulaire ;
- avec un logement loué vide (``LOGEMENT``), que les ménages types n'ont pas par ailleurs.

Le montant comparé est celui de ``MOIS_RESULTAT``, premier mois qui suit les ressources
déclarées. Les prestations familiales versées sont déclarées nettes de la CRDS (paramètre
OpenFisca ``prelevements_sociaux.contributions_sociales.crds``), arrondies à l'euro.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from functools import cache
from typing import Any

from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_core.simulations import Simulation

from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.menages.types import PROFILS, situation

ANNEE_SIMULATEUR = 2026
MOIS_RESSOURCES = ("2026-06", "2026-07", "2026-08", "2026-09")
MOIS_RESULTAT = "2026-10"
PROFILS_AVEC_PRESTATIONS = ("celibataire_smic", "parent_isole_1_enfant", "couple_2_enfants")
PRESTATIONS_DECLAREES = ("asf", "af")
"""Prestations versées que le simulateur demande comme « autres ressources »."""


@dataclass(frozen=True)
class Logement:
    """Logement loué vide, choisi pour la validation (non fixé par la spécification)."""

    code_postal: str
    depcom: str
    """Code commune (Paris 11e arrondissement, rattaché à Paris dans la table des communes
    d'OpenFisca ``assets/apl/commune_depcom_by_subcommune_depcom.json``)."""
    loyer: float
    """Loyer mensuel hors charges, en euros."""


LOGEMENT = Logement(code_postal="75011", depcom="75111", loyer=700)


def situation_logee(identifiant: str, logement: Logement = LOGEMENT) -> dict[str, Any]:
    """Situation OpenFisca du ménage type pour ``ANNEE_SIMULATEUR``, avec le logement."""
    sit = situation(PROFILS[identifiant], ANNEE_SIMULATEUR)
    mois = [f"{ANNEE_SIMULATEUR - 1}-{m:02d}" for m in range(1, 13)]
    mois += [f"{ANNEE_SIMULATEUR}-{m:02d}" for m in range(1, 13)]
    sit["menages"]["menage"] |= {
        "statut_occupation_logement": dict.fromkeys(mois, "locataire_vide"),
        "loyer": dict.fromkeys(mois, logement.loyer),
        "depcom": dict.fromkeys(mois, logement.depcom),
    }
    return sit


@cache
def _simulation(identifiant: str) -> Simulation:
    return SimulationBuilder().build_from_entities(
        systeme_socio_fiscal(), situation_logee(identifiant)
    )


def calcul(identifiant: str, variable: str, periode: str) -> list[float]:
    """Valeurs d'une variable OpenFisca pour le ménage type logé (une par entité)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return [float(v) for v in _simulation(identifiant).calculate(variable, periode)]


def taux_crds(periode: str) -> float:
    """Taux de la CRDS (paramètre OpenFisca) au premier jour de ``periode`` (AAAA-MM)."""
    crds = systeme_socio_fiscal().parameters.prelevements_sociaux.contributions_sociales.crds
    return float(crds(f"{periode}-01"))


def cas_simulateur(identifiant: str) -> dict[str, Any]:
    """Saisie du ménage type dans le simulateur : salaires imposables par adulte et par mois
    (arrondis à l'euro), enfants, prestations versées nettes de CRDS, logement."""
    profil = PROFILS[identifiant]
    salaires = [calcul(identifiant, "salaire_imposable", m) for m in MOIS_RESSOURCES]
    adultes = [
        {
            "naissance": a.naissance,
            "salaires": [round(salaires[k][i]) for k in range(len(MOIS_RESSOURCES))],
        }
        for i, a in enumerate(profil.adultes)
    ]
    autres = []
    for p in PRESTATIONS_DECLAREES:
        montants = [
            round(calcul(identifiant, p, m)[0] * (1 - taux_crds(m))) for m in MOIS_RESSOURCES
        ]
        if any(montants):
            autres.append({"prestation": p, "montants": montants})
    return {
        "id": identifiant,
        "mois_ressources": list(MOIS_RESSOURCES),
        "mois_resultat": MOIS_RESULTAT,
        "couple": len(profil.adultes) > 1,
        "adultes": adultes,
        "enfants": list(profil.enfants),
        "autres_ressources": autres,
        "logement": {
            "code_postal": LOGEMENT.code_postal,
            "depcom": LOGEMENT.depcom,
            "loyer": LOGEMENT.loyer,
        },
    }
