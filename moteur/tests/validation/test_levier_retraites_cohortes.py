"""Validation du modèle de retraites par cohortes (relèvement de l'âge légal d'ouverture des
droits, ``fr_budget.retraites_cohortes``).

Référence : COR, rapport annuel de juin 2026, tableau 2.10 (page 123), effet d'un an de plus sur
l'âge d'ouverture des droits sur le solde primaire des administrations publiques selon les
simulations de la DG Trésor, d'I-MIP et de l'OFCE, bornes basse et haute, à 2, 10 et 20 ans
(mêmes références que le levier sur l'âge effectif). Entrée en vigueur en 2027.

Tolérance : ±10 % (règle de publication), à chaque borne.
"""

from __future__ import annotations

import pytest

from fr_budget import validation as v


@pytest.mark.validation
@pytest.mark.parametrize(("reference", "calcul"), [(r, c) for r, c, _ in v.definitions_variantes()])
def test_relevement_d_un_an_cohortes(reference: str, calcul: object) -> None:
    c = v.comparer(reference, calcul(), variante=v.COHORTES)  # type: ignore[operator]
    assert c.dans_la_tolerance, (
        f"{reference} (cohortes) : modèle {c.modele:.2f} point de PIB, référence "
        f"{c.valeur_reference:.2f}, écart {c.ecart:+.1%} (tolérance ±{c.tolerance:.0%})"
    )
