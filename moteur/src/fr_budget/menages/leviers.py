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
  de base du RSA et de la prime d'activité multipliés par 1 + x ; pension du retraité multipliée
  par 1 + x * part des pensions de base dans les pensions de droit direct (comptes de la
  protection sociale, ``fr_budget.agrege.indexation.part_base_droit_direct``) : le levier ne
  porte que sur les pensions de base, et la part de base de chaque retraité n'est pas connue.

Les autres leviers n'ont pas d'effet direct sur la cascade de ces ménages (``SANS_EFFET``).
"""

from __future__ import annotations

import multiprocessing
import warnings
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from functools import cache, lru_cache
from typing import Any

from openfisca_core.periods import period as periode
from openfisca_core.reforms import Reform

from fr_budget import scenario
from fr_budget.agrege import indexation
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
OPENFISCA = "openfisca_france_176_1_2"
CCSS = "ccss_octobre_2026"


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
    ecart_pension: bool = False
    """Le levier revalorise la part de base de la pension d'un retraité (donnée d'OpenFisca,
    changée hors du système socio-fiscal)."""
    non_chiffre: Callable[[types.Profil], bool] = lambda _p: False
    """Profils dont l'effet n'est pas chiffré, faute de source."""
    sources: tuple[str, ...] = (OPENFISCA,)
    """Sources du registre qui définissent le levier et sa traduction (paramètres et formules
    d'OpenFisca-France, périmètre fixé par la référence du levier)."""


LEVIERS: dict[str, LevierMenage] = {
    "csg_activite": LevierMenage(
        _points(PARAMETRE_CSG_ACTIVITE),
        "points",
        ecart_csg_independant=True,
        sources=(OPENFISCA, CCSS, "service_public_f2971", "urssaf_reforme_assiette_independants"),
    ),
    "csg_retraites": LevierMenage(
        _points(PARAMETRE_CSG_RETRAITES), "points", sources=(OPENFISCA, CCSS)
    ),
    scenario.LEVIER_COTISATIONS_TAUX: LevierMenage(
        _cotisation_patronale, "points", sources=(OPENFISCA, CCSS)
    ),
    scenario.LEVIER_ALLEGEMENTS: LevierMenage(_allegements, "%", sources=(OPENFISCA, CCSS)),
    scenario.LEVIER_IR_SEUILS: LevierMenage(
        _seuils_ir, "%", sources=(OPENFISCA, "plf2025_evaluations_prealables")
    ),
    scenario.LEVIER_PA_PENTE: LevierMenage(_points(PARAMETRE_PENTE, ppa=True), "points"),
    scenario.LEVIER_INDEXATION: LevierMenage(
        _indexation,
        "points",
        ecart_pension=True,
        sources=(
            OPENFISCA,
            "drees_comptes_protection_sociale_2025",
            "drees_retraites_2025_fiche05",
        ),
    ),
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
    scenario.LEVIER_RETRAITES_AGE_LEGAL: "structurel",
    scenario.LEVIER_DEPENSE_FISCALE_UNITE: "catalogue",
    scenario.LEVIER_CREDITS_UNITE: "administrations",
}


Mesures = tuple[tuple[str, float], ...]
"""Mesures d'un scénario : couples (levier, valeur), triés, sans valeur nulle."""


def mesures(valeurs: dict[str, float]) -> Mesures:
    """Mesures du scénario qui changent la législation des ménages ; les autres leviers du
    simulateur (``SANS_EFFET``, et chaque dépense fiscale ou mission prise à part) sont
    écartés, un levier inconnu du simulateur est refusé."""

    def connu(levier: str) -> bool:
        try:
            scenario.bornes_levier(levier)
        except ValueError:
            return False
        return True

    inconnus = {k for k in valeurs if k not in LEVIERS and not connu(k)}
    if inconnus:
        msg = f"leviers inconnus : {sorted(inconnus)}"
        raise ValueError(msg)
    return tuple(sorted((k, float(v)) for k, v in valeurs.items() if k in LEVIERS and v != 0))


class ReformeLevier(Reform):  # type: ignore[misc]
    name = "Scénario du simulateur FR_Budget"

    def __init__(self, systeme: Any, mesures_: Mesures, debut: str) -> None:
        self._mesures, self._debut = mesures_, debut
        self.modifications: list[Callable[[Any], None]] = []
        super().__init__(systeme)

    def apply(self) -> None:
        for levier, valeur in self._mesures:
            LEVIERS[levier].modification(self, valeur, self._debut)
        if self.modifications:

            def modifier(parametres: Any) -> Any:
                for modification in self.modifications:
                    modification(parametres)
                return parametres

            self.modify_parameters(modifier_function=modifier)


@lru_cache(maxsize=CACHE_LEGISLATIONS)
def legislation_scenario(mesures_: Mesures, annee: int = types.ANNEE) -> types.Legislation:
    """Législation de référence modifiée par toutes les mesures à partir du 1er janvier de
    ``annee``. Mise en cache : elle ne dépend d'aucune donnée saisie."""
    for levier, _ in mesures_:
        if levier not in LEVIERS:
            msg = f"{levier} : pas d'effet direct sur les ménages"
            raise ValueError(msg)
    systeme = ReformeLevier(systeme_socio_fiscal(), mesures_, f"{annee}-01-01")
    ecart = sum(v / POURCENT for k, v in mesures_ if LEVIERS[k].ecart_csg_independant)
    pension = sum(
        v / POURCENT * indexation.part_base_droit_direct()
        for k, v in mesures_
        if LEVIERS[k].ecart_pension
    )
    return types.Legislation(systeme=systeme, ecart_csg_activite=ecart, ecart_pension=pension)


def legislation(levier: str, valeur: float, annee: int = types.ANNEE) -> types.Legislation:
    """Législation de référence modifiée par un seul levier."""
    return legislation_scenario(((levier, valeur),), annee)


def chiffre(levier: str, profil: types.Profil) -> bool:
    return not LEVIERS[levier].non_chiffre(profil)


# Incidence des cotisations patronales (spécification : réglage visible, incidence comptable
# par défaut, résultat montré dans les deux lectures).
COMPTABLE = "comptable"
"""Le coût employeur change, le salaire brut ne change pas."""
SALAIRE = "salaire"
"""Le coût employeur ne change pas : le salaire brut s'ajuste (répercussion complète)."""
INCIDENCES = (COMPTABLE, SALAIRE)
LEVIERS_INCIDENCE = (scenario.LEVIER_COTISATIONS_TAUX, scenario.LEVIER_ALLEGEMENTS)
PRECISION_COUT = 2.0
"""Écart toléré entre le coût employeur annuel ajusté et celui de référence, en euros. Le coût
calculé par OpenFisca avance par marches de moins d'un euro (taux de la réduction générale
arrondi à quatre décimales, calcul en simple précision)."""
PAS_MINIMAL = 0.005
"""Variation du salaire mensuel, en euros, sous laquelle l'ajustement s'arrête."""
ITERATIONS_INCIDENCE = 30


def _ajustable(adulte: types.Adulte) -> bool:
    """Salarié dont le salaire peut s'ajuster : ni retraité, ni indépendant, ni apprenti (payé
    au minimum légal, en pourcentage du SMIC)."""
    return not (adulte.retraite or adulte.independant or adulte.apprentissage is not None)


def _brut_initial(adulte: types.Adulte, annee: int, variante: str = types.CENTRAL) -> float:
    if adulte.montant_mensuel is not None:
        return adulte.montant_mensuel
    return types.brut_mensuel(adulte.niveau, annee, adulte.cadre, variante)


def _couts(profil: types.Profil, legislation_: types.Legislation, annee: int) -> list[float]:
    """Coût employeur annuel de chaque adulte (``salaire_super_brut``)."""
    simulation = types._construire(profil, annee, types.rfr_point_fixe(profil, annee), legislation_)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        total = sum(simulation.calculate("salaire_super_brut", m) for m in types._mois(annee))
    return [float(total[i]) for i in range(len(profil.adultes))]


def profil_repercute(
    profil: types.Profil, legislation_: types.Legislation, annee: int = types.ANNEE
) -> types.Profil:
    """Profil dont le salaire brut de chaque salarié ajustable donne, sous la législation
    réformée, le coût employeur de la législation de référence (point fixe).

    Le salaire ne descend pas sous le SMIC mensuel à temps plein (paramètre d'OpenFisca), ni
    sous le salaire initial s'il lui est déjà inférieur (temps partiel saisi) : la part de la
    hausse qui ne peut pas être répercutée reste au coût employeur. Le salaire ajusté vaut pour
    toutes les années simulées, comme le salaire de référence.
    """
    reference = _couts(profil, types.REFERENCE, annee)
    smic = types.brut_mensuel(types.SMIC, annee)
    bruts = [
        _brut_initial(a, annee, profil.variante) if _ajustable(a) else 0.0 for a in profil.adultes
    ]
    planchers = [min(b, smic) for b in bruts]
    precedents: list[tuple[float, float] | None] = [None] * len(bruts)
    ajuste = profil
    for _ in range(ITERATIONS_INCIDENCE):
        ajuste = replace(
            profil,
            adultes=tuple(
                replace(a, montant_mensuel=b) if _ajustable(a) else a
                for a, b in zip(profil.adultes, bruts, strict=True)
            ),
        )
        couts = _couts(ajuste, legislation_, annee)
        fini = True
        for i, adulte in enumerate(profil.adultes):
            if not _ajustable(adulte) or reference[i] == 0:
                continue
            ecart = couts[i] - reference[i]
            bloque = bruts[i] <= planchers[i] and ecart > 0
            if abs(ecart) <= PRECISION_COUT or bloque:
                continue
            # Sécante sur les deux derniers essais ; au premier, coût supposé proportionnel au
            # salaire. Le coût marginal diffère du coût moyen là où les allègements décroissent
            # avec le salaire.
            precedent = precedents[i]
            precedents[i] = (bruts[i], couts[i])
            if precedent is not None and couts[i] != precedent[1]:
                pente = (couts[i] - precedent[1]) / (bruts[i] - precedent[0])
                nouveau = bruts[i] - ecart / pente
            else:
                nouveau = bruts[i] * reference[i] / couts[i]
            nouveau = max(planchers[i], nouveau)
            if abs(nouveau - bruts[i]) < PAS_MINIMAL:
                continue
            fini = False
            bruts[i] = nouveau
        if fini:
            return ajuste
    msg = f"{profil.libelle} : salaire répercuté sans point fixe"
    raise RuntimeError(msg)


def _verifier_incidence(levier: str, incidence: str) -> None:
    if incidence not in INCIDENCES:
        msg = f"incidence inconnue : {incidence}"
        raise ValueError(msg)
    if incidence == SALAIRE and levier not in LEVIERS_INCIDENCE:
        msg = f"{levier} : pas de lecture répercutée sur le salaire"
        raise ValueError(msg)


def verifier_incidence_scenario(mesures_: Mesures, incidence: str) -> None:
    """Lecture répercutée seulement si une mesure touche les cotisations patronales (choix 44)."""
    if incidence not in INCIDENCES:
        msg = f"incidence inconnue : {incidence}"
        raise ValueError(msg)
    if incidence == SALAIRE and not any(k in LEVIERS_INCIDENCE for k, _ in mesures_):
        msg = "pas de lecture répercutée sur le salaire sans mesure sur les cotisations patronales"
        raise ValueError(msg)


def _chiffre_scenario(mesures_: Mesures, profil: types.Profil) -> bool:
    return all(chiffre(levier, profil) for levier, _ in mesures_)


def _cascade(
    profil: types.Profil, mesures_: Mesures, annee: int, incidence: str
) -> types.CascadeMenage:
    reforme = legislation_scenario(mesures_, annee)
    if incidence == SALAIRE:
        profil = profil_repercute(profil, reforme, annee)
    return types.cascade_profil(profil, annee, reforme)


@lru_cache(maxsize=CACHE_CASCADES)
def cascade_scenario(
    identifiant: str,
    mesures_: Mesures,
    annee: int = types.ANNEE,
    incidence: str = COMPTABLE,
    variante: str = types.CENTRAL,
) -> types.CascadeMenage | None:
    """Cascade du ménage type sous toutes les mesures du scénario, dans la variante de revenu
    ``variante`` ; ``None`` si l'effet d'une des mesures n'est pas chiffré pour ce ménage."""
    verifier_incidence_scenario(mesures_, incidence)
    profil = types.profil_type(identifiant, variante)
    if not _chiffre_scenario(mesures_, profil):
        return None
    if incidence == COMPTABLE:
        return types.cascade_type_reformee(
            identifiant, legislation_scenario(mesures_, annee), annee, variante
        )
    return _cascade(profil, mesures_, annee, incidence)


def cascade_profil_scenario(
    profil: types.Profil,
    mesures_: Mesures,
    annee: int = types.ANNEE,
    incidence: str = COMPTABLE,
) -> types.CascadeMenage | None:
    """Même calcul pour un profil saisi, sans cache (règle 5)."""
    verifier_incidence_scenario(mesures_, incidence)
    if not _chiffre_scenario(mesures_, profil):
        return None
    return _cascade(profil, mesures_, annee, incidence)


def cascade_reformee(
    identifiant: str,
    levier: str,
    valeur: float,
    annee: int = types.ANNEE,
    incidence: str = COMPTABLE,
    variante: str = types.CENTRAL,
) -> types.CascadeMenage | None:
    """Cascade du ménage type sous un seul levier ; ``None`` si l'effet n'est pas chiffré."""
    _verifier_incidence(levier, incidence)
    return cascade_scenario(identifiant, ((levier, valeur),), annee, incidence, variante)


def cascade_profil_reformee(
    profil: types.Profil,
    levier: str,
    valeur: float,
    annee: int = types.ANNEE,
    incidence: str = COMPTABLE,
) -> types.CascadeMenage | None:
    """Même calcul pour un profil saisi, sans cache (règle 5)."""
    _verifier_incidence(levier, incidence)
    return cascade_profil_scenario(profil, ((levier, valeur),), annee, incidence)


SENS = (1.0, -1.0)
"""Hausse et baisse d'une unité du levier (point ou pourcent), publiées pour chaque ménage."""
PAS_GRILLE: dict[str, float] = {scenario.LEVIER_ALLEGEMENTS: 10.0}
"""Pas de la grille des effets exportés (une unité par défaut). Allègements : 10 %, leur effet
sur le coût employeur étant proportionnel (et nul sur le net en lecture comptable)."""


def grille(levier: str) -> tuple[float, ...]:
    """Valeurs du levier dont l'effet exact est exporté : les multiples du pas dans les bornes
    du simulateur, plus une unité de chaque côté ; jamais zéro (la référence)."""
    bas, haut = scenario.bornes_levier(levier)
    pas = PAS_GRILLE.get(levier, 1.0)
    valeurs = {*SENS}
    k = 1
    while k * pas <= max(-bas, haut) + 1e-9:
        valeurs |= {v for v in (k * pas, -k * pas) if bas - 1e-9 <= v <= haut + 1e-9}
        k += 1
    return tuple(sorted(v for v in valeurs if bas - 1e-9 <= v <= haut + 1e-9))


def _cascades_levier(
    levier: str, valeur: float, incidence: str, variante: str = types.CENTRAL
) -> dict[str, types.CascadeMenage | None]:
    return {
        i: cascade_reformee(i, levier, valeur, types.ANNEE, incidence, variante)
        for i in types.PROFILS
    }


Effets = dict[str, dict[str, dict[float, dict[str, types.CascadeMenage | None]]]]
"""Levier → incidence → valeur → ménage type → cascade."""


@cache
def effets_grille_variantes(processus: int | None = None) -> dict[str, Effets]:
    """Cascades des ménages types pour chaque valeur de la grille de chaque levier, en lecture
    comptable, et aussi répercutée sur le salaire pour les cotisations patronales, dans chaque
    variante de revenu (``types.VARIANTES``).

    Calcul réparti entre ``processus`` processus (un par levier, incidence, valeur et
    variante), car chaque législation réformée reconstruit ses paramètres (quelques secondes
    par ménage). Mis en cache : ne dépend d'aucune donnée saisie.
    """
    cas = [
        (levier, valeur, incidence, variante)
        for variante in types.VARIANTES
        for levier in LEVIERS
        for incidence in (INCIDENCES if levier in LEVIERS_INCIDENCE else (COMPTABLE,))
        for valeur in grille(levier)
    ]
    # « spawn » plutôt que « fork » : le processus appelant (serveur, tests) peut avoir des
    # fils d'exécution, et un fork les copierait dans un état incohérent.
    contexte = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=processus, mp_context=contexte) as executeur:
        resultats = executeur.map(_cascades_levier, *zip(*cas, strict=True))
        effets: dict[str, Effets] = {}
        for (levier, valeur, incidence, variante), cascades in zip(cas, resultats, strict=True):
            par_levier = effets.setdefault(variante, {}).setdefault(levier, {})
            par_levier.setdefault(incidence, {})[valeur] = cascades
    return effets


