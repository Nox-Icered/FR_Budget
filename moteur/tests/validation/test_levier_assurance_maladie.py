"""Validation des leviers d'assurance maladie face aux chiffrages officiels.

Références (``registres/references/chiffrages.yaml``) :

- franchises et participations forfaitaires : doublement des montants unitaires et des plafonds
  journaliers et annuels, projets de décrets de l'été 2025, 2,3 Md€ en année pleine (Cour des
  comptes, rapport sur l'application des LFSS de mai 2026, page 189) ;
- plafond des revenus pris en compte pour les indemnités journalières : baisse de 1,8 à 1,4
  Smic, économie de la première année, 0,6 Md€ (annexe 5 du PLFSS pour 2025, page 34) et 0,4 Md€
  (montant inclus dans la LFSS pour 2025 selon la Cour des comptes, page 92) ;
- ticket modérateur des consultations des médecins et des sages-femmes : hausse de 30 % à 40 %
  prévue pour 2025, 1,1 Md€ (avis n° 130 de la commission des finances du Sénat, page 38) ;
  calage : le modèle reprend le chiffrage du PLFSS pour 2025, que le Sénat cite ; la mesure n'a
  pas été appliquée, il n'existe pas de constat ;
- ticket modérateur des soins dentaires : hausse de 30 % à 40 % du 15 octobre 2023, 525 M€
  d'économie jusqu'à fin 2024 (Cour des comptes, mai 2026, page 216) ; calage sur ce constat.

Tolérance : ±10 % (règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.registres.acces import chiffrage
from fr_budget.validation import (
    _franchises_doublement,
    _ij_plafond_premiere_annee,
    _tm_consultations_hausse,
    _tm_dentaire_constat,
)

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


@pytest.mark.validation
def test_hausse_du_ticket_moderateur_des_consultations() -> None:
    reference = chiffrage("tm_consultations_economie_senat_2025")
    assert _tm_consultations_hausse() == pytest.approx(reference, rel=TOLERANCE)


@pytest.mark.validation
def test_hausse_du_ticket_moderateur_des_soins_dentaires() -> None:
    reference = chiffrage("tm_dentaire_economie_oct2023_dec2024")
    assert _tm_dentaire_constat() == pytest.approx(reference, rel=TOLERANCE)
