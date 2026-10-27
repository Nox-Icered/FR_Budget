"""Comparaisons du modèle aux chiffrages de référence, pour la page Validation du site.

CLAUDE.md : « L'écart avec la référence est toujours affiché sur la page Validation, y compris
quand le modèle est moins bon. » Ce module calcule, pour chaque référence testée dans
``moteur/tests/validation/``, la valeur du modèle, la référence et l'écart relatif, avec les
mêmes fonctions et les mêmes paramètres que les tests (qui restent la vérification
exécutée par la CI).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from fr_budget import retraites_cohortes
from fr_budget.agrege.accises import recette_brute
from fr_budget.agrege.cotisations import cout_allegements, valeur_point_modele
from fr_budget.agrege.credits_missions import total_execution
from fr_budget.agrege.csg import (
    ACTIVITE,
    CAPITAL,
    RETRAITES,
    hausse_mesuree,
    rendement_taux_plein,
    valeur_point,
)
from fr_budget.agrege.depenses_fiscales import cout_par_impot
from fr_budget.agrege.dotations import COMPENSATIONS, DGF, execution
from fr_budget.agrege.impot_revenu import rendement_gel
from fr_budget.agrege.impot_societes import is_brut
from fr_budget.agrege.indexation import (
    AAH,
    BLOCS,
    BRUT,
    FAMILLE,
    NET_PRELEVEMENTS_SOCIAUX,
    PENSIONS,
    cout_mesure,
)
from fr_budget.agrege.prime_activite import economie_baisse_2025
from fr_budget.agrege.remunerations import VERSANTS, cout_brut_point_mesure
from fr_budget.agrege.tva import estimer_point_tva, estimer_recette_totale
from fr_budget.dette import surcout_choc_taux_etat
from fr_budget.registres.acces import chiffrage
from fr_budget.retraites import effet_a_horizon

TOLERANCE_PUBLICATION = 0.10
"""Règle de publication d'un levier (CLAUDE.md) : ±10 % sur le rendement à 1 an."""

MILLIONS_PAR_MILLIARD = 1000.0
EUROS_PAR_MILLIARD = 1e9
IMPOTS_DEPENSES_FISCALES = ("impot_revenu", "impot_revenu_et_societes", "impot_societes")
POURCENT = 100.0
TAUX_TVA = ("ensemble", "taux_2_1", "taux_5_5", "taux_10", "taux_20")


@dataclass(frozen=True)
class Comparaison:
    reference: str
    """Identifiant du chiffrage (registres/references/chiffrages.yaml)."""
    modele: float
    valeur_reference: float
    ecart: float
    """Écart relatif (modèle - référence) / référence."""
    tolerance: float
    variante: str = ""
    """Modèle comparé quand plusieurs modèles répondent à la même référence (``cohortes`` :
    retraites, modèle par cohortes) ; vide sinon."""

    @property
    def dans_la_tolerance(self) -> bool:
        return abs(self.ecart) <= self.tolerance


def comparer(
    reference: str, modele: float, tolerance: float = TOLERANCE_PUBLICATION, variante: str = ""
) -> Comparaison:
    valeur = chiffrage(reference)
    return Comparaison(reference, modele, valeur, (modele - valeur) / valeur, tolerance, variante)


def _point_tva(annee_comptes: int, annee_cible: int, nature: str, taux: str) -> float:
    point = estimer_point_tva(annee_comptes, annee_cible)
    return (point.brut if nature == "brut" else point.net)[taux]


def _choc_taux_premiere_annee() -> float:
    return surcout_choc_taux_etat(annee=1).central


def _choc_taux_cinquieme_annee() -> float:
    return surcout_choc_taux_etat(annee=5).central


def _cout_prevu(plf: int, annee: int, impot: str) -> float:
    return cout_par_impot(plf, annee)[impot]