def effets_grille(processus: int | None = None) -> Effets:
    """Cascades de la grille au revenu central (``effets_grille_variantes``)."""
    return effets_grille_variantes(processus)[types.CENTRAL]


# Approximation du simulateur : le site ne peut pas lancer OpenFisca. Pour chaque mesure, il
# interpole chaque ligne de la cascade entre les valeurs de la grille qui l'encadrent, additionne
# les écarts des mesures ligne par ligne, et ne laisse aucune prestation devenir négative. Même
# calcul en TypeScript : web/lib/effets-menages.ts.

CHAMPS_CASCADE = (
    "cout_employeur",
    "salaire_brut",
    "net_avant_impot",
    "net_imposable",
    "impot_revenu",
    "pension_brute",
    "pension_nette",
    "revenu_independant_brut",
    "cotisations_independant",
    "csg_crds_independant",
    "revenu_independant_net",
)


def _vecteur(c: types.CascadeMenage) -> dict[str, float]:
    return {
        **{champ: getattr(c, champ) for champ in CHAMPS_CASCADE},
        **{f"prestations.{k}": v for k, v in c.prestations.items()},
    }


def _interpoler(
    reference: dict[str, float], points: dict[float, types.CascadeMenage | None], valeur: float
) -> dict[str, float] | None:
    """Écart de chaque ligne pour ``valeur``, interpolé entre les deux points qui l'encadrent
    (la référence est le point zéro) ; ``None`` si l'un d'eux n'est pas chiffré."""
    if valeur in points:
        exact = points[valeur]
        if exact is None:
            return None
        vecteur = _vecteur(exact)
        return {k: vecteur.get(k, 0.0) - reference.get(k, 0.0) for k in {*vecteur, *reference}}
    abscisses = sorted({0.0, *points})
    bas = max(x for x in abscisses if x <= valeur)
    haut = min(x for x in abscisses if x >= valeur)
    ecarts = []
    for x in (bas, haut):
        if x == 0:
            ecarts.append(dict.fromkeys(reference, 0.0))
            continue
        ecart = _interpoler(reference, points, x)
        if ecart is None:
            return None
        ecarts.append(ecart)
    poids = (valeur - bas) / (haut - bas)
    cles = {*ecarts[0], *ecarts[1]}
    return {k: (1 - poids) * ecarts[0].get(k, 0.0) + poids * ecarts[1].get(k, 0.0) for k in cles}


