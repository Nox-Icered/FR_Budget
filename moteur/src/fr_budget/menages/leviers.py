"""Effet des leviers paramétriques sur les ménages types (cascade avant et après réforme).

Chaque levier qui change directement la législation d'un ménage est traduit en réforme
d'OpenFisca-France (paramètres ou formules, noms vérifiés dans le paquet installé) ; la cascade
est recalculée sous cette législation. Choix à relire (``docs/fiches/menages_types.md``, effet
des leviers) :

- la mesure s'applique à la législation et aux revenus de l'année des ménages types (2025), du
  1er janvier au 31 décembre : effet en année pleine, sans changement de comportement. Les
  paramètres de la prime d'activité, qu'OpenFisca lit aux mois des ressources, sont modifiés
  dès le 1er octobre de l'année précédente, pour que tous les droits de l'année en tiennent
  compte ;
- les revenus des années précédentes (ressources des prestations, revenu fiscal de référence)
  restent ceux de la législation de référence ;
- cotisations patronales : incidence comptable (le coût employeur change, le salaire brut non).

Leviers traduits (unité du simulateur) :

- ``csg_activite`` (points) : taux de CSG déductible des revenus d'activité (paramètre
  ``csg.activite.deductible``, et taux de l'artisan hors d'OpenFisca), comme la hausse de 2018 ;
- ``csg_retraites`` (points) : taux plein de CSG déductible des pensions
  (``csg.remplacement.pensions_retraite_invalidite.deductible.taux_plein``) ;
- ``cotisations_patronales_taux`` (points) : cotisation patronale ajoutée, assise sur
  l'assiette des cotisations, hors du champ des allègements (lecture de la CCSS) ;
- ``allegements_generaux`` (%) : réduction générale (par son taux, ``taux_allegement_general``)
  et réductions des taux maladie et famille (``allegement_cotisation_maladie``,
  ``allegement_cotisation_allocations_familiales``) multipliées par 1 + x ;
- ``ir_seuils_bareme`` (%) : limites des tranches du barème, plafonds des effets du quotient
  familial et seuils de la décote multipliés par 1 + x (champ de l'évaluation préalable de
  l'article 2 du PLF 2025, ``docs/fiches/impot_revenu.md``) ;
- ``prime_activite_pente`` (points) : fraction des revenus professionnels prise en compte
  (``ppa.pa_m.majoration_ressources_revenus_activite``) ;
- ``indexation_pensions_prestations`` (points) : base mensuelle des allocations familiales, montant
  de base du RSA et de la prime d'activité multipliés par 1 + x. La pension du retraité n'est pas
  chiffrée : le levier ne porte que sur les pensions de base, dont la part dans la pension
  moyenne de la DREES n'est pas publiée dans les sources du registre.

Les autres leviers n'ont pas d'effet direct sur la cascade de ces ménages (``SANS_EFFET``).
"""

from __future__ import annotations

import multiprocessing
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache, lru_cache
from typing import Any

from openfisca_core.periods import period as periode
from openfisca_core.reforms import Reform

from fr_budget import scenario
from fr_budget.menages import types
from fr_budget.menages.corrections import _noeud, _remplacer
from fr_budget.menages.openfisca import systeme_socio_fiscal

POURCENT = 100.0
# Caches bornés : l'API accepte toute valeur dans les bornes d'un levier.
CACHE_LEGISLATIONS = 32
CACHE_CASCADES = 512

