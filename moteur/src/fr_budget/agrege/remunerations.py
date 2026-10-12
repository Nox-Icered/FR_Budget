"""Rémunérations publiques : point d'indice et effectifs (lot 2.7).

Données :

- rémunération des salariés (D1) et cotisations sociales imputées (D122) par sous-secteur des
  administrations publiques, comptes nationaux de l'INSEE (``fr_budget.apu``) ;
- traitement brut et primes mensuels moyens des fonctionnaires par versant et par catégorie,
  DGAFP, rapport annuel 2025, figure 9 (chiffrages ``remunerations_tib_*`` et
  ``remunerations_primes_*``) ;
- législation socio-fiscale d'OpenFisca-France (cotisations, CSG, impôt sur le revenu).

Correspondance entre versants et sous-secteurs (approximation validée par
``moteur/tests/validation/test_levier_remunerations.py``) : fonction publique de l'État et
administration publique centrale (S1311), territoriale et administrations publiques locales
(S1313), hospitalière et administrations de sécurité sociale (S1314). L'assiette est D1 moins
D122 : les cotisations imputées sont surtout la contribution de l'État employeur au compte des
pensions, un flux interne à l'État.

Coût brut d'une hausse de x % du point d'indice, par versant :

    x % * (D1 - D122) * traitement brut / salaire brut (fonctionnaires, DGAFP)

Coût net pour les administrations publiques (décision du mainteneur du 12 octobre 2026,
option 2 (a)) : les cotisations patronales et salariales, la CSG et la CRDS reviennent aux
administrations publiques ; l'impôt sur le revenu aussi. Seule la hausse du revenu après impôt
des agents est une dépense nette : le coût brut est multiplié par la part qui reste à l'agent,
calculée avec OpenFisca pour un fonctionnaire célibataire sans enfant, au traitement et aux
primes moyens de la DGAFP (valeur centrale : ensemble des fonctionnaires ; fourchette :
catégories A, B et C). Pour l'État, la contribution au compte des pensions est retirée du coût,
comme dans l'assiette.

Effectifs : une variation de x % des effectifs change de x % la masse D1 - D122 de chaque
sous-secteur ; coût net : même méthode, sur le traitement et les primes.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from functools import cache
from typing import Any

from openfisca_core.simulation_builder import SimulationBuilder

from fr_budget.apu import comptes_apu
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage

VERSANTS = {"fpe": "S1311", "fpt": "S1313", "fph": "S1314"}
CATEGORIES_OPENFISCA = {
    "fpe": "public_titulaire_etat",
    "fpt": "public_titulaire_territoriale",
    "fph": "public_titulaire_hospitaliere",
}
CATEGORIES = ("a", "b", "c")
ENSEMBLE = "ensemble"
ANNEE_MASSE = 2025
ANNEE_LEGISLATION = 2025
MOIS_PAR_AN = 12
POURCENT = 100.0
POINT = "point"
EFFECTIFS = "effectifs"


def masse(versant: str, annee: int = ANNEE_MASSE) -> float:
    """Rémunération des salariés hors cotisations imputées (D1 - D122), en Md€."""
    c = comptes_apu()
    secteur = VERSANTS[versant]
    return c.valeur(annee, secteur, "remuneration_salaries") - c.valeur(
        annee, secteur, "cotisations_sociales_imputees"
    )


def traitement_et_primes(versant: str, categorie: str = ENSEMBLE) -> tuple[float, float]:
    """Traitement brut et primes mensuels moyens en EQTP des fonctionnaires (DGAFP, 2023)."""
    return (
        chiffrage(f"remunerations_tib_{versant}_{categorie}"),
        chiffrage(f"remunerations_primes_{versant}_{categorie}"),
    )


def part_indiciaire(versant: str) -> float:
    """Part du traitement brut dans le salaire brut des fonctionnaires du versant."""
    tib, primes = traitement_et_primes(versant)
    return tib / (tib + primes)


def cout_brut_point(versant: str, taux: float, annee: int = ANNEE_MASSE) -> float:
    """Coût brut d'une hausse de ``taux`` (fraction) du point, sur la masse de ``annee``, Md€."""
    return taux * masse(versant, annee) * part_indiciaire(versant)


def cout_brut_point_mesure(versant: str, taux: float, annee: int) -> float:
    """Coût en année pleine d'une hausse déjà incluse dans la masse de ``annee``, en Md€.

    Sert à la validation : la masse de la première année pleine contient déjà la hausse.
    """
    return cout_brut_point(versant, taux / (1 + taux), annee)


