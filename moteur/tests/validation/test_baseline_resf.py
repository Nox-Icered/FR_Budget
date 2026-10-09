"""Validation de la formule de dette contre la trajectoire du RESF 2027.

Référence : PLF 2027, rapport économique, social et financier, tableaux de l'annexe
« finances publiques » (tableaux 13 et 14) et tableau 4 de la partie « finances publiques »
(``data/processed/baseline/resf_2027.csv``). Millésime : PLF 2027 (publié le 6 octobre 2026).

Pour 2026 et 2027, toutes les entrées de la formule sont publiées : dette de l'année précédente,
taux apparent, croissance nominale, solde primaire et flux de créances. La formule
``d(t+1) = d(t) * (1 + r) / (1 + g) - pb + sfa`` doit redonner la dette publiée.

Tolérance : 0,35 point de PIB. Les six entrées et la dette publiée sont arrondies au dixième ;
la somme des erreurs d'arrondi maximales vaut environ 0,31 point pour une dette de 116 % du PIB
(0,05 sur la dette initiale, 0,06 sur le taux, 0,06 sur la croissance, 0,05 sur le solde
primaire, 0,05 sur les flux de créances, 0,05 sur la dette publiée).
"""

from __future__ import annotations

import pytest

from fr_budget.baseline import dette_resf_reproduite, resf

TOLERANCE_POINTS = 0.35


@pytest.mark.validation
@pytest.mark.parametrize("annee", [2026, 2027])
def test_formule_reproduit_la_dette_du_resf(annee: int) -> None:
    reference = resf()[(annee, "dette")]
    modele = dette_resf_reproduite(annee)
    ecart = modele - reference
    assert abs(ecart) <= TOLERANCE_POINTS, (
        f"baseline_resf_dette_{annee} : modèle {modele:.2f} % du PIB, référence "
        f"{reference:.1f} % du PIB, écart {ecart:+.2f} point (tolérance ±{TOLERANCE_POINTS})"
    )