CSG = "prelevements_sociaux.contributions_sociales.csg."
PARAMETRE_CSG_ACTIVITE = CSG + "activite.deductible"
PARAMETRE_CSG_RETRAITES = CSG + "remplacement.pensions_retraite_invalidite.deductible.taux_plein"
PARAMETRE_PENTE = (
    "prestations_sociales.solidarite_insertion.minima_sociaux.ppa.pa_m."
    "majoration_ressources_revenus_activite"
)
BAREME_IR = "impot_revenu.bareme_ir_depuis_1945.bareme"
_PLAF_QF = "impot_revenu.calcul_impot_revenu.plaf_qf."
SEUILS_IR = tuple(
    _PLAF_QF + n
    for n in (
        "plafond_avantages_procures_par_demi_part.general",
        "plafond_avantages_procures_par_demi_part.celib_enf",
        "plafond_avantages_procures_par_demi_part.celib",
        "plafond_avantages_procures_par_demi_part.reduc_postplafond",
        "plafond_avantages_procures_par_demi_part.reduc_postplafond_veuf",
        "decote.seuil_celib",
        "decote.seuil_couple",
    )
)
_MINIMA = "prestations_sociales.solidarite_insertion.minima_sociaux."
MONTANTS_INDEXES = (
    "prestations_sociales.prestations_familiales.bmaf.bmaf",
    _MINIMA + "rsa.rsa_m.montant_de_base_du_rsa",
)
MONTANT_PPA = _MINIMA + "ppa.pa_m.montant_de_base"
MOIS_RESSOURCES_PPA = 3
"""OpenFisca lit les paramètres de la prime d'activité aux mois des ressources (les trois mois
qui précèdent le droit) : modifiés trois mois plus tôt, ils s'appliquent à tous les droits de
l'année."""
# Allègements multipliés : taux de la réduction générale (en amont de la régularisation
# progressive d'OpenFisca, qui retranche les montants des mois précédents) et réductions des
# taux maladie et famille.
TAUX_REDUCTION_GENERALE = "taux_allegement_general"
ALLEGEMENTS = (
    "allegement_general",
    "allegement_cotisation_maladie",
    "allegement_cotisation_allocations_familiales",
)

Modification = Callable[[Reform, float, str], None]


def _transformer(parametre: Any, f: Callable[[float], float], debut: str) -> None:
    """Applique ``f`` aux valeurs du paramètre en vigueur à partir de ``debut`` (incluse),
    en gardant les changements de valeur postérieurs."""
    instants = sorted(
        {debut} | {v.instant_str for v in parametre.values_list if v.instant_str > debut}
    )
    valeurs = [parametre(i) for i in instants]
    for instant, valeur in zip(instants, valeurs, strict=True):
        if valeur is not None:
            parametre.update(start=periode(instant), value=f(float(valeur)))


def _modifier_parametres(
    reforme: Reform, chemins: tuple[str, ...], f: Callable[[float], float], debut: str
) -> None:
    """Ajoute une modification de paramètres à la réforme. ``Reform.modify_parameters`` repart
    des paramètres de référence à chaque appel : les modifications sont donc réunies et
    appliquées en un seul appel (``ReformeLevier.apply``)."""

    def modifier(parametres: Any) -> None:
        for chemin in chemins:
            _transformer(_noeud(parametres, chemin), f, debut)

    reforme.modifications.append(modifier)


def debut_ppa(debut: str) -> str:
    """Premier jour du troisième mois avant ``debut`` (« AAAA-MM-01 »)."""
    annee, mois = int(debut[:4]), int(debut[5:7]) - MOIS_RESSOURCES_PPA
    if mois < 1:
        annee, mois = annee - 1, mois + 12
    return f"{annee}-{mois:02d}-01"


def _points(chemin: str, ppa: bool = False) -> Modification:
    def appliquer(reforme: Reform, valeur: float, debut: str) -> None:
        depart = debut_ppa(debut) if ppa else debut
        _modifier_parametres(reforme, (chemin,), lambda v: v + valeur / POURCENT, depart)

    return appliquer


def _seuils_ir(reforme: Reform, valeur: float, debut: str) -> None:
    facteur = 1 + valeur / POURCENT

    def modifier(parametres: Any) -> None:
        for tranche in _noeud(parametres, BAREME_IR).brackets[1:]:
            _transformer(tranche.threshold, lambda v: v * facteur, debut)

    reforme.modifications.append(modifier)
    _modifier_parametres(reforme, SEUILS_IR, lambda v: v * facteur, debut)