@dataclass(frozen=True)
class Agent:
    cout: float
    """Coût annuel pour l'employeur, hors contribution au compte des pensions de l'État."""
    revenu_apres_impot: float
    """Salaire net à payer moins l'impôt sur le revenu, sur l'année."""


@cache
def agent(versant: str, tib: float, primes: float) -> Agent:
    """Fonctionnaire célibataire sans enfant, à temps plein toute l'année (OpenFisca)."""
    mois = [f"{ANNEE_LEGISLATION}-{m:02d}" for m in range(1, MOIS_PAR_AN + 1)]
    individu: dict[str, Any] = {
        "traitement_indiciaire_brut": dict.fromkeys(mois, tib),
        "primes_fonction_publique": dict.fromkeys(mois, primes),
        "categorie_salarie": dict.fromkeys(mois, CATEGORIES_OPENFISCA[versant]),
    }
    situation = {
        "individus": {"agent": individu},
        "foyers_fiscaux": {"foyer": {"declarants": ["agent"]}},
        "familles": {"famille": {"parents": ["agent"]}},
        "menages": {"menage": {"personne_de_reference": ["agent"]}},
    }
    simulation = SimulationBuilder().build_from_entities(systeme_socio_fiscal(), situation)
    with warnings.catch_warnings():
        # Avertissements numpy neutralisés par OpenFisca lui-même (divisions par zéro).
        warnings.simplefilter("ignore", RuntimeWarning)
        cout = sum(float(simulation.calculate("salaire_super_brut", m)[0]) for m in mois)
        if versant == "fpe":
            # « pension_employeur » est négatif : l'ajouter retire la contribution au CAS.
            cout += sum(float(simulation.calculate("pension_employeur", m)[0]) for m in mois)
        net = sum(float(simulation.calculate("salaire_net_a_payer", m)[0]) for m in mois)
        # « impot_revenu_restant_a_payer » est négatif quand l'impôt est dû.
        impot = float(
            simulation.calculate("impot_revenu_restant_a_payer", str(ANNEE_LEGISLATION))[0]
        )
    return Agent(cout=cout, revenu_apres_impot=net + impot)


HAUSSE_TEST = 0.01


def part_restant_a_l_agent(versant: str, categorie: str, assiette: str) -> float:
    """Part d'une hausse du coût employeur qui reste à l'agent après prélèvements.

    ``assiette`` : « point » (hausse de 1 % du traitement) ou « effectifs » (agent entier).
    """
    tib, primes = traitement_et_primes(versant, categorie)
    base = agent(versant, tib, primes)
    if assiette == EFFECTIFS:
        return base.revenu_apres_impot / base.cout
    hausse = agent(versant, tib * (1 + HAUSSE_TEST), primes)
    return (hausse.revenu_apres_impot - base.revenu_apres_impot) / (hausse.cout - base.cout)


def _parts(versant: str, assiette: str) -> tuple[float, list[float]]:
    centrale = part_restant_a_l_agent(versant, ENSEMBLE, assiette)
    return centrale, [part_restant_a_l_agent(versant, c, assiette) for c in CATEGORIES]


def cout_net_un_pourcent(levier: str) -> Fourchette:
    """Coût net pour les administrations publiques d'une hausse de 1 %, en Md€ de 2025.

    ``levier`` : « point » ou « effectifs ». Fourchette : part restant à l'agent des
    catégories A, B et C (bornes) et de l'ensemble des fonctionnaires (valeur centrale).
    """
    central = 0.0
    bornes = [0.0, 0.0]
    for versant in VERSANTS:
        brut = cout_brut_un_pourcent(levier, versant)
        c, autres = _parts(versant, levier)
        central += brut * c
        bornes[0] += brut * min([*autres, c])
        bornes[1] += brut * max([*autres, c])
    return encadrer(central, bornes)


def cout_brut_un_pourcent(levier: str, versant: str | None = None) -> float:
    """Coût brut d'une hausse de 1 % (point ou effectifs), en Md€ de 2025."""
    versants = [versant] if versant else list(VERSANTS)
    if levier == POINT:
        return sum(cout_brut_point(v, 1 / POURCENT) for v in versants)
    return sum(masse(v) / POURCENT for v in versants)