def approximation(
    identifiant: str,
    mesures_: Mesures,
    effets: Effets,
    incidence: str = COMPTABLE,
    variante: str = types.CENTRAL,
) -> types.CascadeMenage | None:
    """Cascade approchée du ménage type sous le scénario ; ``None`` si une mesure n'est pas
    chiffrée pour ce ménage. ``effets`` : grille de la même variante de revenu."""
    reference = _vecteur(types.cascade_annuelle(identifiant, types.ANNEE, variante))
    total = dict(reference)
    for levier, valeur in mesures_:
        lecture = incidence if levier in LEVIERS_INCIDENCE else COMPTABLE
        points = {v: cascades[identifiant] for v, cascades in effets[levier][lecture].items()}
        ecart = _interpoler(reference, points, valeur)
        if ecart is None:
            return None
        for k, v in ecart.items():
            total[k] = total.get(k, 0.0) + v
    prestations = {
        k.removeprefix("prestations."): max(v, 0.0)
        for k, v in total.items()
        if k.startswith("prestations.") and max(v, 0.0) != 0
    }
    return types.CascadeMenage(
        **{champ: total[champ] for champ in CHAMPS_CASCADE}, prestations=prestations
    )


def scenarios_controle() -> list[Mesures]:
    """Scénarios de contrôle : chaque levier à une valeur hors de la grille (la moitié de sa
    borne, sauf si elle y est), à sa borne basse et à sa borne haute, puis tous les leviers
    ensemble à la moitié de leurs bornes et à leurs bornes (bornes du simulateur)."""
    bornes = {levier: scenario.bornes_levier(levier) for levier in LEVIERS}
    scenarios: list[Mesures] = []
    for levier, (bas, haut) in bornes.items():
        for v in (bas, bas / 2 + 0.25, haut / 2 + 0.25, haut):
            if v != 0:
                scenarios.append(((levier, v),))
    for facteur in (0.5, 1.0):
        for k in (0, 1):
            scenarios.append(mesures({lv: b[k] * facteur for lv, b in bornes.items()}))
    return [m for m in scenarios if m]


