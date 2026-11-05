"""Validation du moteur de barème de l'impôt sur le revenu.

Le modèle est calé sur la seule année 2024 (impôt au barème par décile de RFR par part, DGFiP).
Les références sont des réformes passées du barème, chiffrées par le Gouvernement et recalculées
avec le barème et la répartition des revenus de leur année (hors échantillon de calage) :

- PLF 2013 : création de la tranche à 45 % (revenus 2012), 0,3 Md€ ;
- PLF 2015 : suppression de la tranche à 5,5 % et seuil de la tranche à 14 % à 9 690 €
  (revenus 2014), coût de 3,187 Md€, décote renforcée comprise ;
- PLF 2020 : taux de 14 % ramené à 11 % et seuils revus (revenus 2020), environ 5 Md€, décote
  atténuée comprise ;
- PLF 2025 : absence d'indexation de 2 % des seuils (revenus 2024), 3,7 Md€.

Les réformes de 2015 et de 2020 changeaient aussi la décote, que le modèle ne fait pas varier.
Tolérance : ±10 % (règle de publication).
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from fr_budget.agrege import bareme_ir as b
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
REFERENCES: dict[str, Callable[[], float]] = {
    "ir_bareme_tranche_45_plf2013": b.validation_tranche_45_2012,
    "ir_bareme_bas_de_bareme_plf2015": b.validation_bas_de_bareme_2014,
    "ir_bareme_classes_moyennes_plf2020": b.validation_classes_moyennes_2020,
    "ir_non_indexation_2025": b.validation_non_indexation_2024,
}


@pytest.mark.validation
@pytest.mark.parametrize("reference", list(REFERENCES))
def test_reformes_du_bareme(reference: str) -> None:
    modele = REFERENCES[reference]()
    valeur = chiffrage(reference)
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.2f} Md€, référence {valeur:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
