"""Scénario : effet de leviers sur le solde primaire et la dette (lot 2.1 du plan).

Chaîne de calcul (CLAUDE.md) : levier → écart de solde primaire → dynamique de la dette avec
la baseline (``fr_budget.baseline``) → résultats en fourchette.

- Effet d'un levier : rendement de l'année de référence (Md€), rapporté au PIB de la même
  année (INSEE, comptes nationaux 2025), puis tenu constant en points de PIB à partir de
  l'année d'entrée en vigueur (hypothèse ``scenario_rendement_constant_pib``).
- Dette du scénario : même formule et mêmes entrées que la baseline (taux apparent,
  croissance, ajustement stock-flux), solde primaire augmenté de l'effet. La baisse de la
  charge d'intérêts découle de la dette plus faible.
- Aucun effet de comportement (V3) ni de croissance : l'interrupteur du multiplicateur
  budgétaire n'existe pas encore et sera désactivé par défaut (CLAUDE.md).

Leviers disponibles :

- ``tva_taux_normal`` : hausse (ou baisse) de x points du taux normal de TVA. Rendement d'un
  point : point net 2025 au taux normal (``fr_budget.agrege.tva``, convention du point net,
  décision du mainteneur du 9 octobre 2026, option (a)). Statut du levier : celui de ``tva``
  dans ``registres/leviers.yaml``.
- ``depense_fiscale_<numéro>`` et ``depenses_fiscales_<impôt>`` : réduction de x % d'une
  dépense fiscale, ou de toutes celles d'un impôt (``fr_budget.agrege.depenses_fiscales``).
  Rendement d'un pour cent : 1 % du coût prévu pour 2026 par le PLF 2026, ramené en euros de
  2025 par la croissance nominale 2026 du RESF 2027 (le rapport au PIB 2025 donne alors le
  rapport du coût 2026 au PIB 2026). ``depense_fiscale`` : unité générique (1 Md€ de 2025, plage
  d'une dépense), dont le site se sert pour une dépense choisie dans le catalogue.
- ``credits_mission_<mission>`` : variation de x % des crédits de paiement d'une mission du
  budget général (``fr_budget.agrege.credits_missions``), de -20 à +20 % (borne confirmée
  par le mainteneur). Effet d'un pour cent : moins 1 % des crédits demandés au PLF 2026
  (une hausse dégrade le solde), ramené en euros de 2025 comme les dépenses fiscales ;
  1 € de crédit compte pour 1 € de solde des administrations publiques (option 3 (a) du
  9 octobre 2026). ``credits_missions`` : unité
  générique (hausse de 1 Md€ de 2025), dont le site se sert pour les missions réglées.
- ``dotations_dgf`` et ``dotations_compensations`` : variation de x % (de -10 à +10) de la
  dotation globale de fonctionnement ou des compensations fiscales versées aux collectivités
  (``fr_budget.agrege.dotations``). Le solde public ne change que par la réaction de
  l'investissement local : effet d'un pour cent = moins 1 % du montant 2026, ramené en euros de
  2025, multiplié par le taux de répercussion (élasticités de la Caisse des Dépôts). L'effet
  sur le seul budget de l'État (``effet_etat_unitaire``) est affiché à part.
- ``remunerations_point_indice`` et ``remunerations_effectifs`` : variation de x % (de -5 à
  +5) de la valeur du point d'indice ou des effectifs des trois fonctions publiques
  (``fr_budget.agrege.remunerations``). Effet d'un pour cent : moins le coût net pour les
  administrations publiques (hausse du revenu après impôt des agents) ; le coût brut
  (``effet_brut_unitaire``) est affiché à part. Montants de 2025 : aucune conversion.
- ``indexation_pensions_prestations`` : revalorisation des pensions de base et des prestations
  revalorisées par la loi supérieure (ou inférieure) de x points à la revalorisation légale,
  une année, de -2 à +1 point (décision du mainteneur du 12 octobre 2026)
  (``fr_budget.agrege.indexation``). Effet d'un point : moins le coût net en année pleine
  (prélèvements sociaux et impôt sur le revenu déduits), sur les montants de 2025 ; le coût
  brut (``effet_brut_unitaire``) est affiché à part. Combinaison refusée avec la mission
  « Solidarité, insertion et égalité des chances », qui finance l'AAH et la prime d'activité.
- ``csg_activite``, ``csg_retraites`` et ``csg_capital`` : hausse (ou baisse) de x points, de
  -2 à +2, du taux de CSG sur les revenus d'activité, sur les pensions de retraite au taux
  plein ou sur les revenus du capital (``fr_budget.agrege.csg``). Effet d'un point : rendement
  constaté en 2025 divisé par le taux (part du taux plein pour les retraites), brut de l'effet
  de la CSG déductible sur l'impôt sur le revenu.
- ``cotisations_patronales_taux`` : hausse (ou baisse) de x points, de -2 à +2, du taux de
  cotisation patronale déplafonnée du secteur privé, hors champ des allègements généraux
  (``fr_budget.agrege.cotisations``) ; effet d'un point : valeur de point de la CCSS.
- ``allegements_generaux`` : variation de x % (de -20 à +20) du coût des allègements généraux
  de cotisations des salariés ; effet d'un pour cent : moins 1 % du coût constaté en 2025.
- ``prime_activite_pente`` : variation de x points, de -5 à +5, de la fraction des revenus
  professionnels prise en compte dans le calcul de la prime d'activité
  (``fr_budget.agrege.prime_activite``) ; effet d'un point : moins le coût en année pleine,
  calé sur le chiffrage de la baisse de 2025. Combinaison refusée avec la mission
  « Solidarité, insertion et égalité des chances », qui finance la prime d'activité.
- ``ir_seuils_bareme`` : revalorisation des seuils du barème de l'impôt sur le revenu supérieure
  (ou inférieure) de x %, de -3 à +3, à l'indexation sur l'inflation
  (``fr_budget.agrege.impot_revenu``) ; effet d'un pour cent : moins la sensibilité de
  l'évaluation préalable du PLF 2025 (borne basse : calcul par décile).

Fourchettes : écart au scénario de référence, avec la plage du rendement du levier ; niveau
de dette et de solde, avec la plage du levier et celle de la baseline, chacune seule.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from functools import cache

from fr_budget import baseline as module_baseline
from fr_budget import croissance as module_croissance
from fr_budget.agrege import (
    accises,
    cotisations,
    credits_missions,
    csg,
    depenses_fiscales,
    dotations,
    impot_revenu,
    impot_societes,
    indexation,
    prime_activite,
    remunerations,
)
from fr_budget.agrege.tva import HYPOTHESE_REPARTITION, fourchette_point_tva, taux_tva
from fr_budget.apu import comptes_apu, ratio_pib
from fr_budget.baseline import ANNEE_FIN, AnneeBaseline, trajectoires
from fr_budget.dette import dette_suivante
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import chiffrage, hypothese

LEVIER_TVA_NORMAL = "tva_taux_normal"
LEVIER_ACCISE_GAZOLE = "accise_gazole"
LEVIER_ACCISE_ESSENCES = "accise_essences"
LEVIERS_ACCISES = {LEVIER_ACCISE_GAZOLE: "gazole", LEVIER_ACCISE_ESSENCES: "essences"}
LEVIER_IS_TAUX_NORMAL = "is_taux_normal"
LEVIER_IS_SURTAXE = "is_surtaxe_grandes_entreprises"
LEVIER_DEPENSE_FISCALE_UNITE = "depense_fiscale"
PREFIXE_DEPENSE_FISCALE = "depense_fiscale_"
PREFIXE_DEPENSES_FISCALES_IMPOT = "depenses_fiscales_"
HYPOTHESE_ECART_DEPENSE = "depenses_fiscales_ecart_depense"
LEVIER_CREDITS_UNITE = "credits_missions"
PREFIXE_CREDITS_MISSION = "credits_mission_"
HYPOTHESE_ECART_CREDITS = "credits_missions_ecart_execution"
# Variation admise des crédits d'une mission, en % : choix du lot 2.5, confirmé par le
# mainteneur le 9 octobre 2026 (aucune source ne borne une variation de crédits).
BORNE_CREDITS = 20.0
LEVIER_DOTATIONS_DGF = "dotations_dgf"
LEVIER_DOTATIONS_COMPENSATIONS = "dotations_compensations"
LEVIERS_DOTATIONS = {
    LEVIER_DOTATIONS_DGF: dotations.DGF,
    LEVIER_DOTATIONS_COMPENSATIONS: dotations.COMPENSATIONS,
}
# Variation admise des dotations, en % (option 3 (a) du 9 octobre 2026) ; repère : la baisse
# de la DGF de 2014 à 2017, environ 3,5 Md€ par an (Caisse des Dépôts, Éclairages n° 8).
BORNE_DOTATIONS = 10.0
LEVIER_POINT_INDICE = "remunerations_point_indice"
LEVIER_EFFECTIFS = "remunerations_effectifs"
LEVIERS_REMUNERATIONS = {
    LEVIER_POINT_INDICE: remunerations.POINT,
    LEVIER_EFFECTIFS: remunerations.EFFECTIFS,
}
# Variation admise du point et des effectifs, en % (décision du mainteneur du 12 octobre 2026).
BORNE_REMUNERATIONS = 5.0
LEVIERS_CSG = {
    "csg_activite": csg.ACTIVITE,
    "csg_retraites": csg.RETRAITES,
    "csg_capital": csg.CAPITAL,
}
# Variation admise des taux de CSG, en points (choix du lot 2.9, à relire) ; repère : la hausse
# de 1,7 point de la LFSS 2018.
BORNE_CSG = 2.0
LEVIER_COTISATIONS_TAUX = "cotisations_patronales_taux"
LEVIER_ALLEGEMENTS = "allegements_generaux"
# Bornes choisies au lot 2.10 (à relire) : ±2 points de taux comme la CSG ; ±20 % des
# allègements comme les crédits des missions (repère : le gel du barème de la RGDU, 5,6 Md€
# en 2027, soit environ 8 % du coût).
BORNE_COTISATIONS_TAUX = 2.0
BORNE_ALLEGEMENTS = 20.0
LEVIER_PA_PENTE = "prime_activite_pente"
# Variation admise de la pente, en points (choix du lot 2.12, à relire) ; repère : la baisse de
# 1,15 point de 2025.
BORNE_PA_PENTE = 5.0
LEVIER_IR_SEUILS = "ir_seuils_bareme"
# Écart admis à l'indexation des seuils, en % (choix du lot 2.11, à relire) ; repères : gel de
# 2026 (-1,0 %), indexation de 4,8 % de la LFI 2024.
BORNE_IR_SEUILS = 3.0
LEVIER_INDEXATION = "indexation_pensions_prestations"
# Écart admis à la revalorisation légale, en points (décision du mainteneur du 12 octobre 2026) ;
# repère : le gel de 2026 proposé au PLFSS 2026 correspondait à -1,0 point.
BORNES_INDEXATION = (-2.0, 1.0)
# Mission qui finance l'AAH et la prime d'activité (programmes 157 et 304), comprises dans le
# levier d'indexation.
MISSION_SOLIDARITE = "solidarite_insertion_et_egalite_des_chances"
IMPOT_REVENU_DEPENSES_FISCALES = "impot_revenu"
MILLIONS_PAR_MILLIARD = 1000.0
EUROS_PAR_MILLIARD = 1e9
ANNEE_REFERENCE = 2025
# Premier exercice dont le budget n'est pas encore voté : celui du PLF 2027.
ANNEE_PREMIERE_MESURE = 2027
POURCENT = 100.0


@dataclass(frozen=True)
class Mesure:
    """Un levier, sa valeur (en points pour la TVA) et son année d'entrée en vigueur."""

    levier: str
    valeur: float
    annee: int


