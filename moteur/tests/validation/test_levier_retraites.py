"""Validation du module retraites (première étape) : relèvement d'un an de l'âge de départ.

Référence : tableau 2.10 du rapport annuel du COR de juin 2026 (page 123), effet d'une
augmentation d'un an de l'âge d'ouverture des droits sur le solde primaire des APU, d'après
les simulations de la DG Trésor (Mésange et modèle comptable), d'I-MIP (CepreHANK) et de l'OFCE
(EmeRaude) : +0,05 à +0,4 point de PIB à 2 ans, +0,3 à +0,6 point à 10 ans, +0,3 à +0,65
point à 20 ans. Le modèle est
comparé à chaque borne de la fourchette publiée. Tolérance : ±10 % (règle de publication).

Ces références ne valident pas exactement la même mesure : le modèle relève l'âge effectif
moyen de départ d'un an, alors que l'âge d'ouverture des droits relevé d'un an élève moins
l'âge effectif ; les simulations comptent les effets macroéconomiques, absents du modèle.
"""

from __future__ import annotations

import pytest

from fr_budget.registres.acces import chiffrage
from fr_budget.retraites import effet_a_horizon

TOLERANCE = 0.10
ENTREE = 2027


@pytest.mark.validation
@pytest.mark.parametrize("horizon", [2, 10, 20])
@pytest.mark.parametrize("borne", ["bas", "haut"])
def test_relevement_d_un_an(horizon: int, borne: str) -> None:
    reference = f"cor_aod_un_an_solde_apu_{horizon}ans_{borne}"
    modele = effet_a_horizon(horizon, ENTREE)
    valeur = chiffrage(reference)
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.2f} point de PIB, référence {valeur:.2f}, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
