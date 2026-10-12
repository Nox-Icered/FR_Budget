"""Validation du levier « impôt sur le revenu » : revalorisation des seuils du barème.

La sensibilité centrale du modèle vient de l'évaluation préalable de l'article 2 du PLF 2025
(3,7 Md€ pour 2 % d'indexation, revenus 2024) : elle ne peut pas valider le modèle. La référence
hors calage est le gel du barème proposé par le PLF 2026 : 1,9 Md€ en 2026 (rapport général du
Sénat n° 139, tome I, pages 149 et 150), pour une inflation hors tabac de 2025 prévue à 1,0 %
(PLFSS 2026, même prévision du Gouvernement). Tolérance : ±10 % (règle de publication).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.impot_revenu import rendement_gel
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
INFLATION_2025 = "indexation_inflation_hors_tabac_2025_plfss2026"


@pytest.mark.validation
def test_gel_du_bareme_2026() -> None:
    reference = "ir_gel_bareme_2026"
    modele = rendement_gel(chiffrage(INFLATION_2025), 2026)
    valeur = chiffrage(reference)
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.2f} Md€, référence {valeur:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
