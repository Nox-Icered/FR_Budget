"""Où va l'écart entre le coût employeur et le revenu après impôt d'un ménage type.

Décomposition en étapes, chacune équilibrée (ce qui entre en ressort) :

1. ``employeur`` : coût employeur et allègements de cotisations patronales, puis salaire brut et
   cotisations patronales avant allègements, par risque ;
2. ``salarie`` : salaire brut (et exonérations de cotisations salariales de l'apprenti), puis
   salaire net, cotisations salariales, CSG et CRDS ;
3. ``retraite`` : pension brute, puis pension nette, CSG, CRDS et CASA ;
4. ``independant`` : revenu brut de l'indépendant, puis cotisations, CSG-CRDS et revenu net ;
5. ``impot`` : revenus nets et prestations, puis impôt sur le revenu et revenu après impôt.

Lecture comptable : chaque prélèvement est attribué à celui qui le verse (employeur ou
salarié). Aucun chiffre nouveau : tous les montants sont des variables d'OpenFisca-France
(176.1.2) calculées pour la cascade des ménages types (``fr_budget.menages.types``). Les
regroupements par risque suivent la formule de ``cotisations_employeur`` d'OpenFisca-France
(``openfisca_france/model/prelevements_obligatoires/prelevements_sociaux/cotisations_sociales/
travail_prive.py``) ; « autres » reçoit le reste (APEC, prévoyance des cadres, dialogue
social…), qui est vérifié positif.

Allègements : la différence entre les cotisations patronales au taux plein (``mmid_employeur``,
``famille``) et au taux réduit (``*_net_allegement``), l'allègement général
(``allegement_general``) et les exonérations (``exonerations``, apprentis). Ces montants ne sont
pas versés par l'employeur ; l'État en compense l'essentiel à la Sécurité sociale.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from functools import cache

from openfisca_core.simulations import Simulation

from fr_budget.menages import types

PATRONALES: dict[str, tuple[str, ...]] = {
    "retraite_base": ("vieillesse_plafonnee_employeur", "vieillesse_deplafonnee_employeur"),
    "retraite_complementaire": (
        "agirc_arrco_employeur",
        "contribution_equilibre_general_employeur",
        "contribution_equilibre_technique_employeur",
    ),
    "maladie": ("mmid_employeur",),
    "famille": ("famille",),
    "accidents_travail": ("accident_du_travail",),
    "chomage": ("chomage_employeur", "ags"),
    "autonomie": ("contribution_solidarite_autonomie",),
    "formation": (
        "contribution_unique_formation_professionnelle_alternance",
        "contribution_supplementaire_apprentissage",
        "contribution_developpement_apprentissage",
        "conge_individuel_formation_cdd",
    ),
    "logement": ("fnal", "participation_effort_construction"),
    "transport": ("versement_transport",),
}
"""Cotisations patronales au taux plein, par risque (variables OpenFisca, montants négatifs)."""

ALLEGEMENTS_TAUX = (
    ("mmid_employeur", "mmid_employeur_net_allegement"),
    ("famille", "famille_net_allegement"),
)
"""Cotisation au taux plein et au taux réduit (allègement de taux maladie et famille)."""

SALARIALES: dict[str, tuple[str, ...]] = {
    "retraite_base": ("vieillesse_plafonnee_salarie", "vieillesse_deplafonnee_salarie"),
    "retraite_complementaire": (
        "agirc_arrco_salarie",
        "contribution_equilibre_general_salarie",
        "contribution_equilibre_technique_salarie",
    ),
}
EXONERATIONS_SALARIALES = (
    "exoneration_cotisations_salariales_apprenti",
    "exoneration_cotisations_salarie_stagiaire",
)
DEMI_CENTIME = 0.005
"""Montant en dessous duquel une ligne nulle est omise, en euros."""
RESTE_ADMIS = -0.05
"""Arrondi admis sur le reste « autres », en euros par an."""


@dataclass(frozen=True)
class Etape:
    """Une étape de la décomposition, en euros par an (montants positifs)."""

    id: str
    entrees: dict[str, float]
    sorties: dict[str, float]


def _positifs(montants: dict[str, float]) -> dict[str, float]:
    return {k: v for k, v in montants.items() if v > DEMI_CENTIME}


def _reste(total: float, parties: dict[str, float], quoi: str) -> float:
    reste = total - sum(parties.values())
    if reste < RESTE_ADMIS:
        msg = f"{quoi} : reste négatif ({reste:.2f} €), regroupement à revoir"
        raise ValueError(msg)
    return reste


def _total(simulation: Simulation, annee: int):  # type: ignore[no-untyped-def]
    mois = types._mois(annee)

    def total(variable: str) -> float:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            return float(sum(simulation.calculate(variable, m).sum() for m in mois))

    return total


def _employeur(total, c: types.CascadeMenage) -> Etape:  # type: ignore[no-untyped-def]
    brutes = {k: -sum(total(v) for v in vs) for k, vs in PATRONALES.items()}
    nettes_taux = sum(total(net) - total(plein) for plein, net in ALLEGEMENTS_TAUX)
    toutes = -total("cotisations_employeur") + nettes_taux
    brutes["autres"] = _reste(toutes, brutes, "cotisations patronales")
    allegements = nettes_taux + total("allegement_general") + total("exonerations")
    return Etape(
        "employeur",
        _positifs({"cout_employeur": c.cout_employeur, "allegements": allegements}),
        _positifs({"salaire_brut": c.salaire_brut, **brutes}),
    )


def _salarie(total, c: types.CascadeMenage) -> Etape:  # type: ignore[no-untyped-def]
    exonerations = sum(total(v) for v in EXONERATIONS_SALARIALES)
    brutes = {k: -sum(total(v) for v in vs) for k, vs in SALARIALES.items()}
    toutes = -total("cotisations_salariales") + exonerations
    brutes["autres"] = _reste(toutes, brutes, "cotisations salariales")
    return Etape(
        "salarie",
        _positifs({"salaire_brut": c.salaire_brut, "exonerations_salariales": exonerations}),
        _positifs(
            {
                "net_avant_impot": c.net_avant_impot,
                **brutes,
                "csg_deductible": -total("csg_deductible_salaire"),
                "csg_non_deductible": -total("csg_imposable_salaire"),
                "crds": -total("crds_salaire"),
            }
        ),
    )


def _retraite(total, c: types.CascadeMenage) -> Etape:  # type: ignore[no-untyped-def]
    return Etape(
        "retraite",
        {"pension_brute": c.pension_brute},
        _positifs(
            {
                "pension_nette": c.pension_nette,
                "csg_deductible": -total("csg_deductible_retraite"),
                "csg_non_deductible": -total("csg_imposable_retraite"),
                "crds": -total("crds_retraite"),
                "casa": -total("casa"),
            }
        ),
    )


def _independant(c: types.CascadeMenage) -> Etape:
    return Etape(
        "independant",
        {"revenu_independant_brut": c.revenu_independant_brut},
        _positifs(
            {
                "revenu_independant_net": c.revenu_independant_net,
                "cotisations_independant": c.cotisations_independant,
                "csg_crds_independant": c.csg_crds_independant,
            }
        ),
    )


def _impot(c: types.CascadeMenage) -> Etape:
    entrees = {
        "net_avant_impot": c.net_avant_impot,
        "pension_nette": c.pension_nette,
        "revenu_independant_net": c.revenu_independant_net,
        **{f"prestation_{k}": v for k, v in c.prestations.items()},
        "restitution_impot": -c.impot_revenu,
    }
    return Etape(
        "impot",
        _positifs(entrees),
        _positifs({"impot_revenu": c.impot_revenu, "net_apres_impot": c.net_apres_impot}),
    )


@cache
def flux_type(identifiant: str, annee: int = types.ANNEE) -> tuple[Etape, ...]:
    """Étapes de la décomposition d'un ménage type (revenu central), en euros par an."""
    c = types.cascade_annuelle(identifiant, annee)
    total = _total(types._simulation(identifiant, annee, types.CENTRAL), annee)
    etapes = []
    if c.salaire_brut:
        etapes += [_employeur(total, c), _salarie(total, c)]
    if c.pension_brute:
        etapes.append(_retraite(total, c))
    if c.revenu_independant_brut:
        etapes.append(_independant(c))
    etapes.append(_impot(c))
    return tuple(etapes)
