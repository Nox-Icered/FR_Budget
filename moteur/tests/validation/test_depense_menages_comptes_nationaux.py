"""Validation de l'indicateur de dépense des ménages : part de la consommation au taux normal de
TVA dans l'enquête Budget de famille 2017 (valeur centrale : milieu de la plage des postes
mixtes), confrontée à la même part dans la consommation des ménages des comptes nationaux de
l'Insee (base 2020), produits rattachés à un régime par le levier TVA
(``registres/tva/correspondance_produits.csv`` et répartition des produits mixtes), hors loyers
imputés aux propriétaires, que l'enquête ne compte pas.

Références : comptes nationaux 2015 et 2022 (années encadrant l'enquête et disponibles au niveau
le plus fin). Tolérance : ±10 % (règle de publication, CLAUDE.md).
"""

from __future__ import annotations

import pytest

from fr_budget.menages import depense as d

TOLERANCE = 0.10


@pytest.mark.validation
@pytest.mark.parametrize("annee", d.ANNEES_CONTROLE)
def test_part_au_taux_normal(annee: int) -> None:
    modele = d.part_taux_normal()
    reference = d.part_taux_normal_comptes_nationaux(annee)
    ecart = (modele.central - reference) / reference
    assert modele.bas <= reference <= modele.haut
    assert abs(ecart) <= TOLERANCE, (
        f"Budget de famille 2017 {modele.central:.3f}, comptes nationaux {annee} "
        f"{reference:.3f}, écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
