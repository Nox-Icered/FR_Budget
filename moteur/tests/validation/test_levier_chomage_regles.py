"""Validation des leviers d'assurance chômage de la deuxième étape (condition d'affiliation,
dégressivité) face aux études de l'Unédic.

Références (``registres/references/chiffrages.yaml``) : moindres dépenses d'allocations en régime
de croisière du passage de 4 à 6 mois de la condition d'ouverture de droit (étude de 2019 :
1 000 M€ ; étude de 2021 : 800 M€) et de la dégressivité au 7e mois (étude de 2021 : 460 M€ ;
évaluation de 2025 : 0,5 Md€, estimation de 2021 arrondie, confirmée par les observations).
Le modèle est calé sur l'étude de 2021 : la comparaison à 2021 vérifie le calage, celle à 2019
et à 2025 en est la validation. Tolérance : ±10 % (règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.registres.acces import chiffrage
from fr_budget.validation import _definitions_chomage_regles

TOLERANCE = 0.10
DEFINITIONS = dict(_definitions_chomage_regles())


@pytest.mark.validation
@pytest.mark.parametrize("reference", list(DEFINITIONS))
def test_reference_unedic(reference: str) -> None:
    assert DEFINITIONS[reference]() == pytest.approx(chiffrage(reference), rel=TOLERANCE)