def levier_depense_fiscale(code: str) -> str:
    """Identifiant du levier de réduction d'une dépense fiscale du catalogue."""
    return PREFIXE_DEPENSE_FISCALE + code


def levier_depenses_fiscales_impot(impot: str) -> str:
    """Identifiant du levier de réduction des dépenses fiscales d'un impôt."""
    return PREFIXE_DEPENSES_FISCALES_IMPOT + impot


LEVIERS_DEPENSES_FISCALES_IMPOT = {
    levier_depenses_fiscales_impot(i): i for i in depenses_fiscales.IMPOTS_LEVIER
}


def depense_du_levier(levier: str) -> depenses_fiscales.DepenseFiscale | None:
    """Dépense fiscale visée par un levier ``depense_fiscale_<numéro>`` ; ``None`` sinon."""
    if not levier.startswith(PREFIXE_DEPENSE_FISCALE):
        return None
    try:
        return depenses_fiscales.depense(levier.removeprefix(PREFIXE_DEPENSE_FISCALE))
    except ValueError:
        return None


def levier_credits_mission(ident: str) -> str:
    """Identifiant du levier de variation des crédits d'une mission."""
    return PREFIXE_CREDITS_MISSION + ident


def mission_du_levier(levier: str) -> credits_missions.Mission | None:
    """Mission visée par un levier ``credits_mission_<mission>`` ; ``None`` sinon."""
    if not levier.startswith(PREFIXE_CREDITS_MISSION):
        return None
    try:
        return credits_missions.mission(levier.removeprefix(PREFIXE_CREDITS_MISSION))
    except ValueError:
        return None


