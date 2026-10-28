"""Validation du modèle de retraites par cohortes (relèvement de l'âge légal d'ouverture des
droits, ``fr_budget.retraites_cohortes``).

Référence : COR, rapport annuel de juin 2026, tableau 2.10 (page 123), effet d'un an de plus sur
l'âge d'ouverture des droits sur le solde primaire des administrations publiques selon les
simulations de la DG Trésor, d'I-MIP et de l'OFCE, fourchette basse-haute, à 2, 10 et 20 ans
(mêmes références que le levier sur l'âge effectif). Entrée en vigueur en 2027.

Règle (décision du mainteneur du 28 octobre 2026) : le modèle passe s'il est dans
[0,9 * borne basse ; 1,1 * borne haute] (``fr_budget.validation.comparer_fourchette``).
"""

from __future__ import annotations

import pytest

from fr_budget import validation as v

COHORTES = [(b, h, c) for b, h, c, variante in v.definitions_fourchettes() if variante]


@pytest.mark.validation
@pytest.mark.parametrize(("basse", "haute", "calcul"), COHORTES)
def test_relevement_d_un_an_cohortes(basse: str, haute: str, calcul: object) -> None:
    c = v.comparer_fourchette(basse, haute, calcul(), variante=v.COHORTES)  # type: ignore[operator]
    assert c.dans_la_tolerance, (
        f"{basse} (cohortes) : modèle {c.modele:.2f} point de PIB, fourchette "
        f"{c.valeur_reference:.2f} à {c.valeur_haute:.2f}, écart à la borne la plus proche "
        f"{c.ecart:+.1%} (tolérance ±{c.tolerance:.0%})"
    )
