"""Moteur de barème de l'impôt sur le revenu : impôt de n'importe quel barème (nombre de
tranches, seuils et taux), et effet d'un changement de barème.

Plan validé par le mainteneur le 5 novembre 2026 (``docs/fiches/bareme_ir.md``, choix à relire).

Répartition des foyers (sans micro-données) : déciles de revenu fiscal de référence (RFR) par
part publiés par la DGFiP pour chaque année de revenus
(``data/processed/impot_revenu/deciles_rfr_part.csv``). Le RFR par part sert de quotient
familial (revenu imposable par part).

- Dixièmes 1 à 9 : quotient réparti uniformément entre les bornes du dixième.
- Dernier dixième : trois segments (hors dernier centième, dernier centième hors dernier
  millième, dernier millième), chacun réparti selon une loi de Pareto dont le paramètre redonne
  le RFR moyen par part publié pour 2024
  (``data/processed/impot_revenu/deciles_rfr_part_2024.csv``). Pour une autre année, les bornes
  du haut sont celles de 2024 multipliées par le rapport des bornes du dernier dixième.
- Parts par foyer : nombre de parts moyen de chaque dixième en 2024, supposé stable.

Calage (2024 seulement) : pour chaque segment, le rapport entre l'impôt au barème moyen par part
publié et l'impôt par part calculé avec le barème de 2024. Il absorbe l'écart entre RFR et
revenu imposable, la décote et le plafonnement du quotient familial, supposés agir de la même
façon sur un changement de barème. Variante pour la fourchette : un seul rapport pour
l'ensemble des segments.

Effet d'une réforme sur l'année ``annee`` : somme, sur les segments, de foyers x parts x rapport
de calage x écart moyen d'impôt par part entre le nouveau barème et la référence.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Callable
from dataclasses import dataclass
from functools import cache

from fr_budget.agrege.indexation import facteur_pib
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage
from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "impot_revenu"
FICHIER = DOSSIER / "deciles_rfr_part.csv"
FICHIER_2024 = DOSSIER / "deciles_rfr_part_2024.csv"
ANNEE_CALAGE = 2024
ANNEE_DECOTE_COUPLE = 2014
ANNEE_REDUCTION = (2016, 2019)
"""Années de revenus de la réduction d'impôt sous condition de revenus (OpenFisca)."""
"""Première année de revenus de la décote à seuils célibataire et couple (OpenFisca)."""
DIXIEMES = 10
PART_CENTIEME = 0.1
"""Part du dernier dixième dans le dernier centième, et du dernier centième dans le dernier
millième (définitions de la DGFiP)."""
DIXIEME = 0.1
"""Part des foyers dans un dixième."""
POINTS = 400
"""Points d'intégration par segment (règle du point milieu sur les quantiles)."""
EUROS_PAR_MILLIARD = 1e9
MILLIER = 1000.0
POURCENT = 100.0
SEUIL_CALAGE = 1.0
"""Impôt modélisé par part (euros) sous lequel un segment n'est pas calé (rapport 1)."""
TAUX_MAXIMUM = 1.0


@dataclass(frozen=True)
class Decote:
    """Décote de l'impôt des foyers faiblement imposés (OpenFisca, ``plaf_qf.decote``).

    Depuis les revenus de 2014 : ``seuil - taux x impôt`` (seuil célibataire ou couple).
    Avant (``ancienne``) : ``taux x (seuil - impôt)``, même seuil pour tous les foyers."""

    seuil_celibataire: float
    seuil_couple: float
    taux: float
    ancienne: bool = False

    def montant(self, impot: float, couple: bool) -> float:
        seuil = self.seuil_couple if couple else self.seuil_celibataire
        brut = self.taux * (seuil - impot) if self.ancienne else seuil - self.taux * impot
        return min(impot, max(0.0, brut))

    def indexee(self, facteur: float) -> Decote:
        return Decote(
            self.seuil_celibataire * facteur, self.seuil_couple * facteur, self.taux, self.ancienne
        )


