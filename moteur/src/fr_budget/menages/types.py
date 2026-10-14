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

Retraité : pension moyenne de droit direct de fin 2023 (DREES, la médiane n'est pas publiée),
revalorisée comme les pensions de base (instructions de la DSS ; hypothèse
``menages_ecart_evolution_pension_moyenne``).

Indépendant : artisan dont le résultat fiscal est le revenu d'activité médian des non-salariés
classiques de 2023 (Insee), porté à l'année simulée comme le SMIC horaire brut ; cotisations
selon l'assiette réformée de 2025 (``fr_budget.menages.independants``), impôt par OpenFisca.

Non comptés : aides au logement (le loyer n'est pas fixé), taxe d'habitation, revenus du
patrimoine.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field
from functools import cache
from typing import Any

from openfisca_core.simulation_builder import SimulationBuilder
from openfisca_core.simulations import Simulation

from fr_budget.menages import independants
from fr_budget.menages.openfisca import HypothesesEmploi, smic_mensuel_brut, systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage, hypothese

ANNEE = 2025
ANNEE_INSEE = 2024
SMIC = "smic"
MEDIAN = "median"
P95 = "p95"
APPRENTI = "apprenti"
RETRAITE = "retraite"
INDEPENDANT = "independant"
REVENU_INSEE_INDEPENDANT = "insee_revenu_median_non_salaries_classiques_2023"
ANNEE_INSEE_INDEPENDANT = 2023
HYPOTHESE_INDEPENDANT = "menages_ecart_evolution_revenu_independant"
MOIS_PAR_AN = 12
PENSION_DREES = "drees_pension_brute_moyenne_droit_direct_2023"
ANNEE_DREES = 2023
# Coefficients de revalorisation des pensions de base au 1er janvier de l'année.
REVALORISATIONS = {
    2024: "dss_revalorisation_pensions_base_2024_01",
    2025: "dss_revalorisation_pensions_base_2025_01",
}
HYPOTHESE_PENSION = "menages_ecart_evolution_pension_moyenne"
# Point fixe du revenu fiscal de référence d'avant la période simulée (taux de CSG des
# pensions) : précision en euros et nombre d'itérations.
PRECISION_RFR = 1.0
ITERATIONS_RFR = 10
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
class Apprentissage:
    """Contrat d'apprentissage payé au salaire minimum légal (pourcentage du SMIC)."""

    contrat_debut: str
    """Date de début du contrat (« AAAA-MM-JJ ») ; pas de salaire avant."""
    parts_smic: tuple[str, ...]
    """Chiffrages des pourcentages du SMIC, par année d'exécution du contrat."""


@dataclass(frozen=True)
class Adulte:
    naissance: str
    niveau: str
    cadre: bool = False
    """Salarié cadre (cotisations des cadres) ; sinon non cadre, valeur par défaut d'OpenFisca."""
    apprentissage: Apprentissage | None = None
    """Apprenti (``niveau`` vaut alors ``APPRENTI``) : salaire et exonérations propres."""
    montant_mensuel: float | None = None
    """Montant saisi (profil de l'utilisateur), à la place du niveau statistique : salaire brut
    d'un salarié, pension brute d'un retraité, résultat fiscal d'un indépendant, par mois.
    Supposé constant sur toutes les années de la simulation."""

    @property
    def retraite(self) -> bool:
        return self.niveau == RETRAITE

    @property
    def independant(self) -> bool:
        return self.niveau == INDEPENDANT


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
    "apprenti_19_ans": Profil(
        "Apprenti de 19 ans, payé au minimum légal",
        (
            Adulte(
                "2006-01-01",
                APPRENTI,
                apprentissage=Apprentissage(
                    "2024-09-01",
                    (
                        "service_public_apprenti_18_20_ans_1re_annee",
                        "service_public_apprenti_18_20_ans_2e_annee",
                        "service_public_apprenti_18_20_ans_3e_annee",
                    ),
                ),
            ),
        ),
    ),
    "artisan": Profil(
        "Artisan, revenu médian des indépendants", (Adulte("1980-01-01", INDEPENDANT),)
    ),
    "retraite_seul": Profil(
        "Retraité seul, pension moyenne de droit direct", (Adulte("1955-01-01", RETRAITE),)
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
    pension_brute: float = 0.0
    """Pension de retraite brute (``retraite_brute``)."""
    pension_nette: float = 0.0
    """Pension nette de CSG, CRDS et CASA (``retraite_nette``)."""
    revenu_independant_brut: float = 0.0
    """Revenu brut d'un indépendant, avant cotisations et contributions sociales."""
    cotisations_independant: float = 0.0
    """Cotisations sociales obligatoires de l'indépendant, formation professionnelle comprise."""
    csg_crds_independant: float = 0.0
    revenu_independant_net: float = 0.0
    """Revenu après cotisations, CSG et CRDS."""

    @property
    def net_apres_impot(self) -> float:
        return (
            self.net_avant_impot
            + self.pension_nette
            + self.revenu_independant_net
            - self.impot_revenu
            + sum(self.prestations.values())
        )


@dataclass(frozen=True)
class Legislation:
    """Législation appliquée à la cascade : celle d'OpenFisca corrigée (par défaut) ou une
    réforme (effet d'un levier, ``fr_budget.menages.leviers``)."""

    systeme: Any = None
    """Système socio-fiscal réformé ; ``None`` pour le système de référence."""
    ecart_csg_activite: float = 0.0
    """Variation du taux de CSG déductible des revenus d'activité d'un indépendant, en
    fraction, à partir de l'année simulée (calculée hors d'OpenFisca)."""
    ecart_pension: float = 0.0
    """Variation de la pension d'un retraité, en fraction, sur l'année simulée (revalorisation
    de sa part de base, ``fr_budget.menages.leviers``)."""


REFERENCE = Legislation()


def _systeme(legislation: Legislation) -> Any:
    return legislation.systeme if legislation.systeme is not None else systeme_socio_fiscal()


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


def salaire_apprenti(apprentissage: Apprentissage, mois: str) -> float:
    """Salaire brut d'un mois : pourcentage du SMIC de l'année d'exécution du contrat
    (service-public.gouv.fr, fiche F2918), nul avant le début du contrat."""
    debut = apprentissage.contrat_debut[:7]
    if mois < debut:
        return 0.0
    ecart = (int(mois[:4]) - int(debut[:4])) * 12 + int(mois[5:]) - int(debut[5:])
    annee_contrat = ecart // 12
    if annee_contrat >= len(apprentissage.parts_smic):
        # Pas de taux pour cette année d'exécution : le contrat est terminé, le profil ne
        # s'applique plus (on ne prolonge pas le dernier taux).
        msg = f"{mois} : au-delà des {len(apprentissage.parts_smic)} années du contrat"
        raise ValueError(msg)
    part = chiffrage(apprentissage.parts_smic[annee_contrat])
    return part * smic_mensuel_brut(mois)


def pension_brute_mensuelle(annee: int) -> float:
    """Pension brute mensuelle du retraité type pour ``annee`` : pension moyenne de droit
    direct de fin 2023 (DREES), revalorisée au 1er janvier de chaque année suivante comme les
    pensions de base. Pas de valeur avant 2023 ni sans coefficient de revalorisation sourcé."""
    if annee < ANNEE_DREES:
        msg = f"{annee} : pension du retraité type non définie avant {ANNEE_DREES}"
        raise ValueError(msg)
    pension = chiffrage(PENSION_DREES)
    for a in range(ANNEE_DREES + 1, annee + 1):
        if a not in REVALORISATIONS:
            msg = f"{a} : coefficient de revalorisation des pensions non saisi"
            raise ValueError(msg)
        pension *= chiffrage(REVALORISATIONS[a])
    if annee > ANNEE_DREES:
        pension *= 1 + hypothese(HYPOTHESE_PENSION).valeur_centrale
    return pension


def resultat_fiscal_independant(annee: int) -> float:
    """Résultat fiscal annuel de l'artisan type : revenu d'activité médian des non-salariés
    classiques de 2023 (Insee, net de cotisations sociales), porté à ``annee`` comme le SMIC
    horaire brut au 1er janvier (hypothèse ``menages_ecart_evolution_revenu_independant``)."""
    rapport = independants.smic_horaire(annee) / independants.smic_horaire(ANNEE_INSEE_INDEPENDANT)
    ecart = hypothese(HYPOTHESE_INDEPENDANT).valeur_centrale
    return chiffrage(REVENU_INSEE_INDEPENDANT) * MOIS_PAR_AN * rapport * (1 + ecart)


def _resultat_fiscal_reference(adulte: Adulte, annee: int) -> float:
    if adulte.montant_mensuel is not None:
        return adulte.montant_mensuel * MOIS_PAR_AN
    return resultat_fiscal_independant(annee)


def _cotisations_independant(
    adulte: Adulte, annee: int, ecart_csg: float
) -> independants.CotisationsIndependant:
    """Cotisations de l'indépendant ; sous un écart de CSG, le revenu brut (avant cotisations)
    reste celui de la législation de référence et le résultat fiscal change."""
    brut = independants.revenu_brut_pour_resultat(_resultat_fiscal_reference(adulte, annee), annee)
    return independants.cotisations_artisan(brut, annee, ecart_csg)


def _resultat_fiscal(adulte: Adulte, annee: int, ecart_csg: float = 0.0) -> float:
    if ecart_csg == 0:
        return _resultat_fiscal_reference(adulte, annee)
    return _cotisations_independant(adulte, annee, ecart_csg).resultat_fiscal


def _salaires(
    adulte: Adulte,
    annee: int,
    mois: list[str],
    ecart_csg: float = 0.0,
    ecart_pension: float = 0.0,
) -> dict[str, Any]:
    """Salaire de base des ``mois``, pour un apprenti son contrat, pour un retraité sa
    pension (sans salaire), changée de ``ecart_pension`` sur l'année simulée seulement."""
    montant = adulte.montant_mensuel
    if adulte.retraite:

        def pension(m: str) -> float:
            p = montant if montant is not None else pension_brute_mensuelle(int(m[:4]))
            return p * (1 + ecart_pension) if int(m[:4]) == annee else p

        return {"retraite_brute": {m: pension(m) for m in mois}}
    if adulte.independant:
        # Résultat fiscal (bénéfice industriel et commercial) pour l'impôt ; les cotisations
        # sont calculées hors d'OpenFisca (fr_budget.menages.independants).
        annees = sorted({int(m[:4]) for m in mois})
        # L'écart de CSG d'un levier ne s'applique qu'à l'année simulée.
        revenu = {
            str(a): _resultat_fiscal(adulte, annee, ecart_csg if a == annee else 0.0)
            for a in annees
        }
        # rpns_imposables pour l'impôt ; rpns_autres_revenus pour les ressources du RSA et de
        # la prime d'activité, qu'OpenFisca lit dans cette variable pour un non-salarié.
        return {"rpns_imposables": revenu, "rpns_autres_revenus": revenu}
    if montant is not None:
        return {"salaire_de_base": dict.fromkeys(mois, montant)}
    if adulte.apprentissage is None:
        return {
            "salaire_de_base": dict.fromkeys(mois, brut_mensuel(adulte.niveau, annee, adulte.cadre))
        }
    contrat = adulte.apprentissage
    sous_contrat = [m for m in mois if m >= contrat.contrat_debut[:7]]
    return {
        "salaire_de_base": {m: salaire_apprenti(contrat, m) for m in mois},
        "apprenti": dict.fromkeys(sous_contrat, True),
        # OpenFisca calcule sa propre rémunération d'apprenti (pourcentages du SMIC antérieurs
        # à ceux de la fiche F2918) et l'ajoute au salaire de base : elle est neutralisée.
        "remuneration_apprenti": dict.fromkeys(mois, 0.0),
        "apprentissage_contrat_debut": dict.fromkeys(sous_contrat, contrat.contrat_debut),
    }


def _avec_retraite(profil: Profil) -> bool:
    return any(a.retraite for a in profil.adultes)


def situation(
    profil: Profil,
    annee: int = ANNEE,
    rfr_anterieur: float | None = None,
    ecart_csg_independant: float = 0.0,
    ecart_pension: float = 0.0,
) -> dict[str, Any]:
    """Situation OpenFisca du ménage : salaires de l'année et de la précédente, déclaration
    commune pour un couple (marié), enfants à charge.

    Retraité : pensions des deux années précédentes aussi, car le taux de CSG d'une pension
    dépend du revenu fiscal de référence de l'avant-dernière année. Ce revenu dépend à son
    tour de la CSG : pour arrêter la chaîne, le revenu fiscal de référence des années
    ``annee - 4`` et ``annee - 3`` est donné (``rfr_anterieur``, voir :func:`_simulation`).
    """
    retraite = _avec_retraite(profil)
    mois = (_mois(annee - 2) if retraite else []) + _mois(annee - 1) + _mois(annee)
    individus: dict[str, Any] = {}
    adultes = []
    for i, a in enumerate(profil.adultes):
        nom = f"adulte_{i + 1}"
        adultes.append(nom)
        individus[nom] = {
            "date_naissance": {"ETERNITY": a.naissance},
            **_salaires(a, annee, mois, ecart_csg_independant, ecart_pension),
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
    if retraite and rfr_anterieur is not None:
        foyer["rfr"] = {str(annee - 4): rfr_anterieur, str(annee - 3): rfr_anterieur}
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


def _construire(
    profil: Profil,
    annee: int,
    rfr_anterieur: float | None,
    legislation: Legislation = REFERENCE,
) -> Simulation:
    simulation = SimulationBuilder().build_from_entities(
        _systeme(legislation),
        situation(
            profil, annee, rfr_anterieur, legislation.ecart_csg_activite, legislation.ecart_pension
        ),
    )
    if _avec_retraite(profil):
        # OpenFisca met à zéro une variable demandée pour une autre période au cours de son
        # propre calcul (spirale) : le revenu fiscal de référence des années précédentes est
        # calculé d'abord, pour que le taux de CSG des pensions ne dépende pas de l'ordre des
        # calculs.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            simulation.calculate("rfr", str(annee - 2))
            simulation.calculate("rfr", str(annee - 1))
    return simulation


@cache
def _rfr_point_fixe(identifiant: str, annee: int) -> float | None:
    return rfr_point_fixe(PROFILS[identifiant], annee)


def rfr_point_fixe(profil: Profil, annee: int) -> float | None:
    """Revenu fiscal de référence donné pour les années ``annee - 4`` et ``annee - 3`` d'un
    ménage de retraités : celui que le modèle calcule pour ``annee - 2`` quand on le lui
    donne (point fixe), soit une pension supposée stable avant la période simulée."""
    if not _avec_retraite(profil):
        return None
    rfr = 0.0
    for _ in range(ITERATIONS_RFR):
        simulation = _construire(profil, annee, rfr)
        nouveau = float(simulation.calculate("rfr", str(annee - 2))[0])
        if abs(nouveau - rfr) < PRECISION_RFR:
            return nouveau
        rfr = nouveau
    msg = f"{profil.libelle} : revenu fiscal de référence sans point fixe"
    raise RuntimeError(msg)


def _simulation(identifiant: str, annee: int) -> Simulation:
    return _construire(PROFILS[identifiant], annee, _rfr_point_fixe(identifiant, annee))


@cache
def cascade_annuelle(identifiant: str, annee: int = ANNEE) -> CascadeMenage:
    """Cascade annuelle d'un ménage type, en euros (revenus de ``annee``)."""
    return _cascade(PROFILS[identifiant], annee, _simulation(identifiant, annee))


def cascade_profil(
    profil: Profil, annee: int = ANNEE, legislation: Legislation = REFERENCE
) -> CascadeMenage:
    """Cascade annuelle d'un profil quelconque (profil saisi par l'utilisateur).

    Sans cache : aucune donnée saisie ne reste en mémoire après le calcul (règle 5). Le revenu
    fiscal de référence d'avant la période est celui de la législation de référence : une
    réforme ne s'applique qu'à partir de l'année simulée.
    """
    simulation = _construire(profil, annee, rfr_point_fixe(profil, annee), legislation)
    return _cascade(profil, annee, simulation, legislation)


def cascade_type_reformee(
    identifiant: str, legislation: Legislation, annee: int = ANNEE
) -> CascadeMenage:
    """Cascade annuelle d'un ménage type sous une législation réformée."""
    profil = PROFILS[identifiant]
    simulation = _construire(profil, annee, _rfr_point_fixe(identifiant, annee), legislation)
    return _cascade(profil, annee, simulation, legislation)


def _cascade(
    profil: Profil, annee: int, simulation: Simulation, legislation: Legislation = REFERENCE
) -> CascadeMenage:

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
        net_imposable=total("revenu_assimile_salaire", [str(annee)]),
        impot_revenu=-total("impot_revenu_restant_a_payer", [str(annee)]),
        prestations={k: v for k, v in prestations.items() if v},
        pension_brute=total("retraite_brute", mois),
        pension_nette=total("retraite_nette", mois),
        **_independant(profil, annee, legislation.ecart_csg_activite),
    )


def _independant(profil: Profil, annee: int, ecart_csg: float = 0.0) -> dict[str, float]:
    """Lignes de l'indépendant (revenu brut, cotisations, CSG-CRDS, revenu net)."""
    lignes = dict.fromkeys(
        (
            "revenu_independant_brut",
            "cotisations_independant",
            "csg_crds_independant",
            "revenu_independant_net",
        ),
        0.0,
    )
    for adulte in profil.adultes:
        if not adulte.independant:
            continue
        c = _cotisations_independant(adulte, annee, ecart_csg)
        lignes["revenu_independant_brut"] += c.revenu_brut
        lignes["cotisations_independant"] += c.cotisations
        lignes["csg_crds_independant"] += c.csg_crds
        lignes["revenu_independant_net"] += c.revenu_net
    return lignes if lignes["revenu_independant_brut"] else {}


def declaration(identifiant: str, annee: int = ANNEE) -> dict[str, Any]:
    """Cases de la déclaration des revenus de ``annee`` pour le ménage type, au format du
    simulateur d'impots.gouv.fr (validation) : situation, années de naissance, enfants à
    charge, case T, salaires et pensions imposables arrondis à l'euro."""
    profil = PROFILS[identifiant]
    simulation = _simulation(identifiant, annee)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        # Revenu imposé comme des salaires : salaire imposable, moins la part exonérée du
        # salaire d'un apprenti (correction apprenti_impot_revenu).
        salaires = simulation.calculate("revenu_assimile_salaire", str(annee))
        pensions = simulation.calculate_add("retraite_imposable", str(annee))
    cases: dict[str, Any] = {
        "situation": "M" if len(profil.adultes) > 1 else "C",
        "0DA": profil.adultes[0].naissance[:4],
        "0CF": len(profil.enfants),
        "1AJ": round(float(salaires[0])),
    }
    if profil.adultes[0].retraite:
        cases["1AS"] = round(float(pensions[0]))
    if profil.adultes[0].independant:
        # Bénéfice industriel et commercial professionnel, régime réel (case 5KC) ; pas de
        # salaire déclaré.
        del cases["1AJ"]
        cases["5KC"] = round(resultat_fiscal_independant(annee))
    if len(profil.adultes) > 1:
        cases["0DB"] = profil.adultes[1].naissance[:4]
        cases["1BJ"] = round(float(salaires[1]))
    if profil.parent_isole:
        cases["0BT"] = True
    return cases


def revenu_fiscal_et_parts(identifiant: str, annee: int = ANNEE) -> tuple[float, float]:
    """Revenu fiscal de référence (``rfr``) et nombre de parts (``nbptr``) du ménage type."""
    simulation = _simulation(identifiant, annee)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return (
            float(simulation.calculate("rfr", str(annee))[0]),
            float(simulation.calculate("nbptr", str(annee))[0]),
        )