def _indexation(reforme: Reform, valeur: float, debut: str) -> None:
    facteur = 1 + valeur / POURCENT
    _modifier_parametres(reforme, MONTANTS_INDEXES, lambda v: v * facteur, debut)
    _modifier_parametres(reforme, (MONTANT_PPA,), lambda v: v * facteur, debut_ppa(debut))


def _envelopper(
    reforme: Reform, nom: str, nouvelle: Callable[[Any, Any, Any], Any], debut: str
) -> None:
    """Remplace la formule de ``nom`` à partir de ``debut`` : ``nouvelle(individu, period,
    valeur_d_origine)``."""

    def fabrique(nom_origine: str) -> Any:
        def formule(individu: Any, period: Any) -> Any:
            valeur = individu(nom_origine, period)
            if str(period.start) < debut:
                return valeur
            return nouvelle(individu, period, valeur)

        return formule

    sans_levier, avec_levier = _remplacer(reforme, nom, fabrique, "avant_levier")
    reforme.add_variable(sans_levier)
    reforme.update_variable(avec_levier)


def _allegements(reforme: Reform, valeur: float, debut: str) -> None:
    facteur = 1 + valeur / POURCENT
    for nom in (TAUX_REDUCTION_GENERALE, *ALLEGEMENTS[1:]):
        _envelopper(reforme, nom, lambda _i, _p, v: v * facteur, debut)


def _cotisation_patronale(reforme: Reform, valeur: float, debut: str) -> None:
    taux = valeur / POURCENT

    def cout(individu: Any, period: Any, v: Any) -> Any:
        return v + taux * individu("assiette_cotisations_sociales", period)

    _envelopper(reforme, "salaire_super_brut", cout, debut)


@dataclass(frozen=True)
class LevierMenage:
    modification: Modification
    unite: str
    """« points » ou « % », comme dans le simulateur."""
    ecart_csg_independant: bool = False
    """Le levier change aussi la CSG de l'artisan (calculée hors d'OpenFisca)."""
    non_chiffre: Callable[[types.Profil], bool] = lambda _p: False
    """Profils dont l'effet n'est pas chiffré, faute de source."""


def _avec_pension(profil: types.Profil) -> bool:
    return any(a.retraite for a in profil.adultes)


LEVIERS: dict[str, LevierMenage] = {
    "csg_activite": LevierMenage(
        _points(PARAMETRE_CSG_ACTIVITE), "points", ecart_csg_independant=True
    ),
    "csg_retraites": LevierMenage(_points(PARAMETRE_CSG_RETRAITES), "points"),
    scenario.LEVIER_COTISATIONS_TAUX: LevierMenage(_cotisation_patronale, "points"),
    scenario.LEVIER_ALLEGEMENTS: LevierMenage(_allegements, "%"),
    scenario.LEVIER_IR_SEUILS: LevierMenage(_seuils_ir, "%"),
    scenario.LEVIER_PA_PENTE: LevierMenage(_points(PARAMETRE_PENTE, ppa=True), "points"),
    scenario.LEVIER_INDEXATION: LevierMenage(_indexation, "points", non_chiffre=_avec_pension),
}

# Leviers sans effet direct sur la cascade des ménages types, et la raison (clé de texte).
SANS_EFFET: dict[str, str] = {
    scenario.LEVIER_TVA_NORMAL: "consommation",
    scenario.LEVIER_ACCISE_GAZOLE: "consommation",
    scenario.LEVIER_ACCISE_ESSENCES: "consommation",
    "csg_capital": "patrimoine",
    scenario.LEVIER_IS_TAUX_NORMAL: "entreprises",
    scenario.LEVIER_IS_SURTAXE: "entreprises",
    scenario.LEVIER_DOTATIONS_DGF: "administrations",
    scenario.LEVIER_DOTATIONS_COMPENSATIONS: "administrations",
    scenario.LEVIER_POINT_INDICE: "agents_publics",
    scenario.LEVIER_EFFECTIFS: "agents_publics",
    scenario.LEVIER_RETRAITES_AGE: "structurel",
    scenario.LEVIER_DEPENSE_FISCALE_UNITE: "catalogue",
    scenario.LEVIER_CREDITS_UNITE: "administrations",
}


