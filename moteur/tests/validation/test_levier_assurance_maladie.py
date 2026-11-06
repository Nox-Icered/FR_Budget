"""Validation des leviers d'assurance maladie face aux chiffrages officiels.

Références (``registres/references/chiffrages.yaml``) :

- franchises et participations forfaitaires : doublement des montants unitaires et des plafonds
  journaliers et annuels, projets de décrets de l'été 2025, 2,3 Md€ en année pleine (Cour des
  comptes, rapport sur l'application des LFSS de mai 2026, page 189) ;
- plafond des revenus pris en compte pour les indemnités journalières : baisse de 1,8 à 1,4
  Smic, économie de la première année, 0,6 Md€ (annexe 5 du PLFSS pour 2025, page 34) et 0,4 Md€
  (montant inclus dans la LFSS pour 2025 selon la Cour des comptes, page 92).

Tolérance : ±10 % (règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.registres.acces import chiffrage
from fr_budget.validation import _franchises_doublement, _ij_plafond_premiere_annee

TOLERANCE = 0.10


@pytest.mark.validation
def test_doublement_des_franchises_et_des_plafonds() -> None:
    reference = chiffrage("franchises_pf_doublement_avec_plafonds_2026")
    assert _franchises_doublement() == pytest.approx(reference, rel=TOLERANCE)


@pytest.mark.validation
@pytest.mark.parametrize(
    "reference", ["ij_plafond_1_8_1_4_plfss2025", "ij_plafond_lfss2025_ccomptes"]
)
def test_baisse_du_plafond_des_indemnites_journalieres(reference: str) -> None:
    assert _ij_plafond_premiere_annee() == pytest.approx(chiffrage(reference), rel=TOLERANCE)
