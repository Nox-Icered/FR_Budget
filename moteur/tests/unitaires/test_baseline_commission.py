"""Projection de la Commission européenne à politique inchangée (fr_budget.baseline_commission)."""

from __future__ import annotations

import pytest

from fr_budget import baseline_commission as bc
from fr_budget.baseline import ANNEE_FIN
from fr_budget.registres.acces import hypothese


def test_serie_publiee_de_la_fiche_france() -> None:
    """Debt Sustainability Monitor 2025, fiche France : 116,3 % en 2025, 144,0 % en 2036."""
    s = bc.serie_publiee()
    assert min(s) == 2024 and max(s) == 2036
    assert s[2025] == 116.3
    assert s[2036] == 144.0
    assert bc.scenarios_2036()["central"] == s[2036]


def test_hypotheses_concordent_avec_la_serie_publiee() -> None:
    """Le registre recopie des valeurs tirées de la série : elles doivent rester exactes."""
    basse, centrale, haute = bc.pentes_prolongement()
    pente = hypothese(bc.HYPOTHESE_PENTE)
    assert pente.valeur_centrale == pytest.approx(centrale, abs=1e-3)
    assert pente.plage.basse == pytest.approx(basse, abs=1e-3)
    assert pente.plage.haute == pytest.approx(haute, abs=1e-3)
    assert hypothese(bc.HYPOTHESE_ECART).plage.haute == pytest.approx(bc.ecart_haut_publie())


def test_annees_publiees_reprises_telles_quelles() -> None:
    s = bc.serie_publiee()
    for ligne in bc.trajectoire(ANNEE_FIN):
        if ligne.publiee:
            assert ligne.dette.central == s[ligne.annee]
            assert ligne.dette.bas == s[ligne.annee]


def test_prolongement_lineaire_apres_2036() -> None:
    lignes = {lg.annee: lg for lg in bc.trajectoire(ANNEE_FIN)}
    assert not lignes[2037].publiee
    pente = hypothese(bc.HYPOTHESE_PENTE).valeur_centrale
    assert lignes[2046].dette.central == pytest.approx(144.0 + 10 * pente)
    assert lignes[2040].dette.central - lignes[2039].dette.central == pytest.approx(pente)


def test_fourchette_jusqu_au_scenario_le_plus_eleve() -> None:
    lignes = {lg.annee: lg for lg in bc.trajectoire(ANNEE_FIN)}
    assert lignes[2026].dette.haut == lignes[2026].dette.central
    assert lignes[2036].dette.haut == pytest.approx(max(bc.scenarios_2036().values()))
    for lg in lignes.values():
        assert lg.dette.bas <= lg.dette.central <= lg.dette.haut