class ReformeLevier(Reform):  # type: ignore[misc]
    name = "Levier du simulateur FR_Budget"

    def __init__(self, systeme: Any, levier: str, valeur: float, debut: str) -> None:
        self._levier, self._valeur, self._debut = levier, valeur, debut
        self.modifications: list[Callable[[Any], None]] = []
        super().__init__(systeme)

    def apply(self) -> None:
        LEVIERS[self._levier].modification(self, self._valeur, self._debut)
        if self.modifications:

            def modifier(parametres: Any) -> Any:
                for modification in self.modifications:
                    modification(parametres)
                return parametres

            self.modify_parameters(modifier_function=modifier)


@lru_cache(maxsize=CACHE_LEGISLATIONS)
def legislation(levier: str, valeur: float, annee: int = types.ANNEE) -> types.Legislation:
    """Législation de référence modifiée par ``valeur`` (unité du levier) à partir du 1er
    janvier de ``annee``. Mise en cache : elle ne dépend d'aucune donnée saisie."""
    if levier not in LEVIERS:
        msg = f"{levier} : pas d'effet direct sur les ménages"
        raise ValueError(msg)
    definition = LEVIERS[levier]
    systeme = ReformeLevier(systeme_socio_fiscal(), levier, valeur, f"{annee}-01-01")
    ecart = valeur / POURCENT if definition.ecart_csg_independant else 0.0
    return types.Legislation(systeme=systeme, ecart_csg_activite=ecart)


def chiffre(levier: str, profil: types.Profil) -> bool:
    return not LEVIERS[levier].non_chiffre(profil)


@lru_cache(maxsize=CACHE_CASCADES)
def cascade_reformee(
    identifiant: str, levier: str, valeur: float, annee: int = types.ANNEE
) -> types.CascadeMenage | None:
    """Cascade du ménage type sous le levier ; ``None`` si l'effet n'est pas chiffré."""
    if not chiffre(levier, types.PROFILS[identifiant]):
        return None
    return types.cascade_type_reformee(identifiant, legislation(levier, valeur, annee), annee)


def cascade_profil_reformee(
    profil: types.Profil, levier: str, valeur: float, annee: int = types.ANNEE
) -> types.CascadeMenage | None:
    """Même calcul pour un profil saisi, sans cache (règle 5)."""
    if not chiffre(levier, profil):
        return None
    return types.cascade_profil(profil, annee, legislation(levier, valeur, annee))


SENS = (1.0, -1.0)
"""Hausse et baisse d'une unité du levier (point ou pourcent), publiées pour chaque ménage."""


def _cascades_levier(levier: str, valeur: float) -> dict[str, types.CascadeMenage | None]:
    return {i: cascade_reformee(i, levier, valeur) for i in types.PROFILS}


@cache
def effets_unitaires(
    processus: int | None = None,
) -> dict[str, dict[float, dict[str, types.CascadeMenage | None]]]:
    """Cascades des ménages types après une hausse et une baisse d'une unité de chaque levier.

    Calcul réparti entre ``processus`` processus (un par couple levier-sens), car chaque
    législation réformée reconstruit ses paramètres (quelques secondes par ménage). Mis en
    cache : ne dépend d'aucune donnée saisie.
    """
    couples = [(levier, valeur) for levier in LEVIERS for valeur in SENS]
    # « spawn » plutôt que « fork » : le processus appelant (serveur, tests) peut avoir des
    # fils d'exécution, et un fork les copierait dans un état incohérent.
    contexte = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=processus, mp_context=contexte) as executeur:
        resultats = executeur.map(_cascades_levier, *zip(*couples, strict=True))
        effets: dict[str, dict[float, dict[str, types.CascadeMenage | None]]] = {}
        for (levier, valeur), cascades in zip(couples, resultats, strict=True):
            effets.setdefault(levier, {})[valeur] = cascades
    return effets
