"""Confrontation des leviers à des sources indépendantes de l'administration (règle de
publication, CLAUDE.md) : IPP, OFCE, Cour des comptes et, à défaut, Fipeco.

Références : ``registres/references/chiffrages.yaml`` (``independante: true``) ; mesures et
années du modèle : ``fr_budget.validation._confrontations_independantes``.

- TVA : hausse d'un point des quatre taux, recettes et effet net des achats des
  administrations (IPP, juin 2025), modèle en 2025 ;
- impôt sur le revenu : gel du barème en 2026 pour une inflation de 1 % et de 1,3 % (IPP), de
  1,1 % (OFCE) ;
- pensions de base : gel en 2026 pour une inflation de 1 % et de 1,3 % (IPP), baisse de
  dépenses brute ;
- point d'indice : hausse de 1 %, Cour des comptes (2017, total et par versant) et Fipeco
  (2026, hors cotisations des employeurs, modèle en 2025).

Tolérance : ±10 % (règle de publication). Un écart hors tolérance est publié tel quel.
"""

from __future__ import annotations

import pytest

from fr_budget import validation as v

REFERENCES = [r for r, _ in v._confrontations_independantes()]


@pytest.mark.validation
@pytest.mark.parametrize("reference", REFERENCES)
def test_confrontation_independante(reference: str) -> None:
    calcul = dict(v._confrontations_independantes())[reference]
    c = v.comparer(reference, calcul())
    assert c.dans_la_tolerance, (
        f"{reference} : modèle {c.modele:.3f}, référence {c.valeur_reference:.3f}, "
        f"écart {c.ecart:+.1%} (tolérance ±{c.tolerance:.0%})"
    )
