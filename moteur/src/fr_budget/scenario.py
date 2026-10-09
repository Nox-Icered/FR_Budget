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

Fourchettes : écart au scénario de référence, avec la plage du rendement du levier ; niveau
de dette et de solde, avec la plage du levier et celle de la baseline, chacune seule.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace

from fr_budget.agrege.tva import fourchette_point_tva
from fr_budget.apu import comptes_apu, ratio_pib
from fr_budget.baseline import ANNEE_FIN, AnneeBaseline, trajectoires
from fr_budget.dette import dette_suivante
from fr_budget.fourchette import Fourchette, encadrer

LEVIER_TVA_NORMAL = "tva_taux_normal"
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


def _rendement_unitaire(levier: str) -> Fourchette:
    """Rendement d'une unité du levier, en Md€ de l'année de référence."""
    if levier == LEVIER_TVA_NORMAL:
        return fourchette_point_tva(annee_comptes=2022, annee_cible=ANNEE_REFERENCE)["net"][
            "taux_20"
        ]
    msg = f"levier inconnu : {levier}"
    raise ValueError(msg)


def effet_solde(mesure: Mesure) -> Fourchette:
    """Effet de la mesure sur le solde primaire, en points de PIB (positif : solde amélioré)."""
    if not ANNEE_PREMIERE_MESURE <= mesure.annee <= ANNEE_FIN:
        periode = f"{ANNEE_PREMIERE_MESURE}-{ANNEE_FIN}"
        msg = f"année d'entrée en vigueur hors de {periode} : {mesure.annee}"
        raise ValueError(msg)
    unite = _rendement_unitaire(mesure.levier)
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


def _effets_par_annee(mesures: Iterable[Mesure], borne: str) -> dict[int, float]:
    effets: dict[int, float] = {}
    for m in mesures:
        valeur = getattr(effet_solde(m), borne)
        for annee in range(m.annee, ANNEE_FIN + 1):
            effets[annee] = effets.get(annee, 0.0) + valeur
    return effets


@dataclass(frozen=True)
class AnneeScenario:
    annee: int
    dette: Fourchette
    solde_primaire: Fourchette
    ecart_dette: Fourchette
    ecart_solde_primaire: Fourchette


def scenario(mesures: Sequence[Mesure]) -> list[AnneeScenario]:
    """Scénario 2025-2046 : niveaux et écarts à la baseline, en points de PIB, en fourchette.

    Plusieurs mesures s'additionnent (pas d'interaction entre leviers à ce stade).
    """
    centrale, variantes = trajectoires()
    effets = {b: _effets_par_annee(mesures, b) for b in ("bas", "central", "haut")}
    avec = {b: trajectoire_avec_effet(centrale, e) for b, e in effets.items()}
    variantes_avec = [trajectoire_avec_effet(v, effets["central"]) for v in variantes]
    resultat = []
    for i, ref in enumerate(centrale):
        c = avec["central"][i]
        autres = [avec["bas"][i], avec["haut"][i]]
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