ANNEE_MONTANTS_2026 = 2026
if not (
    depenses_fiscales.ANNEE_COUT_LEVIER
    == credits_missions.ANNEE_CREDITS
    == dotations.PLF_LEVIER
    == ANNEE_MONTANTS_2026
):
    msg = "les montants des leviers de dépenses fiscales et de crédits doivent être de 2026"
    raise RuntimeError(msg)


def _vers_euros_reference(montant_2026: float) -> float:
    """Montant de 2026 ramené en euros de 2025 par la croissance nominale 2026 (RESF 2027)."""
    croissance = module_baseline.resf()[(ANNEE_MONTANTS_2026, "croissance_nominale")]
    return montant_2026 / (1 + croissance / POURCENT)


def _avec_plage(valeur: float, identifiant: str) -> Fourchette:
    plage = hypothese(identifiant).plage
    return encadrer(valeur, [valeur * (1 + plage.basse), valeur * (1 + plage.haute)])


def _cout_un_pourcent(cout_meur: float) -> float:
    """Rendement d'1 % d'un coût 2026 en M€, en Md€ de l'année de référence."""
    return _vers_euros_reference(cout_meur / MILLIONS_PAR_MILLIARD / POURCENT)


def effet_etat_unitaire(levier: str) -> float:
    """Dotations : effet d'une hausse d'un pour cent sur le solde du seul État, en Md€ de 2025.

    C'est l'opposé d'un pour cent du montant proposé pour 2026 ; les collectivités reçoivent
    autant, et le solde public ne change que par leur réaction (``rendement_unitaire``).
    """
    dotation = LEVIERS_DOTATIONS[levier]
    return -_vers_euros_reference(dotations.montant_levier(dotation) / POURCENT)


LEVIERS_EFFET_BRUT = (*LEVIERS_REMUNERATIONS, LEVIER_INDEXATION)


def effet_brut_unitaire(levier: str) -> float:
    """Rémunérations et indexation : effet brut d'une unité (1 %, ou 1 point de
    revalorisation), avant les retours de cotisations, de CSG et d'impôt aux administrations
    publiques, en Md€ de 2025."""
    if levier == LEVIER_INDEXATION:
        return -indexation.cout_brut_un_point()
    return -remunerations.cout_brut_un_pourcent(LEVIERS_REMUNERATIONS[levier])


def rendement_unitaire(levier: str) -> Fourchette:
    """Rendement d'une unité du levier, en Md€ de l'année de référence.

    TVA : point net au taux normal. Accises : un centime par litre (1 €/hl) sur l'assiette du
    levier (``fr_budget.agrege.accises.assiette_levier``), bornes de l'hypothèse des masses
    volumiques. Dépenses fiscales : 1 % du coût 2026, plage de l'écart de prévision. Crédits
    d'une mission : moins 1 % des crédits 2026, plage de l'écart d'exécution.
    """
    if levier in LEVIERS_REMUNERATIONS:
        net = remunerations.cout_net_un_pourcent(LEVIERS_REMUNERATIONS[levier])
        return encadrer(-net.central, [-net.bas, -net.haut])
    if levier == LEVIER_INDEXATION:
        net = indexation.cout_un_point()
        return encadrer(-net.central, [-net.bas, -net.haut])
    if levier in LEVIERS_CSG:
        return csg.rendement_un_point(LEVIERS_CSG[levier])
    if levier == LEVIER_COTISATIONS_TAUX:
        return cotisations.rendement_point_taux()
    if levier == LEVIER_PA_PENTE:
        cout = prime_activite.cout_un_point()
        return encadrer(-cout.central, [-cout.bas, -cout.haut])
    if levier == LEVIER_IR_SEUILS:
        r = impot_revenu.rendement_un_pourcent()
        return encadrer(-r.central, [-r.bas, -r.haut])
    if levier == LEVIER_ALLEGEMENTS:
        cout = cotisations.cout_un_pourcent_allegements()
        return encadrer(-cout.central, [-cout.bas, -cout.haut])
    if levier in LEVIERS_DOTATIONS:
        dotation = LEVIERS_DOTATIONS[levier]
        un_pourcent = -effet_etat_unitaire(levier)
        t = dotations.taux_repercussion(dotation)
        return encadrer(-t.central * un_pourcent, [-t.bas * un_pourcent, -t.haut * un_pourcent])
    if levier == LEVIER_CREDITS_UNITE:
        return _avec_plage(-1.0, HYPOTHESE_ECART_CREDITS)
    mission = mission_du_levier(levier)
    if mission is not None:
        valeur = _vers_euros_reference(mission.credits / EUROS_PAR_MILLIARD / POURCENT)
        return _avec_plage(-valeur, HYPOTHESE_ECART_CREDITS)
    if levier == LEVIER_DEPENSE_FISCALE_UNITE:
        return _avec_plage(1.0, HYPOTHESE_ECART_DEPENSE)
    if levier in LEVIERS_DEPENSES_FISCALES_IMPOT:
        impot = LEVIERS_DEPENSES_FISCALES_IMPOT[levier]
        return _avec_plage(
            _cout_un_pourcent(depenses_fiscales.cout_impot_levier(impot)),
            f"depenses_fiscales_ecart_{impot}",
        )
    depense = depense_du_levier(levier)
    if depense is not None:
        return _avec_plage(_cout_un_pourcent(depense.cout), HYPOTHESE_ECART_DEPENSE)
    if levier == LEVIER_IS_TAUX_NORMAL:
        valeur = impot_societes.rendement_point_taux_normal(ANNEE_REFERENCE)
        return Fourchette(valeur, valeur, valeur)
    if levier == LEVIER_IS_SURTAXE:
        valeur = impot_societes.assiette_surtaxe(ANNEE_REFERENCE) / POURCENT
        return Fourchette(valeur, valeur, valeur)
    if levier in LEVIERS_ACCISES:
        cle = LEVIERS_ACCISES[levier]
        plage = hypothese(accises.HYPOTHESE_MASSES).plage
        valeurs = [
            accises.assiette_levier(ANNEE_REFERENCE, e)[cle] / accises.EUROS_PAR_MILLIARD
            for e in (plage.basse, None, plage.haute)
        ]
        return encadrer(valeurs[1], [valeurs[0], valeurs[2]])
    if levier == LEVIER_TVA_NORMAL:
        return fourchette_point_tva(annee_comptes=2022, annee_cible=ANNEE_REFERENCE)["net"][
            "taux_20"
        ]
    msg = f"levier inconnu : {levier}"
    raise ValueError(msg)


