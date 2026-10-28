"""Validation du module retraites (première étape) : relèvement d'un an de l'âge de départ.

Référence : tableau 2.10 du rapport annuel du COR de juin 2026 (page 123), effet d'une
augmentation d'un an de l'âge d'ouverture des droits sur le solde primaire des APU, d'après
les simulations de la DG Trésor (Mésange et modèle comptable), d'I-MIP (CepreHANK) et de l'OFCE
(EmeRaude) : +0,05 à +0,4 point de PIB à 2 ans, +0,3 à +0,6 point à 10 ans, +0,3 à +0,65
point à 20 ans.

Règle (décision du mainteneur du 28 octobre 2026, la référence étant une fourchette de
modèles et non un chiffrage unique) : le modèle passe s'il est dans [0,9 * borne basse ;
1,1 * borne haute] (``fr_budget.validation.comparer_fourchette``). Elle remplace la
comparaison à chaque borne à ±10 %, qu'aucun modèle ne pouvait satisfaire aux deux bornes à
la fois.

Ces références ne valident pas exactement la même mesure : le modèle relève l'âge effectif
moyen de départ d'un an, alors que l'âge d'ouverture des droits relevé d'un an élève moins
l'âge effectif ; les simulations comptent les effets macroéconomiques, absents du modèle.
"""

from __future__ import annotations

import pytest

from fr_budget import validation as v

LEVIER = [(b, h, c) for b, h, c, variante in v.definitions_fourchettes() if not variante]


@pytest.mark.validation
@pytest.mark.parametrize(("basse", "haute", "calcul"), LEVIER)
def test_relevement_d_un_an(basse: str, haute: str, calcul: object) -> None:
    c = v.comparer_fourchette(basse, haute, calcul())  # type: ignore[operator]
    assert c.dans_la_tolerance, (
        f"{basse} : modèle {c.modele:.2f} point de PIB, fourchette {c.valeur_reference:.2f} à "
        f"{c.valeur_haute:.2f}, écart à la borne la plus proche {c.ecart:+.1%} "
        f"(tolérance ±{c.tolerance:.0%})"
    )