@dataclass(frozen=True)
class ReductionSousCondition:
    """Réduction d'impôt sous condition de revenus, revenus 2016 à 2019 (OpenFisca,
    ``reduction_ss_condition_revenus``) : ``taux`` de l'impôt après décote si le RFR est sous le
    premier plafond, dégressive jusqu'au second."""

    taux: float
    plafond_celibataire: float
    plafond_couple: float
    majoration_demi_part: float

    def montant(self, impot: float, rfr: float, parts: float, couple: bool) -> float:
        adultes = 2.0 if couple else 1.0
        majoration = self.majoration_demi_part * 2 * max(0.0, parts - adultes)
        plafond1 = self.plafond_celibataire * adultes + majoration
        plafond2 = self.plafond_couple * adultes + majoration
        if rfr < plafond1:
            return self.taux * impot
        if rfr < plafond2:
            return self.taux * impot * (plafond2 - rfr) / (plafond2 - plafond1)
        return 0.0


@dataclass(frozen=True)
class Bareme:
    """Barème progressif : ``taux[i]`` s'applique entre ``seuils[i]`` et ``seuils[i + 1]`` ;
    décote facultative."""

    seuils: tuple[float, ...]
    taux: tuple[float, ...]
    decote: Decote | None = None
    reduction: ReductionSousCondition | None = None

    def __post_init__(self) -> None:
        if len(self.seuils) != len(self.taux) or not self.seuils:
            msg = "autant de seuils que de taux"
            raise ValueError(msg)
        if self.seuils[0] != 0.0:
            msg = "le premier seuil vaut 0"
            raise ValueError(msg)
        if any(b <= a for a, b in zip(self.seuils, self.seuils[1:], strict=False)):
            msg = "seuils strictement croissants"
            raise ValueError(msg)
        if any(not 0.0 <= t <= TAUX_MAXIMUM for t in self.taux):
            msg = "taux compris entre 0 et 1"
            raise ValueError(msg)


def impot_par_part(bareme: Bareme, quotient: float) -> float:
    """Impôt d'une part au barème, sans décote ni plafonnement, en euros."""
    hauts = (*bareme.seuils[1:], math.inf)
    return sum(
        t * max(0.0, min(quotient, h) - s)
        for s, h, t in zip(bareme.seuils, hauts, bareme.taux, strict=True)
    )


@cache
def bareme_openfisca(annee: int) -> Bareme:
    """Barème et décote des revenus de ``annee`` (OpenFisca, ``bareme_ir_depuis_1945.bareme``
    et ``calcul_impot_revenu.plaf_qf.decote``)."""
    p = systeme_socio_fiscal().parameters(f"{annee}-01-01").impot_revenu
    b = p.bareme_ir_depuis_1945.bareme
    d = p.calcul_impot_revenu.plaf_qf.decote
    if annee < ANNEE_DECOTE_COUPLE:
        decote = Decote(float(d.seuil), float(d.seuil), float(d.taux), ancienne=True)
    else:
        decote = Decote(float(d.seuil_celib), float(d.seuil_couple), float(d.taux))
    reduction = None
    if ANNEE_REDUCTION[0] <= annee <= ANNEE_REDUCTION[1]:
        r = p.calcul_impot_revenu.plaf_qf.reduction_ss_condition_revenus
        reduction = ReductionSousCondition(
            float(r.taux),
            float(r.plafond_rfr_celib),
            float(r.plafond_rfr_couple),
            float(r.majoration_plafond_par_demi_parts_supp),
        )
    return Bareme(
        tuple(float(s) for s in b.thresholds),
        tuple(float(t) for t in b.rates),
        decote,
        reduction,
    )


@dataclass(frozen=True)
class Segment:
    nom: str
    foyers: float
    """Part des foyers du segment (dixième : 0,1)."""
    parts: float
    quotients: tuple[float, ...]
    """Quotients aux points d'intégration, en euros."""
    rang: tuple[float, float] = (0.0, 1.0)
    """Place du segment parmi les foyers (fractions de la population)."""


@cache
def _deciles() -> dict[int, dict[int, dict[str, str]]]:
    with FICHIER.open(encoding="utf-8") as f:
        lignes = list(csv.DictReader(f))
    resultat: dict[int, dict[int, dict[str, str]]] = {}
    for lg in lignes:
        resultat.setdefault(int(lg["annee"]), {})[int(lg["decile"])] = lg
    return resultat