def _cout_total_prevu(plf: int, annee: int) -> float:
    """Coût total de toutes les dépenses fiscales prévu par un PLF, en Md€."""
    return sum(cout_par_impot(plf, annee).values()) / MILLIONS_PAR_MILLIARD


def _credits_votes(exercice: int) -> float:
    """Crédits votés en LFI des missions du levier « crédits par mission », en Md€."""
    return total_execution(exercice)[0] / EUROS_PAR_MILLIARD


def _dotation_votee(dotation: str, annee: int) -> float:
    """Montant voté en LFI d'une dotation du levier, en M€ (unité des références)."""
    return execution(dotation, annee).lfi * MILLIONS_PAR_MILLIARD


def _cout_point(taux: float, annee: int, versant: str) -> float:
    """Coût brut d'une hausse du point d'indice en année pleine, en Md€ (total ou versant)."""
    versants = list(VERSANTS) if versant == "total" else [versant]
    return sum(cout_brut_point_mesure(v, taux, annee) for v in versants)


def _indexation(taux: float | str, annee: int, blocs: tuple[str, ...]) -> float:
    """Rendement en première année d'un gel ou d'une sous-indexation, net des prélèvements
    sociaux, en Md€. ``taux`` : écart de revalorisation, ou chiffrage de l'inflation évitée (%)."""
    ecart = taux if isinstance(taux, float) else chiffrage(taux) / POURCENT
    return cout_mesure(ecart, annee, blocs, NET_PRELEVEMENTS_SOCIAUX)


def _csg_millions(assiette: str, points: float, annee: int) -> float:
    """Rendement d'une hausse de CSG, en M€ (unité des références de la CCSS)."""
    return hausse_mesuree(assiette, points, annee) * MILLIONS_PAR_MILLIARD


def _indexation_millions(taux: float | str, annee: int, blocs: tuple[str, ...]) -> float:
    return _indexation(taux, annee, blocs) * MILLIONS_PAR_MILLIARD


def _pa_pente_millions() -> float:
    return economie_baisse_2025() * MILLIONS_PAR_MILLIARD


def _ir_gel(inflation: str, annee: int) -> float:
    return rendement_gel(chiffrage(inflation), annee)


def _point_cotisation_millions(annee: int) -> float:
    return valeur_point_modele(annee) * MILLIONS_PAR_MILLIARD


def _csg_point_millions(assiette: str, annee: int) -> float:
    return valeur_point(assiette, annee) * MILLIONS_PAR_MILLIARD


def _csg_taux_plein_millions(annee: int) -> float:
    return rendement_taux_plein(annee) * MILLIONS_PAR_MILLIARD


