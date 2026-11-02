"""Export de la projection de la Commission européenne avec la baseline (page Trajectoires)."""

from __future__ import annotations

from fr_budget_api.app import serie_baseline


def test_commission_exportee_publiee_puis_prolongee() -> None:
    c = serie_baseline()["commission"]
    assert c["source"] == "ce_dsm_2025"
    assert c["derniere_annee_publiee"] == 2036
    valeurs = {v["annee"]: v for v in c["valeurs"]}
    assert valeurs[2036]["publiee"] and not valeurs[2037]["publiee"]
    assert valeurs[2036]["dette"]["central"] == 144.0
    assert max(valeurs) == serie_baseline()["valeurs"][-1]["annee"]