def scenarios_controle_salaire() -> list[Mesures]:
    """Scénarios de contrôle de la lecture répercutée : ceux qui touchent les cotisations
    patronales, aux bornes (chaque levier concerné seul, puis tous les leviers ensemble). Le
    calcul exact ajuste le salaire par itérations : les valeurs intermédiaires ne sont pas
    reprises, pour garder l'export dans une durée raisonnable."""
    bornes = {levier: scenario.bornes_levier(levier) for levier in LEVIERS}
    seuls = [((levier, b),) for levier in LEVIERS_INCIDENCE for b in bornes[levier] if b != 0]
    ensemble = [mesures({lv: b[k] for lv, b in bornes.items()}) for k in (0, 1)]
    return [*seuls, *ensemble]


def _exact(mesures_: Mesures, incidence: str = COMPTABLE) -> dict[str, types.CascadeMenage | None]:
    return {i: cascade_scenario(i, mesures_, types.ANNEE, incidence) for i in types.PROFILS}


@dataclass(frozen=True)
class Controle:
    """Écarts du net après impôt d'un scénario de contrôle, par ménage type : (exact, approché),
    ou ``None`` si l'effet n'est pas chiffré."""

    mesures: Mesures
    incidence: str
    menages: dict[str, tuple[float, float] | None]