def _definitions() -> list[tuple[str, Callable[[], float]]]:
    definitions: list[tuple[str, Callable[[], float]]] = []
    for taux in TAUX_TVA:
        definitions += [
            (f"tva_point_brut_2025_{taux}", partial(_point_tva, 2022, 2025, "brut", taux)),
            (f"tva_point_net_2025_{taux}", partial(_point_tva, 2022, 2025, "net", taux)),
            (f"tva_point_brut_2015_{taux}", partial(_point_tva, 2015, 2015, "brut", taux)),
        ]
    definitions += [
        ("tva_nette_totale_2022_dgtresor", partial(estimer_recette_totale, 2022)),
        ("tva_nette_totale_execution_2024", partial(estimer_recette_totale, 2024)),
        ("dette_etat_choc_taux_100pb_an_1", _choc_taux_premiere_annee),
        ("dette_etat_choc_taux_100pb_an_5", _choc_taux_cinquieme_annee),
        ("accises_ticpe_brute_totale_2023", partial(recette_brute, 2023)),
        ("accises_ticpe_brute_totale_2024", partial(recette_brute, 2024)),
        ("is_brut_2024_dgfip", partial(is_brut, 2024)),
        ("is_brut_2025_dgfip", partial(is_brut, 2025)),
    ]
    for plf, annee in ((2024, 2023), (2025, 2024)):
        definitions += [
            (
                f"depenses_fiscales_{impot}_realisation_{annee}",
                partial(_cout_prevu, plf, annee, impot),
            )
            for impot in IMPOTS_DEPENSES_FISCALES
        ]
    definitions += [
        ("depenses_fiscales_ccomptes_total_2024_revise", partial(_cout_total_prevu, 2024, 2024)),
        ("depenses_fiscales_ccomptes_total_2023_definitif", partial(_cout_total_prevu, 2024, 2023)),
    ]
    definitions += [
        (f"credits_missions_depenses_constatees_{exercice}", partial(_credits_votes, exercice))
        for exercice in (2023, 2024, 2025)
    ]
    definitions += [
        (f"dotations_{dotation}_execution_{annee}", partial(_dotation_votee, dotation, annee))
        for dotation in (DGF, COMPENSATIONS)
        for annee in (2023, 2024)
    ]
    definitions += [
        (
            f"remunerations_point_{mesure}_{versant}_{annee}",
            partial(_cout_point, taux, annee, versant),
        )
        for mesure, taux, annee in (("3_5", 0.035, 2023), ("1_5", 0.015, 2024))
        for versant in (*VERSANTS, "total")
    ]
    inflation_2025 = "indexation_inflation_hors_tabac_2025_plfss2026"
    inflation_2026 = "indexation_inflation_hors_tabac_2026_plfss2027"
    definitions += [
        ("indexation_gel_2026_apu", partial(_indexation, inflation_2025, 2026, tuple(BLOCS))),
        ("indexation_gel_2026_familiales", partial(_indexation, inflation_2025, 2026, (FAMILLE,))),
        ("indexation_sous_indexation_0_5_2027", partial(_indexation, 0.005, 2027, (PENSIONS,))),
        ("indexation_gel_familiales_2027", partial(_indexation, inflation_2026, 2027, (FAMILLE,))),
        ("indexation_gel_aah_2026", partial(_indexation_millions, inflation_2025, 2026, (AAH,))),
        (
            "indexation_pensions_gel_2026_hcfp",
            lambda: _gel_pensions_brut(chiffrage(inflation_2025), 2026),
        ),
    ]
    definitions += [
        ("csg_hausse_1_7_2018_activite", partial(_csg_millions, ACTIVITE, 1.7, 2018)),
        ("csg_hausse_1_7_2018_retraites", partial(_csg_millions, RETRAITES, 1.7, 2018)),
        ("csg_hausse_1_7_2018_capital", partial(hausse_mesuree, CAPITAL, 1.7, 2018)),
        ("csg_hausse_capital_1_4_2026", partial(hausse_mesuree, CAPITAL, 1.4, 2026)),
        ("csg_rendement_retraites_taux_plein_2017", partial(_csg_taux_plein_millions, 2017)),
    ]
    definitions += [
        (f"csg_valeur_point_{assiette}_{annee}", partial(_csg_point_millions, assiette, annee))
        for assiette in (ACTIVITE, CAPITAL)
        for annee in (2025, 2027)
    ]
    definitions += [
        (f"cotisations_point_prive_{annee}", partial(_point_cotisation_millions, annee))
        for annee in (2025, 2017)
    ]
    definitions += [
        (f"allegements_generaux_prevision_{annee}", partial(cout_allegements, annee))
        for annee in (2024, 2025)
    ]
    definitions += [("ir_gel_bareme_2026", partial(_ir_gel, inflation_2025, 2026))]
    definitions += [("pa_pente_moindre_depense_2025", _pa_pente_millions)]
    definitions += [
        (f"cor_aod_un_an_solde_apu_{horizon}ans_{borne}", partial(effet_a_horizon, horizon, 2027))
        for horizon in (2, 10, 20)
        for borne in ("bas", "haut")
    ]
    definitions += _confrontations_independantes()
    return definitions


