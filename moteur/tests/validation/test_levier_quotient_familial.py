"""Validation du levier « plafond du quotient familial ».

La valeur centrale du modèle vient du chiffrage de l'IGF et de l'IGAS (juin 2026 : 580 M€ pour
une baisse de 10 % des plafonds, législation 2026) : elle ne peut pas valider le modèle. Les
références hors calage sont les deux baisses votées, chiffrées par le Gouvernement dans
l'exposé général des motifs des projets de loi de finances :

- PLF 2013 : plafond de 2 336 à 2 000 € par demi-part, 0,5 Md€ (rendement 2013) ;
- PLF 2014 : plafond de 2 000 à 1 500 €, 1 Md€ (arrondi au milliard).

Le modèle applique la sensibilité de 2026, tenue constante en part du PIB nominal, à la baisse
de l'année. Tolérance : ±10 % (règle de publication).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.quotient_familial import baisse_historique, rendement_baisse
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10


@pytest.mark.validation
@pytest.mark.parametrize("annee", [2013, 2014])
def test_baisses_du_plafond(annee: int) -> None:
    reference = f"qf_baisse_plafond_rendement_{annee}"
    modele = rendement_baisse(baisse_historique(annee), annee)
    valeur = chiffrage(reference)
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.2f} Md€, référence {valeur:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