def taux_reference(levier: str) -> float:
    """Valeur du paramètre au 1er janvier de l'année de référence, pour l'affichage.

    TVA : taux normal en %. Accises : tarif en centimes par litre du gazole, et du SP95-E10
    (essence la plus vendue en 2025 selon le SDES) pour les essences. Dépenses fiscales : coût
    prévu pour 2026, en Md€ courants (unité générique : 0). Crédits d'une mission : crédits
    demandés au PLF 2026, en Md€ courants (unité générique : 0).
    """
    mission = mission_du_levier(levier)
    if mission is not None:
        return mission.credits / EUROS_PAR_MILLIARD
    if levier == LEVIER_CREDITS_UNITE:
        return 0.0
    if levier in LEVIERS_DOTATIONS:
        return dotations.montant_levier(LEVIERS_DOTATIONS[levier])
    if levier in LEVIERS_REMUNERATIONS:
        # Masse salariale des trois sous-secteurs, hors cotisations imputées, Md€ de 2025.
        return sum(remunerations.masse(v) for v in remunerations.VERSANTS)
    if levier == LEVIER_PA_PENTE:
        # Fraction des revenus professionnels prise en compte, en %.
        return prime_activite.pente_actuelle()
    if levier == LEVIER_IR_SEUILS:
        # Impôt au barème des revenus de 2024, Md€.
        return chiffrage("ir_impot_total_total_2024")
    if levier == LEVIER_COTISATIONS_TAUX:
        # Valeur d'un point en 2026 publiée par la CCSS, Md€ courants.
        return cotisations.valeur_point_prive(cotisations.ANNEE_POINT)
    if levier == LEVIER_ALLEGEMENTS:
        # Coût constaté en 2025, Md€.
        return cotisations.cout_allegements(cotisations.ANNEE_REFERENCE)
    if levier in LEVIERS_CSG:
        # Taux de 2025, en % (taux plein pour les retraites).
        return csg.taux(LEVIERS_CSG[levier], csg.ANNEE_REFERENCE)
    if levier == LEVIER_INDEXATION:
        # Pensions et prestations du levier, Md€ de 2025.
        return sum(indexation.montant(b) for b in indexation.BLOCS)
    if levier in LEVIERS_DEPENSES_FISCALES_IMPOT:
        impot = LEVIERS_DEPENSES_FISCALES_IMPOT[levier]
        return depenses_fiscales.cout_impot_levier(impot) / MILLIONS_PAR_MILLIARD
    depense = depense_du_levier(levier)
    if depense is not None:
        return depense.cout / MILLIONS_PAR_MILLIARD
    if levier == LEVIER_DEPENSE_FISCALE_UNITE:
        return 0.0
    if levier == LEVIER_IS_TAUX_NORMAL:
        return impot_societes.taux_is(ANNEE_REFERENCE)["normal"] * POURCENT
    if levier == LEVIER_IS_SURTAXE:
        return 0.0
    if levier == LEVIER_ACCISE_GAZOLE:
        return accises.tarifs(ANNEE_REFERENCE)["gazole"]
    if levier == LEVIER_ACCISE_ESSENCES:
        return accises.tarifs(ANNEE_REFERENCE)["e10"]
    if levier == LEVIER_TVA_NORMAL:
        return taux_tva(ANNEE_REFERENCE)["normal"] * POURCENT
    msg = f"levier inconnu : {levier}"
    raise ValueError(msg)


def bornes_levier(levier: str) -> tuple[float, float]:
    """Valeurs admises pour le levier.

    Taux normal de TVA : la baisse s'arrête au taux intermédiaire (au-delà, la structure des
    taux change et le chiffrage par point ne s'applique plus) ; la hausse admise est de même
    ampleur. Taux de l'année de référence, paramètres OpenFisca-France.
    """
    if mission_du_levier(levier) is not None:
        return -BORNE_CREDITS, BORNE_CREDITS
    if levier in LEVIERS_DOTATIONS:
        return -BORNE_DOTATIONS, BORNE_DOTATIONS
    if levier in LEVIERS_REMUNERATIONS:
        return -BORNE_REMUNERATIONS, BORNE_REMUNERATIONS
    if levier == LEVIER_INDEXATION:
        return BORNES_INDEXATION
    if levier in LEVIERS_CSG:
        return -BORNE_CSG, BORNE_CSG
    if levier == LEVIER_COTISATIONS_TAUX:
        return -BORNE_COTISATIONS_TAUX, BORNE_COTISATIONS_TAUX
    if levier == LEVIER_PA_PENTE:
        return -BORNE_PA_PENTE, BORNE_PA_PENTE
    if levier == LEVIER_IR_SEUILS:
        return -BORNE_IR_SEUILS, BORNE_IR_SEUILS
    if levier == LEVIER_ALLEGEMENTS:
        return -BORNE_ALLEGEMENTS, BORNE_ALLEGEMENTS
    if levier == LEVIER_CREDITS_UNITE:
        # Md€ de 2025 : la même variation appliquée à toutes les missions du levier.
        total = _vers_euros_reference(credits_missions.total_credits() / EUROS_PAR_MILLIARD)
        return -total * BORNE_CREDITS / POURCENT, total * BORNE_CREDITS / POURCENT
    if levier in LEVIERS_DEPENSES_FISCALES_IMPOT or depense_du_levier(levier) is not None:
        # Réduction en pourcentage du coût : de 0 (aucune) à 100 (suppression).
        return 0.0, POURCENT
    if levier == LEVIER_DEPENSE_FISCALE_UNITE:
        # Md€ de 2025 : au plus le coût de tout le catalogue.
        total = sum(d.cout for d in depenses_fiscales.catalogue())
        return 0.0, _vers_euros_reference(total / MILLIONS_PAR_MILLIARD)
    if levier == LEVIER_TVA_NORMAL:
        taux = taux_tva(ANNEE_REFERENCE)
        ecart = (taux["normal"] - taux["intermediaire"]) * POURCENT
        return -ecart, ecart
    if levier == LEVIER_IS_TAUX_NORMAL:
        # La baisse s'arrête au taux réduit des PME ; la hausse admise est de même ampleur.
        taux = impot_societes.taux_is(ANNEE_REFERENCE)
        ecart = (taux["normal"] - taux["reduit"]) * POURCENT
        return -ecart, ecart
    if levier == LEVIER_IS_SURTAXE:
        # Surtaxe en pourcentage de l'IS dû, de 0 au taux le plus élevé de la contribution
        # exceptionnelle de 2025 (41,2 %, évaluation préalable de l'article 11 du PLF 2025).
        return 0.0, chiffrage("is_taux_contribution_exceptionnelle_haute")
    if levier in LEVIERS_ACCISES:
        # La baisse du gazole s'arrête au tarif réduit du transport routier de marchandises
        # (au-delà, le mécanisme de remboursement s'inverse) ; même amplitude pour la hausse
        # et pour les essences.
        ecart = accises.tarifs(ANNEE_REFERENCE)["gazole"] - chiffrage("accises_tarif_trm_2025")
        return -ecart, ecart
    msg = f"levier inconnu : {levier}"
    raise ValueError(msg)


