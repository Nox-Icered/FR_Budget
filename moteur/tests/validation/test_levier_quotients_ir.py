"""Validation des leviers sur l'effet du quotient familial et du quotient conjugal.

Références (``registres/references/chiffrages.yaml``) :

- quotient familial : baisse d'impôt due à la composante familiale en 2018, 19,0 Md€ (Insee
  Analyses n° 53, juin 2020, figure 1) ; le modèle est calé sur 2017 (André et Sireyjol, 2021)
  et porté en 2018 par le PIB nominal ;
- quotient conjugal : composante conjugale en 2018, 10,8 Md€ (même source).

Source indépendante (``test_confrontations_independantes.py``) : individualisation avec
répartition des parts des enfants, 7,2 Md€ en 2016 (Allègre, Périvier et Pucci, OFCE).

Tolérance : ±10 % (règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege import quotients_ir as q
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10


@pytest.mark.validation
def test_composante_familiale_2018() -> None:
    reference = chiffrage("ir_insee_familialisation_2018")
    assert q.suppression(q.LEVIER_QF, 2018) == pytest.approx(reference, rel=TOLERANCE)


@pytest.mark.validation
def test_composante_conjugale_2018() -> None:
    reference = chiffrage("ir_insee_conjugalisation_2018")
    assert q.suppression(q.LEVIER_QC, 2018) == pytest.approx(reference, rel=TOLERANCE)