@cache
def _detail_2024() -> dict[str, dict[str, float]]:
    with FICHIER_2024.open(encoding="utf-8") as f:
        return {
            lg["segment"]: {k: float(v) for k, v in lg.items() if k != "segment" and v}
            for lg in csv.DictReader(f)
        }


def nombre_foyers(annee: int) -> float:
    return float(_deciles()[annee][1]["nombre_foyers"])


def _uniforme(bas: float, haut: float) -> tuple[float, ...]:
    return tuple(bas + (haut - bas) * (i + 0.5) / POINTS for i in range(POINTS))


def _pareto_moyenne(alpha: float, bas: float, haut: float) -> float:
    """Moyenne d'une loi de Pareto de paramètre ``alpha`` tronquée à [bas, haut]."""
    if math.isinf(haut):
        return float(alpha * bas / (alpha - 1))
    r = bas / haut
    return float(alpha * bas * (1 - r ** (alpha - 1)) / ((alpha - 1) * (1 - r**alpha)))


def _alpha(moyenne: float, bas: float, haut: float) -> float:
    """Paramètre de Pareto qui redonne ``moyenne`` sur [bas, haut] (dichotomie)."""
    lo, hi = 1.0001, 50.0
    for _ in range(200):
        milieu = (lo + hi) / 2
        if _pareto_moyenne(milieu, bas, haut) > moyenne:
            lo = milieu
        else:
            hi = milieu
    return (lo + hi) / 2


def _pareto(alpha: float, bas: float, haut: float) -> tuple[float, ...]:
    """Quantiles au point milieu d'une loi de Pareto tronquée."""
    tronque = 0.0 if math.isinf(haut) else (bas / haut) ** alpha
    return tuple(
        bas * (1 - (i + 0.5) / POINTS * (1 - tronque)) ** (-1 / alpha) for i in range(POINTS)
    )


def _haut_2024() -> list[tuple[str, float, float, float, float]]:
    """Segments du dernier dixième en 2024 : nom, part des foyers, borne basse, borne haute,
    RFR moyen par part."""
    d = _detail_2024()
    b10, c, m = d["10"]["borne_inferieure"], d["centieme"], d["millieme"]
    moy10, moyc, moym = d["10"]["rfr_part_moyen"], c["rfr_part_moyen"], m["rfr_part_moyen"]
    p = PART_CENTIEME
    reste = 1 - p
    return [
        (
            "10_hors_centieme",
            DIXIEME * reste,
            b10,
            c["borne_inferieure"],
            (moy10 - p * moyc) / reste,
        ),
        (
            "centieme_hors_millieme",
            DIXIEME * p * reste,
            c["borne_inferieure"],
            m["borne_inferieure"],
            (moyc - p * moym) / reste,
        ),
        ("millieme", DIXIEME * p * p, m["borne_inferieure"], math.inf, moym),
    ]


def _parts_haut() -> dict[str, float]:
    d = _detail_2024()
    p = PART_CENTIEME
    return {
        "10_hors_centieme": (d["10"]["parts_moyen"] - p * d["centieme"]["parts_moyen"]) / (1 - p),
        "centieme_hors_millieme": (d["centieme"]["parts_moyen"] - p * d["millieme"]["parts_moyen"])
        / (1 - p),
        "millieme": d["millieme"]["parts_moyen"],
    }


@cache
def _segments_bruts(annee: int) -> tuple[Segment, ...]:
    """Segments de l'année ``annee`` avant la correction du haut (RFR par part)."""
    deciles = _deciles()[annee]
    detail = _detail_2024()
    resultat = []
    for d in range(1, DIXIEMES):
        lg = deciles[d]
        bas = float(lg["borne_inferieure"] or 0.0)
        haut = float(lg["borne_superieure"])
        rang = ((d - 1) * DIXIEME, d * DIXIEME)
        resultat.append(
            Segment(str(d), DIXIEME, detail[str(d)]["parts_moyen"], _uniforme(bas, haut), rang)
        )
    echelle = float(deciles[DIXIEMES]["borne_inferieure"]) / detail["10"]["borne_inferieure"]
    parts = _parts_haut()
    debut = 1 - DIXIEME
    for nom, part, bas, haut, moyenne in _haut_2024():
        alpha = _alpha(moyenne, bas, haut)
        quotients = tuple(q * echelle for q in _pareto(alpha, bas, haut))
        resultat.append(Segment(nom, part, parts[nom], quotients, (debut, debut + part)))
        debut += part
    return tuple(resultat)


