"""Validation du levier « prime d'activité » : pente.

Le rendement d'un point est calé sur le chiffrage en année pleine de l'administration pour la
baisse de 1,15 point de la pente au 1er avril 2025 (500 M€, note de présentation du Sénat sur la
mission « Solidarité, insertion et égalité des chances » du PLF 2026). La référence est la
moindre dépense constatée en 2025 (290 M€, rapport spécial du Sénat, page 55), comparée au
rendement en année pleine pour les mois d'avril à décembre. Ce n'est pas une validation
indépendante : même mesure, autre mesure de son effet. Tolérance : ±10 %.
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.prime_activite import economie_baisse_2025
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
MILLIONS_PAR_MILLIARD = 1000.0


@pytest.mark.validation
def test_baisse_de_la_pente_2025() -> None:
    reference = "pa_pente_moindre_depense_2025"
    modele = economie_baisse_2025()
    valeur = chiffrage(reference) / MILLIONS_PAR_MILLIARD
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.3f} Md€, référence {valeur:.3f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