@cache
def effet_solde(mesure: Mesure) -> Fourchette:
    """Effet de la mesure sur le solde primaire, en points de PIB (positif : solde amélioré)."""
    if not ANNEE_PREMIERE_MESURE <= mesure.annee <= ANNEE_FIN:
        periode = f"{ANNEE_PREMIERE_MESURE}-{ANNEE_FIN}"
        msg = f"année d'entrée en vigueur hors de {periode} : {mesure.annee}"
        raise ValueError(msg)
    basse, haute = bornes_levier(mesure.levier)
    if not basse <= mesure.valeur <= haute:
        msg = f"valeur hors des bornes {basse:g} à {haute:g} : {mesure.valeur}"
        raise ValueError(msg)
    unite = rendement_unitaire(mesure.levier)
    pib = comptes_apu().valeur(ANNEE_REFERENCE, "S1", "pib")
    valeurs = [ratio_pib(mesure.valeur * v, pib) for v in (unite.bas, unite.central, unite.haut)]
    return encadrer(valeurs[1], [valeurs[0], valeurs[2]])


def trajectoire_avec_effet(
    trajectoire: Sequence[AnneeBaseline], effets: Mapping[int, float]
) -> list[AnneeBaseline]:
    """Trajectoire recalculée avec un solde primaire augmenté de ``effets[annee]``.

    La première année est reprise telle quelle ; les suivantes suivent la formule de la dette
    avec le taux apparent, la croissance et l'ajustement stock-flux de la trajectoire donnée.
    """
    lignes = [trajectoire[0]]
    for a in trajectoire[1:]:
        pb = a.solde_primaire + effets.get(a.annee, 0.0)
        dette = dette_suivante(
            lignes[-1].dette,
            a.taux_apparent / POURCENT,
            a.croissance_nominale / POURCENT,
            pb,
            a.ajustement_stock_flux,
        )
        lignes.append(replace(a, dette=dette, solde_primaire=pb))
    return lignes


def facteur_premiere_annee(levier: str) -> float:
    """Part de l'effet en année pleine acquise l'année d'entrée en vigueur.

    Indexation : les prestations revalorisées en avril ne comptent que neuf mois la première
    année (``fr_budget.agrege.indexation.part_effet_premiere_annee``). Autres leviers : 1.
    """
    if levier == LEVIER_INDEXATION:
        return indexation.part_effet_premiere_annee()
    return 1.0


def _effets_par_annee(mesures: Iterable[Mesure], borne: str) -> dict[int, float]:
    effets: dict[int, float] = {}
    for m in mesures:
        valeur = getattr(effet_solde(m), borne)
        for annee in range(m.annee, ANNEE_FIN + 1):
            facteur = facteur_premiere_annee(m.levier) if annee == m.annee else 1.0
            effets[annee] = effets.get(annee, 0.0) + valeur * facteur
    return effets


@dataclass(frozen=True)
class AnneeScenario:
    annee: int
    dette: Fourchette
    solde_primaire: Fourchette
    ecart_dette: Fourchette
    ecart_solde_primaire: Fourchette


def verifier_double_compte(mesures: Sequence[Mesure]) -> None:
    """Refuse deux mesures sur la même dépense fiscale, ou une dépense et tout son impôt.

    Le levier générique (somme des dépenses choisies sur le site) est admis une seule fois et
    jamais avec une dépense désignée par son numéro. Le site empêche lui-même de choisir une
    dépense d'un impôt dont le curseur n'est pas à zéro.
    """
    depenses = [d for d in (depense_du_levier(m.levier) for m in mesures) if d is not None]
    impots = {
        LEVIERS_DEPENSES_FISCALES_IMPOT[m.levier]
        for m in mesures
        if m.levier in LEVIERS_DEPENSES_FISCALES_IMPOT
    }
    codes = [d.code for d in depenses]
    if len(set(codes)) < len(codes) or any(d.impot in impots for d in depenses):
        msg = "double compte : une même dépense fiscale est visée par deux mesures"
        raise ValueError(msg)
    generiques = sum(m.levier == LEVIER_DEPENSE_FISCALE_UNITE for m in mesures)
    if generiques > 1 or (generiques and depenses):
        msg = "double compte : le levier générique regroupe déjà les dépenses choisies"
        raise ValueError(msg)
    leviers = [m.levier for m in mesures if m.levier in LEVIERS_DEPENSES_FISCALES_IMPOT]
    if len(set(leviers)) < len(leviers):
        msg = "double compte : un même impôt est visé par deux mesures"
        raise ValueError(msg)
    _verifier_credits(mesures)
    # Une mesure à zéro ne change rien : elle ne bloque aucune combinaison.
    reglees = [m for m in mesures if m.valeur != 0]
    remunerations_reglees = any(m.levier in LEVIERS_REMUNERATIONS for m in reglees)
    credits_regles = any(
        m.levier == LEVIER_CREDITS_UNITE or mission_du_levier(m.levier) is not None for m in reglees
    )
    if remunerations_reglees and credits_regles:
        # Les crédits de personnel de l'État sont dans les missions (option 4 (a)).
        msg = "double compte : les crédits des missions contiennent les rémunérations de l'État"
        raise ValueError(msg)
    indexation_reglee = any(m.levier in (LEVIER_INDEXATION, LEVIER_PA_PENTE) for m in reglees)
    solidarite_reglee = any(m.levier == levier_credits_mission(MISSION_SOLIDARITE) for m in reglees)
    if indexation_reglee and solidarite_reglee:
        msg = (
            "double compte : la mission « Solidarité, insertion et égalité des chances » "
            "finance l'AAH et la prime d'activité, visées par l'indexation ou la pente"
        )
        raise ValueError(msg)