def _corriger(segment: Segment, borne: float, gamma: float) -> Segment:
    """Quotients au-dessus de ``borne`` ramenés à ``borne x (q / borne) ** gamma``."""
    quotients = tuple(q if q <= borne else borne * (q / borne) ** gamma for q in segment.quotients)
    return Segment(segment.nom, segment.foyers, segment.parts, quotients, segment.rang)


def _foyers_au_dessus(segs: tuple[Segment, ...], seuil: float, annee: int) -> float:
    n = nombre_foyers(annee)
    return sum(n * s.foyers * sum(q > seuil for q in s.quotients) / len(s.quotients) for s in segs)


@cache
def correction_haut() -> float:
    """Exposant de la correction du haut : en 2024, le nombre de foyers au-dessus du seuil de la
    tranche à 45 % redonne celui de la DGFiP (foyers par taux marginal). Le RFR des foyers les
    plus aisés comprend des revenus imposés hors barème (prélèvement forfaitaire unique) : le
    RFR par part surestime leur quotient familial."""
    segs = _segments_bruts(ANNEE_CALAGE)
    borne = float(_deciles()[ANNEE_CALAGE][DIXIEMES]["borne_inferieure"])
    seuil = bareme_openfisca(ANNEE_CALAGE).seuils[-1]
    cible = chiffrage("ir_foyers_tranche_45_2024") * MILLIER
    lo, hi = 0.3, 1.0
    for _ in range(60):
        gamma = (lo + hi) / 2
        corriges = tuple(_corriger(s, borne, gamma) for s in segs)
        if _foyers_au_dessus(corriges, seuil, ANNEE_CALAGE) > cible:
            hi = gamma
        else:
            lo = gamma
    return (lo + hi) / 2


@cache
def segments(annee: int) -> tuple[Segment, ...]:
    """Répartition des foyers de l'année de revenus ``annee`` en segments de quotient, haut de
    la répartition corrigé (``correction_haut``)."""
    borne = float(_deciles()[annee][DIXIEMES]["borne_inferieure"])
    return tuple(_corriger(s, borne, correction_haut()) for s in _segments_bruts(annee))


COUPLES_PAR_QUANTILE = (
    (0.0, 0.25, "ir_couples_quartile_1_2022"),
    (0.25, 0.5, "ir_couples_quartile_2_2022"),
    (0.5, 0.75, "ir_couples_quartile_3_2022"),
    (0.75, 0.9, "ir_couples_quartile_3_decile_9_2022"),
    (0.9, 0.999, "ir_couples_decile_9_centile_99_9_2022"),
    (0.999, 1.0, "ir_couples_tres_hauts_revenus_2022"),
)
"""Part des foyers mariés ou pacsés par quantile de revenu (DGFiP Analyses n° 08, tableau 3)."""
COUPLES_ENSEMBLE = "ir_couples_ensemble_2022"
REPARTITION, UNIFORME = "repartition", "uniforme"


def part_couples(segment: Segment, variante: str = REPARTITION) -> float:
    """Part des foyers mariés ou pacsés du segment : quantiles de revenu de la DGFiP appliqués
    au rang du segment (valeur centrale), ou part de l'ensemble (variante)."""
    if variante == UNIFORME:
        return chiffrage(COUPLES_ENSEMBLE) / POURCENT
    bas, haut = segment.rang
    total = 0.0
    for debut, fin, ident in COUPLES_PAR_QUANTILE:
        recouvrement = max(0.0, min(haut, fin) - max(bas, debut))
        total += recouvrement * chiffrage(ident) / POURCENT
    return total / (haut - bas)


