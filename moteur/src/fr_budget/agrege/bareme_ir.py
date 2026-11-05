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

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage
from fr_budget.registres.verification import RACINE_DEPOT

DOSSIER = RACINE_DEPOT / "data" / "processed" / "impot_revenu"
FICHIER = DOSSIER / "deciles_rfr_part.csv"
FICHIER_2024 = DOSSIER / "deciles_rfr_part_2024.csv"
ANNEE_CALAGE = 2024
DIXIEMES = 10
PART_CENTIEME = 0.1
"""Part du dernier dixième dans le dernier centième, et du dernier centième dans le dernier
millième (définitions de la DGFiP)."""
DIXIEME = 0.1
"""Part des foyers dans un dixième."""
POINTS = 400
"""Points d'intégration par segment (règle du point milieu sur les quantiles)."""
EUROS_PAR_MILLIARD = 1e9
POURCENT = 100.0
SEUIL_CALAGE = 1.0
"""Impôt modélisé par part (euros) sous lequel un segment n'est pas calé (rapport 1)."""
TAUX_MAXIMUM = 1.0


@dataclass(frozen=True)
class Bareme:
    """Barème progressif : ``taux[i]`` s'applique entre ``seuils[i]`` et ``seuils[i + 1]``."""

    seuils: tuple[float, ...]
    taux: tuple[float, ...]

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
    """Barème des revenus de ``annee`` (OpenFisca, ``bareme_ir_depuis_1945.bareme``)."""
    b = systeme_socio_fiscal().parameters(f"{annee}-01-01").impot_revenu.bareme_ir_depuis_1945
    return Bareme(
        tuple(float(s) for s in b.bareme.thresholds), tuple(float(t) for t in b.bareme.rates)
    )


@dataclass(frozen=True)
class Segment:
    nom: str
    foyers: float
    """Part des foyers du segment (dixième : 0,1)."""
    parts: float
    quotients: tuple[float, ...]
    """Quotients aux points d'intégration, en euros."""


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
def segments(annee: int) -> tuple[Segment, ...]:
    """Répartition des foyers de l'année de revenus ``annee`` en segments de quotient."""
    deciles = _deciles()[annee]
    detail = _detail_2024()
    resultat = []
    for d in range(1, DIXIEMES):
        lg = deciles[d]
        bas = float(lg["borne_inferieure"] or 0.0)
        haut = float(lg["borne_superieure"])
        resultat.append(Segment(str(d), 0.1, detail[str(d)]["parts_moyen"], _uniforme(bas, haut)))
    echelle = float(deciles[DIXIEMES]["borne_inferieure"]) / detail["10"]["borne_inferieure"]
    parts = _parts_haut()
    for nom, part, bas, haut, moyenne in _haut_2024():
        alpha = _alpha(moyenne, bas, haut)
        quotients = tuple(q * echelle for q in _pareto(alpha, bas, haut))
        resultat.append(Segment(nom, part, parts[nom], quotients))
    return tuple(resultat)


def _impot_moyen(bareme: Bareme, segment: Segment) -> float:
    return sum(impot_par_part(bareme, q) for q in segment.quotients) / len(segment.quotients)


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
def calage() -> dict[str, float]:
    """Rapport, par segment, entre l'impôt au barème publié et l'impôt modélisé (2024)."""
    bareme = bareme_openfisca(ANNEE_CALAGE)
    publie = _impot_publie_par_part()
    rapports = {}
    for s in segments(ANNEE_CALAGE):
        modele = _impot_moyen(bareme, s)
        rapports[s.nom] = publie[s.nom] / modele if modele > SEUIL_CALAGE else 1.0
    return rapports


@cache
def calage_global() -> float:
    """Variante : un seul rapport pour l'ensemble (2024)."""
    bareme = bareme_openfisca(ANNEE_CALAGE)
    publie = _impot_publie_par_part()
    segs = segments(ANNEE_CALAGE)
    total_publie = sum(s.foyers * s.parts * publie[s.nom] for s in segs)
    total_modele = sum(s.foyers * s.parts * _impot_moyen(bareme, s) for s in segs)
    return total_publie / total_modele


def _total(annee: int, f: Callable[[Segment], float], rapport: Callable[[Segment], float]) -> float:
    n = nombre_foyers(annee)
    return sum(n * s.foyers * s.parts * rapport(s) * f(s) for s in segments(annee))


def impot_modele(bareme: Bareme, annee: int) -> float:
    """Impôt au barème de tous les foyers, en Md€ (calage par segment)."""
    k = calage()
    return _total(annee, lambda s: _impot_moyen(bareme, s), lambda s: k[s.nom]) / EUROS_PAR_MILLIARD


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
            if _impot_moyen(bareme, s) <= SEUIL_CALAGE
        )
        / EUROS_PAR_MILLIARD
    )


def effet(reference: Bareme, reforme: Bareme, annee: int) -> Fourchette:
    """Écart d'impôt entre ``reforme`` et ``reference`` sur les revenus de ``annee``, en Md€
    (positif : l'impôt augmente). Valeur centrale : calage par segment ; autre bout de la
    fourchette : calage unique."""

    def ecart(s: Segment) -> float:
        return _impot_moyen(reforme, s) - _impot_moyen(reference, s)

    k = calage()
    central = _total(annee, ecart, lambda s: k[s.nom]) / EUROS_PAR_MILLIARD
    variante = _total(annee, ecart, lambda _s: calage_global()) / EUROS_PAR_MILLIARD
    return encadrer(central, [variante])


def _indexe(bareme: Bareme, facteur: float) -> Bareme:
    return Bareme(tuple(s * facteur for s in bareme.seuils), bareme.taux)


def validation_tranche_45_2012() -> float:
    """Gain de la tranche à 45 % créée pour les revenus de 2012 (PLF 2013), en Md€."""
    avec = bareme_openfisca(2012)
    sans = Bareme(avec.seuils[:-1], avec.taux[:-1])
    return effet(sans, avec, 2012).central


def validation_bas_de_bareme_2014() -> float:
    """Coût de la réforme du bas de barème sur les revenus de 2014 (PLF 2015), en Md€.

    Référence : barème de 2013 revalorisé comme les tranches non réformées (rapport des seuils
    de la tranche à 30 %, 0,5 %)."""
    apres, avant = bareme_openfisca(2014), bareme_openfisca(2013)
    revalorise = _indexe(avant, apres.seuils[2] / avant.seuils[3])
    return -effet(revalorise, apres, 2014).central


def validation_classes_moyennes_2020() -> float:
    """Coût de la baisse du taux de 14 % à 11 % et des seuils revus, revenus de 2020 (PLF 2020),
    en Md€. Référence : barème de 2019 revalorisé comme le seuil de la tranche à 45 %."""
    apres, avant = bareme_openfisca(2020), bareme_openfisca(2019)
    revalorise = _indexe(avant, apres.seuils[-1] / avant.seuils[-1])
    return -effet(revalorise, apres, 2020).central


def validation_non_indexation_2024() -> float:
    """Gain d'une absence d'indexation de 2 % des seuils sur les revenus de 2024 (PLF 2025), en
    Md€ : barème de 2024 comparé au même barème aux seuils non revalorisés."""
    indexe = bareme_openfisca(2024)
    taux = chiffrage("ir_indexation_plf2025") / POURCENT
    return effet(indexe, _indexe(indexe, 1 / (1 + taux)), 2024).central
