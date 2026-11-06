"""Répartition par décile : l'export du site redonne le calcul du moteur."""

from __future__ import annotations

from typing import Any

import pytest
from fr_budget import scenario as sc
from fr_budget.menages import deciles as dc

from fr_budget_api.app import deciles

ANNEE = 2027
MESURES = [
    ("tva_taux_normal", 1.0),
    ("indexation_pensions_prestations", -1.0),
    ("csg_retraites", 0.5),
    ("remunerations_point_indice", 1.0),
]


def _site(export: dict[str, Any], mesures: list[tuple[str, float]]) -> list[list[float]]:
    """Calcul de web/lib/deciles.ts, reproduit ici : [bas, central, haut] par décile, Md€."""
    reglees = {lv: x for lv, x in mesures if x != 0}
    etendues = list(mesures)
    for ident, lev in export["leviers"].items():
        if "interaction" in lev:
            a, b = lev["interaction"]
            if a in reglees and b in reglees:
                etendues.append((ident, reglees[a] * reglees[b]))
    total = [[0.0, 0.0, 0.0] for _ in range(10)]
    for lv, x in etendues:
        if lv not in export["leviers"] or x == 0:
            continue
        lev = export["leviers"][lv]
        r = lev["rendement"]
        effets = [-x * r[b] for b in ("bas", "central", "haut")]
        for d in range(10):
            central = -x * r["central"] * lev["centrale"][d]
            candidats = [e * p[d] for e in effets for p in lev["variantes"]]
            total[d][0] += min(central, *candidats)
            total[d][1] += central
            total[d][2] += max(central, *candidats)
    return total


def test_export_redonne_le_moteur() -> None:
    export = deciles()
    moteur = dc.repartition([sc.Mesure(lv, x, ANNEE) for lv, x in MESURES])
    for d, (bas, central, haut) in enumerate(_site(export, MESURES)):
        assert central == pytest.approx(moteur.milliards[d].central)
        assert bas == pytest.approx(moteur.milliards[d].bas)
        assert haut == pytest.approx(moteur.milliards[d].haut)
    assert moteur.non_repartis == ["remunerations_point_indice"]
    assert "remunerations_point_indice" in export["non_repartis"]


def test_export_cite_ses_sources() -> None:
    export = deciles()
    assert "insee_cnd_2023" in export["sources"]
    assert len(export["unites_consommation_millions"]) == 10
    assert len(export["revenu_disponible_milliards"]) == 10