COHORTES = "cohortes"
ENTREE_RETRAITES = 2027


def _retraites_cohortes(horizon: int) -> float:
    """Effet central d'un an d'âge légal (modèle par cohortes) la ``horizon``-ième année."""
    return retraites_cohortes.effet(1.0, ENTREE_RETRAITES + horizon - 1, ENTREE_RETRAITES).central


def definitions_variantes() -> list[tuple[str, Callable[[], float], str]]:
    """Références déjà comparées à un modèle, comparées aussi à une variante : le tableau 2.10
    du COR (âge d'ouverture des droits) au modèle de retraites par cohortes."""
    return [
        (
            f"cor_aod_un_an_solde_apu_{horizon}ans_{borne}",
            partial(_retraites_cohortes, horizon),
            COHORTES,
        )
        for horizon in (2, 10, 20)
        for borne in ("bas", "haut")
    ]


def _gel_pensions_brut(inflation: float, annee: int) -> float:
    """Baisse de dépenses brute d'un gel des pensions de base, en Md€ (``inflation`` en %)."""
    return cout_mesure(inflation / POURCENT, annee, (PENSIONS,), BRUT)


def _confrontations_independantes() -> list[tuple[str, Callable[[], float]]]:
    """Références de sources indépendantes de l'administration (``independante: true`` dans
    ``registres/references/chiffrages.yaml``). Mêmes mesures, modèle à l'année de la source."""
    return [
        (
            "tva_point_brut_ipp_2025_quatre_taux",
            partial(_point_tva, 2022, 2025, "brut", "ensemble"),
        ),
        ("tva_point_net_ipp_2025_quatre_taux", partial(_point_tva, 2022, 2025, "net", "ensemble")),
        ("ir_gel_ipp_inflation_1_0_2026", partial(rendement_gel, 1.0, 2026)),
        ("ir_gel_ipp_inflation_1_3_2026", partial(rendement_gel, 1.3, 2026)),
        ("ir_gel_ofce_2026", partial(rendement_gel, 1.1, 2026)),
        ("indexation_pensions_ipp_inflation_1_0_2026", partial(_gel_pensions_brut, 1.0, 2026)),
        ("indexation_pensions_ipp_inflation_1_3_2026", partial(_gel_pensions_brut, 1.3, 2026)),
        *[
            (
                f"remunerations_point_1_ccomptes_2017_{versant}",
                partial(_cout_point, 0.01, 2017, versant),
            )
            for versant in ("total", *VERSANTS)
        ],
        ("remunerations_point_1_fipeco_2026_total", partial(_cout_point, 0.01, 2025, "total")),
    ]


def comparaisons() -> list[Comparaison]:
    """Toutes les comparaisons modèle-référence, dans l'ordre des tests de validation."""
    return [comparer(reference, calcul()) for reference, calcul in _definitions()] + [
        comparer(reference, calcul(), variante=variante)
        for reference, calcul, variante in definitions_variantes()
    ]


def tableau_markdown(liste: list[Comparaison]) -> str:
    """Tableau des écarts, publié par la CI dans le résumé de chaque exécution."""
    hors = sum(not c.dans_la_tolerance for c in liste)
    lignes = [
        f"## Écarts aux références : {len(liste) - hors} sur {len(liste)} dans la tolérance",
        "",
        "| Référence | Modèle | Référence | Écart | Résultat |",
        "|---|---|---|---|---|",
    ]
    for c in liste:
        resultat = "dans la tolérance" if c.dans_la_tolerance else "**hors tolérance**"
        lignes.append(
            f"| {c.reference}{f' ({c.variante})' if c.variante else ''} | {c.modele:.3f} "
            f"| {c.valeur_reference:.3f} | {c.ecart:+.1%} "
            f"(±{c.tolerance:.0%}) | {resultat} |"
        )
    return "\n".join(lignes) + "\n"


if __name__ == "__main__":
    print(tableau_markdown(comparaisons()))