@cache
def controle_approximation(processus: int | None = None) -> list[Controle]:
    """Pour chaque scénario de contrôle et chaque ménage type : écart du net après impôt
    calculé exactement (une seule réforme) et approché (grille interpolée), en lecture
    comptable, et en lecture répercutée sur le salaire pour les scénarios qui touchent les
    cotisations patronales. Mis en cache : ne dépend d'aucune donnée saisie."""
    effets = effets_grille(processus)
    cas = [(m, COMPTABLE) for m in scenarios_controle()] + [
        (m, SALAIRE) for m in scenarios_controle_salaire()
    ]
    contexte = multiprocessing.get_context("spawn")
    with ProcessPoolExecutor(max_workers=processus, mp_context=contexte) as executeur:
        exacts = list(executeur.map(_exact, *zip(*cas, strict=True)))
    resultats: list[Controle] = []
    for (mesures_, incidence), cascades in zip(cas, exacts, strict=True):
        menages: dict[str, tuple[float, float] | None] = {}
        for i, cascade in cascades.items():
            approche = approximation(i, mesures_, effets, incidence)
            if cascade is None or approche is None:
                menages[i] = None
                continue
            reference = types.cascade_annuelle(i).net_apres_impot
            menages[i] = (
                cascade.net_apres_impot - reference,
                approche.net_apres_impot - reference,
            )
        resultats.append(Controle(mesures_, incidence, menages))
    return resultats