def _verifier_credits(mesures: Sequence[Mesure]) -> None:
    """Une mission au plus une fois ; le levier générique (somme des missions réglées sur le
    site) au plus une fois par signe (hausses, baisses) et jamais avec une mission nommée."""
    missions = [m for m in (mission_du_levier(x.levier) for x in mesures) if m is not None]
    if len({m.identifiant for m in missions}) < len(missions):
        msg = "double compte : une même mission est visée par deux mesures"
        raise ValueError(msg)
    generiques = [m.valeur for m in mesures if m.levier == LEVIER_CREDITS_UNITE]
    hausses = sum(v > 0 for v in generiques)
    baisses = sum(v < 0 for v in generiques)
    if hausses > 1 or baisses > 1 or (generiques and missions):
        msg = "double compte : le levier générique regroupe déjà les missions réglées"
        raise ValueError(msg)


def categorie_croissance(levier: str) -> str:
    """Catégorie d'instruments dont le levier prend le multiplicateur (``fr_budget.croissance``).

    Choix du lot 3.2 (à relire) : le levier des dépenses fiscales de l'impôt sur le revenu suit
    l'impôt sur le revenu ; les autres dépenses fiscales, y compris celles choisies une à une
    (regroupées par le site dans le levier générique, quel que soit leur impôt), et l'impôt sur
    les sociétés suivent la catégorie « autres prélèvements » ; dotations, rémunérations et
    crédits des missions la dépense publique.
    """
    if depense_du_levier(levier) is not None:
        return module_croissance.AUTRES_PRELEVEMENTS
    if mission_du_levier(levier) is not None:
        return module_croissance.DEPENSES
    categories = {
        LEVIER_TVA_NORMAL: module_croissance.TVA,
        **dict.fromkeys(LEVIERS_ACCISES, module_croissance.ACCISES),
        **dict.fromkeys(LEVIERS_CSG, module_croissance.CSG),
        LEVIER_COTISATIONS_TAUX: module_croissance.COTISATIONS_EMPLOYEURS,
        LEVIER_ALLEGEMENTS: module_croissance.COTISATIONS_EMPLOYEURS,
        LEVIER_IR_SEUILS: module_croissance.IMPOT_REVENU,
        levier_depenses_fiscales_impot(
            IMPOT_REVENU_DEPENSES_FISCALES
        ): module_croissance.IMPOT_REVENU,
        LEVIER_INDEXATION: module_croissance.PRESTATIONS,
        LEVIER_PA_PENTE: module_croissance.PRESTATIONS,
        **dict.fromkeys(LEVIERS_REMUNERATIONS, module_croissance.DEPENSES),
        **dict.fromkeys(LEVIERS_DOTATIONS, module_croissance.DEPENSES),
        LEVIER_CREDITS_UNITE: module_croissance.DEPENSES,
        LEVIER_IS_TAUX_NORMAL: module_croissance.AUTRES_PRELEVEMENTS,
        LEVIER_IS_SURTAXE: module_croissance.AUTRES_PRELEVEMENTS,
        **dict.fromkeys(LEVIERS_DEPENSES_FISCALES_IMPOT, module_croissance.AUTRES_PRELEVEMENTS),
        LEVIER_DEPENSE_FISCALE_UNITE: module_croissance.AUTRES_PRELEVEMENTS,
    }
    if levier in categories:
        return categories[levier]
    msg = f"levier inconnu : {levier}"
    raise ValueError(msg)


def _trajectoire_mesures(
    trajectoire: Sequence[AnneeBaseline],
    mesures: Sequence[Mesure],
    borne_effet: str,
    borne_multiplicateur: str | None,
) -> list[AnneeBaseline]:
    """Trajectoire avec les mesures ; avec l'effet de croissance si ``borne_multiplicateur``
    désigne la borne du multiplicateur retenue pour toutes les mesures."""
    effets = _effets_par_annee(mesures, borne_effet)
    if borne_multiplicateur is None:
        return trajectoire_avec_effet(trajectoire, effets)
    annees = [a.annee for a in trajectoire]
    rho = module_croissance.persistance()
    ecart = [0.0] * len(annees)
    # L'écart de production est la somme de ceux de chaque mesure (multiplicateur propre).
    for m in mesures:
        multiplicateur = module_croissance.multiplicateur(categorie_croissance(m.levier))
        og = module_croissance.ecart_production(
            _effets_par_annee([m], borne_effet),
            annees,
            getattr(multiplicateur, borne_multiplicateur),
            rho,
        )
        ecart = [x + y for x, y in zip(ecart, og, strict=True)]
    return module_croissance.trajectoire_avec_croissance(
        trajectoire, effets, ecart, module_croissance.effet_sur_le_solde()
    )


CENTRAL = "central"
BORNES_EFFET = ("bas", "haut")


def _bornes(croissance: bool) -> list[tuple[str, str | None]]:
    """Couples (borne de l'effet, borne du multiplicateur) des trajectoires qui encadrent le
    scénario, hors centrale : effet bas et haut ; avec la croissance, s'y ajoutent les coins
    (effet bas ou haut, multiplicateur bas ou haut), le multiplicateur étant commun à toutes
    les mesures."""
    if not croissance:
        return [(b, None) for b in BORNES_EFFET]
    bornes: list[tuple[str, str | None]] = [(b, CENTRAL) for b in BORNES_EFFET]
    return bornes + [(b, j) for j in BORNES_EFFET for b in BORNES_EFFET]


def scenario(mesures: Sequence[Mesure], *, croissance: bool = False) -> list[AnneeScenario]:
    """Scénario 2025-2046 : niveaux et écarts à la baseline, en points de PIB, en fourchette.

    Plusieurs mesures s'additionnent (pas d'interaction entre leviers à ce stade). Deux
    mesures sur la même dépense fiscale sont refusées (``verifier_double_compte``). Avec
    ``croissance``, l'effet sur l'activité (``fr_budget.croissance``) s'ajoute ; il est
    désactivé par défaut.
    """
    verifier_double_compte(mesures)
    centrale, variantes = trajectoires()
    m_central = CENTRAL if croissance else None
    c_traj = _trajectoire_mesures(centrale, mesures, CENTRAL, m_central)
    autres_traj = [_trajectoire_mesures(centrale, mesures, b, j) for b, j in _bornes(croissance)]
    variantes_avec = [_trajectoire_mesures(v, mesures, CENTRAL, m_central) for v in variantes]
    resultat = []
    for i, ref in enumerate(centrale):
        c = c_traj[i]
        autres = [t[i] for t in autres_traj]
        ecarts_dette = [a.dette - ref.dette for a in autres]
        ecarts_solde = [a.solde_primaire - ref.solde_primaire for a in autres]
        resultat.append(
            AnneeScenario(
                annee=ref.annee,
                dette=encadrer(
                    c.dette, [a.dette for a in autres] + [v[i].dette for v in variantes_avec]
                ),
                solde_primaire=encadrer(
                    c.solde_primaire,
                    [a.solde_primaire for a in autres]
                    + [v[i].solde_primaire for v in variantes_avec],
                ),
                ecart_dette=encadrer(c.dette - ref.dette, ecarts_dette),
                ecart_solde_primaire=encadrer(c.solde_primaire - ref.solde_primaire, ecarts_solde),
            )
        )
    return resultat