def _impot_foyer(bareme: Bareme, quotient: float, parts: float, couple: bool) -> float:
    """Impôt d'un foyer après décote et réduction sous condition de revenus, en euros (le RFR
    du foyer est le quotient multiplié par les parts)."""
    impot = parts * impot_par_part(bareme, quotient)
    if bareme.decote is not None:
        impot -= bareme.decote.montant(impot, couple)
    if bareme.reduction is not None:
        impot -= bareme.reduction.montant(impot, quotient * parts, parts, couple)
    return impot


def _impot_moyen(bareme: Bareme, segment: Segment, couples: float) -> float:
    """Impôt moyen par part du segment, décote et réduction comprises, en euros."""
    p = segment.parts
    total = 0.0
    for q in segment.quotients:
        total += couples * _impot_foyer(bareme, q, p, True)
        total += (1 - couples) * _impot_foyer(bareme, q, p, False)
    return total / (p * len(segment.quotients))


def _impot_publie_par_part() -> dict[str, float]:
    """Impôt au barème moyen par part publié pour 2024, par segment, en euros."""
    d = _detail_2024()
    p = PART_CENTIEME
    publie = {str(k): d[str(k)]["impot_bareme_part_moyen"] for k in range(1, DIXIEMES)}
    i10, ic, im = (d[k]["impot_bareme_part_moyen"] for k in ("10", "centieme", "millieme"))
    publie["10_hors_centieme"] = (i10 - p * ic) / (1 - p)
    publie["centieme_hors_millieme"] = (ic - p * im) / (1 - p)
    publie["millieme"] = im
    return publie


@cache
def calage(couples: str = REPARTITION) -> dict[str, float]:
    """Rapport, par segment, entre l'impôt au barème publié et l'impôt modélisé (2024)."""
    bareme = bareme_openfisca(ANNEE_CALAGE)
    publie = _impot_publie_par_part()
    rapports = {}
    for s in segments(ANNEE_CALAGE):
        modele = _impot_moyen(bareme, s, part_couples(s, couples))
        rapports[s.nom] = publie[s.nom] / modele if modele > SEUIL_CALAGE else 1.0
    return rapports


@cache
def calage_global(couples: str = REPARTITION) -> float:
    """Variante : un seul rapport pour l'ensemble (2024)."""
    bareme = bareme_openfisca(ANNEE_CALAGE)
    publie = _impot_publie_par_part()
    segs = segments(ANNEE_CALAGE)
    total_publie = sum(s.foyers * s.parts * publie[s.nom] for s in segs)
    total_modele = sum(
        s.foyers * s.parts * _impot_moyen(bareme, s, part_couples(s, couples)) for s in segs
    )
    return total_publie / total_modele


def _total(annee: int, f: Callable[[Segment], float], rapport: Callable[[Segment], float]) -> float:
    n = nombre_foyers(annee)
    return sum(n * s.foyers * s.parts * rapport(s) * f(s) for s in segments(annee))


def impot_modele(bareme: Bareme, annee: int) -> float:
    """Impôt au barème de tous les foyers, en Md€ (calage par segment)."""
    k = calage()
    return (
        _total(annee, lambda s: _impot_moyen(bareme, s, part_couples(s)), lambda s: k[s.nom])
        / EUROS_PAR_MILLIARD
    )


def impot_bareme_publie_2024() -> float:
    """Impôt au barème publié pour 2024, reconstitué par segment, en Md€."""
    publie = _impot_publie_par_part()
    n = nombre_foyers(ANNEE_CALAGE)
    return sum(n * s.foyers * s.parts * publie[s.nom] for s in segments(ANNEE_CALAGE)) / (
        EUROS_PAR_MILLIARD
    )


def impot_publie_non_cale_2024() -> float:
    """Part de l'impôt publié pour 2024 dans les segments non calés, en Md€."""
    publie, bareme = _impot_publie_par_part(), bareme_openfisca(ANNEE_CALAGE)
    n = nombre_foyers(ANNEE_CALAGE)
    return (
        sum(
            n * s.foyers * s.parts * publie[s.nom]
            for s in segments(ANNEE_CALAGE)
            if _impot_moyen(bareme, s, part_couples(s)) <= SEUIL_CALAGE
        )
        / EUROS_PAR_MILLIARD
    )


