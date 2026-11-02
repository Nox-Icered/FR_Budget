"""Validation des leviers « assurance chômage » (première étape, leviers agrégés).

Références : chiffrages de l'Unédic, tolérance ±10 % (règle de publication, CLAUDE.md).

- Contribution patronale : effet de la contribution exceptionnelle de 0,05 point, en 2019
  (+288 M€, étude d'impact de la convention 2017, tableau 2, ligne (a)) et en 2026 (-385 M€,
  étude d'impact de la convention du 15 novembre 2024, page 55). Modèle : 0,05 point des
  contributions principales de l'année rapportées au taux de l'année.
- Revalorisation des allocations : le modèle est calé sur la revalorisation de 1,9 % au
  1er juillet 2023 (mode d'emploi de l'Unédic, juin 2023, tableau 2). Il est comparé à deux
  autres revalorisations : 1,9 % au 1er avril 2023 (590 M€ cumulés sur 2023 et 2024, hors
  dégressivité) et 0,70 % au 1er juillet 2018 (« de l'ordre de 200 millions d'€ » pour le
  second semestre 2018 et 2019). Même organisme, mêmes méthodes : ce n'est pas une
  confrontation indépendante.

Le levier sur la durée d'indemnisation est calé sur le seul chiffrage publié pour l'ensemble
des allocataires (réforme de 2023) : il n'a pas de référence de validation distincte
(docs/fiches/assurance_chomage.md, § 6).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.assurance_chomage import cout_revalorisation_cumule, effet_contribution
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
MILLIONS_PAR_MILLIARD = 1000.0
JUILLET = 7
AVRIL = 4


def _verifier(reference: str, modele: float) -> None:
    valeur = chiffrage(reference) / MILLIONS_PAR_MILLIARD
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.3f} Md€, référence {valeur:.3f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )


@pytest.mark.validation
def test_contribution_exceptionnelle_2019() -> None:
    points = chiffrage("chomage_contribution_points_0_05")
    _verifier("chomage_contribution_hausse_0_05_2019", effet_contribution(points, 2019))


@pytest.mark.validation
def test_suppression_contribution_exceptionnelle_2026() -> None:
    points = chiffrage("chomage_contribution_points_0_05")
    _verifier("chomage_contribution_baisse_0_05_2026", effet_contribution(points, 2026))


@pytest.mark.validation
def test_revalorisation_avril_2023() -> None:
    taux = chiffrage("chomage_revalorisation_avril_2023_taux")
    allocations = chiffrage("chomage_allocations_brutes_2023")
    _verifier(
        "chomage_revalorisation_avril_2023_cumul",
        cout_revalorisation_cumule(taux, AVRIL, allocations),
    )


@pytest.mark.validation
def test_revalorisation_juillet_2018() -> None:
    taux = chiffrage("chomage_revalorisation_juillet_2018_taux")
    allocations = chiffrage("chomage_allocations_brutes_2018") / MILLIONS_PAR_MILLIARD
    _verifier(
        "chomage_revalorisation_juillet_2018_cout",
        cout_revalorisation_cumule(taux, JUILLET, allocations),
    )