def reponse_unitaire(levier: str, annee: int) -> list[AnneeScenario]:
    """Scénario d'une unité du levier entrée en vigueur en ``annee``.

    Le modèle est linéaire dans la valeur du levier : l'écart pour x unités vaut x fois cette
    réponse (le site statique s'en sert pour calculer sans serveur).
    """
    return scenario([Mesure(levier, 1.0, annee)])


LEVIERS_REGISTRE = {
    LEVIER_IS_TAUX_NORMAL: "impot_societes",
    LEVIER_IS_SURTAXE: "impot_societes",
    LEVIER_TVA_NORMAL: "tva",
    LEVIER_ACCISE_GAZOLE: "accises_energie",
    LEVIER_ACCISE_ESSENCES: "accises_energie",
    **dict.fromkeys(LEVIERS_DEPENSES_FISCALES_IMPOT, "depenses_fiscales"),
    LEVIER_DEPENSE_FISCALE_UNITE: "depenses_fiscales",
    LEVIER_CREDITS_UNITE: "credits_missions",
    **dict.fromkeys(LEVIERS_DOTATIONS, "dotations_collectivites"),
    **dict.fromkeys(LEVIERS_REMUNERATIONS, "remunerations_publiques"),
    LEVIER_INDEXATION: "indexation_pensions_prestations",
    **dict.fromkeys(LEVIERS_CSG, "csg"),
    LEVIER_COTISATIONS_TAUX: "cotisations_patronales",
    LEVIER_ALLEGEMENTS: "cotisations_patronales",
    LEVIER_IR_SEUILS: "impot_revenu",
    LEVIER_PA_PENTE: "minima_prime_activite",
}


def levier_registre(levier: str) -> str | None:
    """Levier du registre dont dépend un levier de scénario ; ``None`` s'il est inconnu."""
    if depense_du_levier(levier) is not None:
        return "depenses_fiscales"
    if mission_du_levier(levier) is not None:
        return "credits_missions"
    return LEVIERS_REGISTRE.get(levier)


HYPOTHESE_RENDEMENT = "scenario_rendement_constant_pib"
SOURCE_PIB = "insee_comptes_nationaux_2025"
# Sources et hypothèses propres à chaque levier (registres/sources.yaml, hypotheses.yaml) :
# pour la TVA, comptes et consommation de l'INSEE, taux d'OpenFisca-France, dépenses fiscales
# (tome II de Voies et Moyens), recettes servant au vieillissement du point (agrege.tva).
# Accises : ventes du SDES, masses volumiques de l'ADEME, tarifs (OpenFisca, guide 2026),
# remboursements (tome II de Voies et Moyens).
PROVENANCE_ACCISES = (
    (
        "sdes_conso_produits_petroliers",
        "ademe_base_carbone_pci_masse_volumique",
        "openfisca_france_176_1_2",
        "ministere_guide_fiscalite_energies_2026",
        "plf2026_voies_et_moyens_tome2",
    ),
    (accises.HYPOTHESE_MASSES,),
)
PROVENANCE_IS = (
    ("dgfip_statistiques_51_is_2025", "openfisca_france_176_1_2", "plf2025_evaluations_prealables"),
    (),
)
SOURCES_DEPENSES_FISCALES = (
    "plf2026_voies_et_moyens_tome2",
    "plf2025_voies_et_moyens_tome2",
    "plf2024_voies_et_moyens_tome2",
    "plf2027_resf",
)
SOURCES_CREDITS = (
    "db_budget_vert_plf2026",
    "dgfip_plrg_2023",
    "dgfip_plrg_2024",
    "dgfip_plrg_2025",
    "plf2027_resf",
)
PROVENANCE_DOTATIONS = (
    (
        "plf2026_voies_et_moyens_tome1",
        "plf2025_voies_et_moyens_tome1",
        "plf2024_voies_et_moyens_tome1",
        "ofgl_comptes_consolides_collectivites",
        "cdc_eclairages_8_dotations_investissement",
        "plf2027_resf",
    ),
    tuple(f"dotations_elasticite_investissement_{n}" for n in dotations.NIVEAUX),
)
PROVENANCE_REMUNERATIONS = (
    (
        "insee_comptes_nationaux_2025",
        "dgafp_rapport_annuel_2025",
        "openfisca_france_176_1_2",
        "senat_avis_plf2024_fonction_publique",
    ),
    (),
)
PROVENANCE_INDEXATION = (
    (
        "drees_comptes_protection_sociale_2025",
        "drees_eir_2020_distribution_pensions",
        "openfisca_france_176_1_2",
        "insee_comptes_nationaux_2025",
        "plf2027_resf",
        "plfss2026_projet_loi",
        "plfss2027_projet_loi",
        "senat_rapport_plfss2026_tome1",
    ),
    (),
)
PROVENANCE_CSG = (
    (
        "ccss_octobre_2026",
        "ccss_septembre_2018",
        "senat_rapport_plfss2026_tome1",
        "drees_eir_2020_distribution_pensions",
        "openfisca_france_176_1_2",
        "insee_comptes_nationaux_2025",
        "plf2027_resf",
    ),
    (),
)
PROVENANCE_COTISATIONS = (
    (
        "ccss_octobre_2026",
        "ccss_octobre_2025",
        "ccss_octobre_2024",
        "ccss_septembre_2018",
        "insee_comptes_nationaux_2025",
        "plf2027_resf",
    ),
    (),
)
PROVENANCE_IR = (
    (
        "plf2025_evaluations_prealables",
        "dgfip_statistiques_41",
        "openfisca_france_176_1_2",
        "senat_rapport_general_plf2026_tome1",
        "plfss2026_projet_loi",
        "insee_comptes_nationaux_2025",
        "plf2027_resf",
    ),
    (),
)
PROVENANCE_PA = (
    (
        "senat_note_presentation_siec_plf2026",
        "senat_rapport_special_siec_plf2026",
        "openfisca_france_176_1_2",
        "insee_comptes_nationaux_2025",
    ),
    (),
)
PROVENANCE_LEVIERS = {
    LEVIER_IS_TAUX_NORMAL: PROVENANCE_IS,
    LEVIER_IS_SURTAXE: PROVENANCE_IS,
    LEVIER_TVA_NORMAL: (
        (
            "insee_tes_2025",
            "insee_consommation_produits_2024",
            "openfisca_france_176_1_2",
            "plf2025_voies_et_moyens_tome2",
            "dgtresor_tresor_eco_371",
            "plf2026_voies_et_moyens_tome1",
        ),
        (HYPOTHESE_REPARTITION,),
    ),
    **dict.fromkeys(LEVIERS_ACCISES, PROVENANCE_ACCISES),
    **{
        levier: (SOURCES_DEPENSES_FISCALES, (f"depenses_fiscales_ecart_{impot}",))
        for levier, impot in LEVIERS_DEPENSES_FISCALES_IMPOT.items()
    },
    LEVIER_DEPENSE_FISCALE_UNITE: (SOURCES_DEPENSES_FISCALES, (HYPOTHESE_ECART_DEPENSE,)),
    LEVIER_CREDITS_UNITE: (SOURCES_CREDITS, (HYPOTHESE_ECART_CREDITS,)),
    **dict.fromkeys(LEVIERS_DOTATIONS, PROVENANCE_DOTATIONS),
    **dict.fromkeys(LEVIERS_REMUNERATIONS, PROVENANCE_REMUNERATIONS),
    LEVIER_INDEXATION: PROVENANCE_INDEXATION,
    **dict.fromkeys(LEVIERS_CSG, PROVENANCE_CSG),
    LEVIER_COTISATIONS_TAUX: PROVENANCE_COTISATIONS,
    LEVIER_ALLEGEMENTS: PROVENANCE_COTISATIONS,
    LEVIER_IR_SEUILS: PROVENANCE_IR,
    LEVIER_PA_PENTE: PROVENANCE_PA,
}