def _ecart(
    reference: Bareme, reforme: Bareme, annee: int, couples: str, par_segment: bool
) -> float:
    k, g = calage(couples), calage_global(couples)

    def ecart(s: Segment) -> float:
        c = part_couples(s, couples)
        return _impot_moyen(reforme, s, c) - _impot_moyen(reference, s, c)

    return _total(annee, ecart, lambda s: k[s.nom] if par_segment else g) / EUROS_PAR_MILLIARD


def effet(reference: Bareme, reforme: Bareme, annee: int) -> Fourchette:
    """Écart d'impôt entre ``reforme`` et ``reference`` sur les revenus de ``annee``, en Md€
    (positif : l'impôt augmente). Valeur centrale : calage par segment, part des couples par
    quantile ; fourchette : calage unique, part des couples uniforme."""
    central = _ecart(reference, reforme, annee, REPARTITION, par_segment=True)
    variantes = [
        _ecart(reference, reforme, annee, REPARTITION, par_segment=False),
        _ecart(reference, reforme, annee, UNIFORME, par_segment=True),
    ]
    return encadrer(central, variantes)


def _indexe(bareme: Bareme, facteur: float) -> Bareme:
    decote = None if bareme.decote is None else bareme.decote.indexee(facteur)
    r = bareme.reduction
    reduction = (
        None
        if r is None
        else ReductionSousCondition(
            r.taux,
            r.plafond_celibataire * facteur,
            r.plafond_couple * facteur,
            r.majoration_demi_part * facteur,
        )
    )
    return Bareme(tuple(s * facteur for s in bareme.seuils), bareme.taux, decote, reduction)


def validation_tranche_45_2012() -> float:
    """Gain de la tranche à 45 % créée pour les revenus de 2012 (PLF 2013), en Md€."""
    avec = bareme_openfisca(2012)
    sans = Bareme(avec.seuils[:-1], avec.taux[:-1], avec.decote, avec.reduction)
    return effet(sans, avec, 2012).central


def validation_bas_de_bareme_2014() -> float:
    """Coût de la réforme du bas de barème sur les revenus de 2014 (PLF 2015), en Md€.

    Référence : barème et décote de 2013 revalorisés comme les tranches non réformées (rapport
    des seuils de la tranche à 30 %, 0,5 %)."""
    apres, avant = bareme_openfisca(2014), bareme_openfisca(2013)
    revalorise = _indexe(avant, apres.seuils[2] / avant.seuils[3])
    return -effet(revalorise, apres, 2014).central


def validation_classes_moyennes_2020() -> float:
    """Coût de la baisse du taux de 14 % à 11 %, de la décote atténuée et des seuils revus,
    revenus de 2020 (PLF 2020), en Md€. Référence : barème et décote de 2019 revalorisés comme
    le seuil de la tranche à 45 %."""
    apres, avant = bareme_openfisca(2020), bareme_openfisca(2019)
    revalorise = _indexe(avant, apres.seuils[-1] / avant.seuils[-1])
    return -effet(revalorise, apres, 2020).central


def validation_non_indexation_2024() -> float:
    """Gain d'une absence d'indexation de 2 % des seuils et de la décote sur les revenus de
    2024 (PLF 2025), en Md€."""
    indexe = bareme_openfisca(2024)
    taux = chiffrage("ir_indexation_plf2025") / POURCENT
    return effet(indexe, _indexe(indexe, 1 / (1 + taux)), 2024).central


VALIDATIONS: dict[str, Callable[[], float]] = {
    "ir_bareme_tranche_45_plf2013": validation_tranche_45_2012,
    "ir_bareme_bas_de_bareme_plf2015": validation_bas_de_bareme_2014,
    "ir_bareme_classes_moyennes_plf2020": validation_classes_moyennes_2020,
    "ir_non_indexation_2025": validation_non_indexation_2024,
}
"""Réformes de validation : identifiant du chiffrage officiel, calcul du moteur."""


def plage_ecart_validation() -> tuple[float, float]:
    """Plus petit et plus grand rapport chiffrage officiel / modèle, moins un (hypothèse
    ``ir_bareme_ecart``)."""
    ecarts = [chiffrage(ident) / calcul() - 1 for ident, calcul in VALIDATIONS.items()]
    return min(ecarts), max(ecarts)


