"""Validation du levier TVA (rendement statique d'un point de TVA).

Références (registres/references/chiffrages.yaml, levier « tva ») :

- DG Trésor, Trésor-Éco n° 371 (septembre 2025), tableaux 1 et 2 : rendement brut et net
  d'un point de TVA en 2025, total et par taux. Millésime : 2025 (modèle sur le compte 2022
  vieilli).
- DG Trésor, Cahier n° 2016-02, tableau 8 : rendement d'un point de TVA en 2015, par taux.
  Millésime : 2015. Valeurs arrondies au quart de milliard dans la source.
- Recette totale reconstituée, sans vieillissement, comparée à la TVA nette observée la même
  année : 2022 (DG Trésor, Trésor-Éco n° 371, page 2) et 2024 (PLF 2026, Voies et Moyens
  tome I, page 33).

Tolérance : ±10 % (règle de publication d'un levier, CLAUDE.md).

Le modèle utilise le coût de certains taux réduits publié dans Voies et Moyens tome 2, chiffré
par le même modèle de la DG Trésor : la comparaison n'est donc que partiellement indépendante
(voir docs/fiches/tva.md).
"""

from __future__ import annotations

from typing import Any

import pytest
import yaml

from fr_budget.agrege.tva import estimer_point_tva, estimer_recette_totale
from fr_budget.registres.verification import RACINE_DEPOT

TOLERANCE = 0.10
TAUX = ["taux_2_1", "taux_5_5", "taux_10", "taux_20"]

CHIFFRAGES: dict[str, Any] = {
    c["id"]: c
    for c in yaml.safe_load(
        (RACINE_DEPOT / "registres" / "references" / "chiffrages.yaml").read_text(encoding="utf-8")
    )["chiffrages"]
}


def ecart_relatif(modele: float, reference: float) -> float:
    return (modele - reference) / reference


def verifier(modele: float, identifiant: str) -> None:
    reference = CHIFFRAGES[identifiant]["valeur"]
    ecart = ecart_relatif(modele, reference)
    assert abs(ecart) <= TOLERANCE, (
        f"{identifiant} : modèle {modele:.2f} Md€, référence {reference:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )


@pytest.mark.validation
@pytest.mark.parametrize("taux", ["ensemble", *TAUX])
def test_point_tva_brut_2025(taux: str) -> None:
    point = estimer_point_tva(annee_comptes=2022, annee_cible=2025)
    verifier(point.brut[taux], f"tva_point_brut_2025_{taux}")


@pytest.mark.validation
@pytest.mark.parametrize("taux", ["ensemble", *TAUX])
def test_point_tva_net_2025(taux: str) -> None:
    point = estimer_point_tva(annee_comptes=2022, annee_cible=2025)
    verifier(point.net[taux], f"tva_point_net_2025_{taux}")


@pytest.mark.validation
@pytest.mark.parametrize("taux", ["ensemble", *TAUX])
def test_point_tva_brut_2015(taux: str) -> None:
    point = estimer_point_tva(annee_comptes=2015, annee_cible=2015)
    verifier(point.brut[taux], f"tva_point_brut_2015_{taux}")


@pytest.mark.validation
@pytest.mark.parametrize(
    ("annee", "reference"),
    [(2022, "tva_nette_totale_2022_dgtresor"), (2024, "tva_nette_totale_execution_2024")],
)
def test_recette_totale(annee: int, reference: str) -> None:
    # Sans vieillissement : la recette reconstituée à partir des comptes d'une année est
    # comparée à la recette observée la même année.
    verifier(estimer_recette_totale(annee_comptes=annee), reference)