def _provenance_levier(levier: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if depense_du_levier(levier) is not None:
        return PROVENANCE_LEVIERS[LEVIER_DEPENSE_FISCALE_UNITE]
    if mission_du_levier(levier) is not None:
        return PROVENANCE_LEVIERS[LEVIER_CREDITS_UNITE]
    if levier not in PROVENANCE_LEVIERS:
        msg = f"levier inconnu : {levier}"
        raise ValueError(msg)
    return PROVENANCE_LEVIERS[levier]


def provenance(leviers: Iterable[str]) -> tuple[list[str], list[str]]:
    """Sources et hypothèses d'un scénario : baseline, PIB, puis celles de chaque levier."""
    sources = [*module_baseline.SOURCES, SOURCE_PIB]
    hypotheses = [*module_baseline.HYPOTHESES, HYPOTHESE_RENDEMENT]
    for levier in leviers:
        s, h = _provenance_levier(levier)
        sources += [x for x in s if x not in sources]
        hypotheses += [x for x in h if x not in hypotheses]
    return sources, hypotheses


"""Levier du registre (``registres/leviers.yaml``) dont chaque levier de scénario dépend."""


@dataclass(frozen=True)
class ReponseLineaire:
    """Réponse d'une unité du levier sur chaque trajectoire, pour un calcul sans serveur.

    ``base_dette`` et ``base_solde`` : niveaux sans mesure, une liste par trajectoire.
    ``unite_dette`` et ``unite_solde`` : écart dû à une unité du levier, mêmes trajectoires.
    Trajectoires : 0 = centrale avec effet central ; puis chaque variante de la baseline avec
    effet central ; puis la centrale avec l'effet bas et avec l'effet haut (indices
    ``indices_effet``). Pour x unités : niveau = base + x * unité ; écart = x * unité. Les
    bornes sont les extrêmes sur les trajectoires (niveaux) ou sur ``indices_effet`` (écarts).
    """

    annees: list[int]
    base_dette: list[list[float]]
    base_solde: list[list[float]]
    unite_dette: list[list[float]]
    unite_solde: list[list[float]]
    indices_effet: list[int]
    croissance_dette: list[list[float]]
    croissance_solde: list[list[float]]
    """Supplément dû à l'effet de croissance pour une unité du levier et un multiplicateur de 1,
    mêmes trajectoires : avec le multiplicateur m, l'écart vaut unité + m * supplément (le
    calcul est linéaire dans m)."""


def reponse_lineaire(levier: str, annee: int) -> ReponseLineaire:
    centrale, variantes = trajectoires()
    mesures = [Mesure(levier, 1.0, annee)]
    m_central = module_croissance.multiplicateur(categorie_croissance(levier)).central
    paires = [
        (centrale, CENTRAL),
        *((v, CENTRAL) for v in variantes),
        (centrale, "bas"),
        (centrale, "haut"),
    ]
    base_dette, base_solde, unite_dette, unite_solde = [], [], [], []
    croissance_dette, croissance_solde = [], []
    for trajectoire, borne in paires:
        avec = _trajectoire_mesures(trajectoire, mesures, borne, None)
        avec_croissance = _trajectoire_mesures(trajectoire, mesures, borne, CENTRAL)
        base_dette.append([a.dette for a in trajectoire])
        base_solde.append([a.solde_primaire for a in trajectoire])
        unite_dette.append([b.dette - a.dette for a, b in zip(trajectoire, avec, strict=True)])
        unite_solde.append(
            [b.solde_primaire - a.solde_primaire for a, b in zip(trajectoire, avec, strict=True)]
        )
        croissance_dette.append(
            [(c.dette - b.dette) / m_central for b, c in zip(avec, avec_croissance, strict=True)]
        )
        croissance_solde.append(
            [
                (c.solde_primaire - b.solde_primaire) / m_central
                for b, c in zip(avec, avec_croissance, strict=True)
            ]
        )
    n = len(paires)
    return ReponseLineaire(
        annees=[a.annee for a in centrale],
        base_dette=base_dette,
        base_solde=base_solde,
        unite_dette=unite_dette,
        unite_solde=unite_solde,
        indices_effet=[0, n - 2, n - 1],
        croissance_dette=croissance_dette,
        croissance_solde=croissance_solde,
    )