ANNEE_SITE = 2025
"""Barème de départ de l'éditeur du site : celui des revenus de 2025 (OpenFisca)."""


def revalorisation_site() -> float:
    """Rapport des seuils de la tranche à 45 % entre les barèmes de 2025 et de 2024 : un barème
    saisi sur la base de 2025 est ramené aux revenus de 2024 (calage) en le divisant."""
    return bareme_openfisca(ANNEE_SITE).seuils[-1] / bareme_openfisca(ANNEE_CALAGE).seuils[-1]


def effet_site(reforme: Bareme) -> Fourchette:
    """Effet d'un barème saisi à partir du barème de 2025, en Md€ de 2025 (positif : recettes
    en hausse). Les deux barèmes sont ramenés aux revenus de 2024, l'écart est porté en 2025
    par le PIB nominal."""
    r = 1 / revalorisation_site()
    vers_2025 = facteur_pib(ANNEE_SITE) / facteur_pib(ANNEE_CALAGE)
    f = effet(_indexe(bareme_openfisca(ANNEE_SITE), r), _indexe(reforme, r), ANNEE_CALAGE)
    return Fourchette(f.bas * vers_2025, f.central * vers_2025, f.haut * vers_2025)


def _bareme_dict(b: Bareme) -> dict[str, object]:
    d = b.decote
    return {
        "seuils": list(b.seuils),
        "taux": list(b.taux),
        "decote": None
        if d is None
        else {
            "seuil_celibataire": d.seuil_celibataire,
            "seuil_couple": d.seuil_couple,
            "taux": d.taux,
        },
    }


def _taux_30_plus_2(b: Bareme) -> Bareme:
    return Bareme(b.seuils, (*b.taux[:2], b.taux[2] + 0.02, *b.taux[3:]), b.decote)


def _tranche_60(b: Bareme) -> Bareme:
    return Bareme((*b.seuils, 500_000.0), (*b.taux, 0.6), b.decote)


def _sans_decote(b: Bareme) -> Bareme:
    return Bareme(b.seuils, b.taux, None)


def _trois_tranches(b: Bareme) -> Bareme:
    return Bareme((0.0, 15_000.0, 60_000.0), (0.0, 0.2, 0.4), b.decote)


BAREMES_CONTROLE: tuple[tuple[str, Callable[[Bareme], Bareme]], ...] = (
    ("taux_30_plus_2", _taux_30_plus_2),
    ("tranche_60_a_500000", _tranche_60),
    ("sans_decote", _sans_decote),
    ("trois_tranches", _trois_tranches),
)
"""Barèmes de contrôle : le calcul du site doit redonner ``effet_site`` (tests du site)."""


def donnees_site() -> dict[str, object]:
    """Données du calcul fait dans le navigateur (éditeur de barème du simulateur), et effets
    de quelques barèmes de contrôle calculés ici."""
    segs = segments(ANNEE_CALAGE)
    n = nombre_foyers(ANNEE_CALAGE)
    k_rep, k_uni = calage(REPARTITION), calage(UNIFORME)
    reference = bareme_openfisca(ANNEE_SITE)
    return {
        "annee_bareme": ANNEE_SITE,
        "annee_revenus": ANNEE_CALAGE,
        "revalorisation": revalorisation_site(),
        "vers_euros_reference": facteur_pib(ANNEE_SITE) / facteur_pib(ANNEE_CALAGE),
        "bareme_reference": _bareme_dict(reference),
        "calage_global": calage_global(REPARTITION),
        "couples_uniforme": chiffrage(COUPLES_ENSEMBLE) / POURCENT,
        "segments": [
            {
                "nom": s.nom,
                "foyers": n * s.foyers,
                "parts": s.parts,
                "calage": k_rep[s.nom],
                "calage_couples_uniforme": k_uni[s.nom],
                "couples": part_couples(s),
                "quotients": [round(q, 2) for q in s.quotients],
            }
            for s in segs
        ],
        "controles": [
            {
                "nom": nom,
                "bareme": _bareme_dict(construire(reference)),
                "effet": vars(effet_site(construire(reference))),
            }
            for nom, construire in BAREMES_CONTROLE
        ],
    }
