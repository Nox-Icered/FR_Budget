"""Validation du levier « indexation des pensions et prestations ».

Références (``registres/references/chiffrages.yaml``) :

- PLFSS 2026, exposé des motifs de l'article 44, page 138 : le maintien en 2026 des prestations
  sociales, pensions comprises, à leur niveau de 2025 rapporte 3,6 Md€ aux administrations
  publiques, nets de l'effet sur la CSG (rapport du Sénat n° 131, tome I, page 134, note 2) ;
  revalorisation légale évitée : inflation hors tabac prévue pour 2025 (1,0 %, page 152) ;
- même mesure, prestations familiales seules : 0,3 Md€ (étude d'impact citée par le rapport
  du Sénat, page 164) ;
- PLFSS 2026, lettre rectificative : sous-indexation supplémentaire de 0,5 point des pensions de
  base en 2027, 1,5 Md€ (rapport du Sénat, page 101) ;
- PLFSS 2027, annexe, page 134 : maintien des prestations familiales à leur niveau de 2026,
  0,5 Md€ en 2027 ; revalorisation évitée : inflation hors tabac prévue pour 2026 (2,1 %,
  page 127) ;
- rapport spécial du Sénat sur la mission « Solidarité, insertion et égalité des chances » du
  PLF 2026, page 27 : « année blanche » de 2026 sur l'AAH, 122,4 M€ (référence en M€, convertie).

Convention commune (celle des PLFSS : « nets des effets CSG et CASA ») : le modèle est comparé
net des prélèvements sociaux (CSG, CRDS, CASA), avant impôt sur le revenu, pour la première
année civile, avec la date de revalorisation de chaque prestation. Tolérance : ±10 % (règle de
publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.indexation import (
    AAH,
    BLOCS,
    FAMILLE,
    NET_PRELEVEMENTS_SOCIAUX,
    PENSIONS,
    cout_mesure,
)
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10
POURCENT = 100.0
INFLATION_2025 = "indexation_inflation_hors_tabac_2025_plfss2026"
INFLATION_2026 = "indexation_inflation_hors_tabac_2026_plfss2027"

MESURES = {
    "indexation_gel_2026_apu": (INFLATION_2025, 2026, tuple(BLOCS)),
    "indexation_gel_2026_familiales": (INFLATION_2025, 2026, (FAMILLE,)),
    "indexation_sous_indexation_0_5_2027": (None, 2027, (PENSIONS,)),
    "indexation_gel_familiales_2027": (INFLATION_2026, 2027, (FAMILLE,)),
    "indexation_gel_aah_2026": (INFLATION_2025, 2026, (AAH,)),
}
SOUS_INDEXATION = 0.005
MILLIONS_PAR_MILLIARD = 1000.0
EN_MILLIONS = ("indexation_gel_aah_2026",)


def taux_mesure(inflation: str | None) -> float:
    return SOUS_INDEXATION if inflation is None else chiffrage(inflation) / POURCENT


@pytest.mark.validation
@pytest.mark.parametrize("reference", list(MESURES))
def test_rendement_premiere_annee(reference: str) -> None:
    inflation, annee, blocs = MESURES[reference]
    modele = cout_mesure(taux_mesure(inflation), annee, blocs, NET_PRELEVEMENTS_SOCIAUX)
    valeur = chiffrage(reference) / (MILLIONS_PAR_MILLIARD if reference in EN_MILLIONS else 1)
    ecart = (modele - valeur) / valeur
    assert abs(ecart) <= TOLERANCE, (
        f"{reference} : modèle {modele:.2f} Md€, référence {valeur:.2f} Md€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
