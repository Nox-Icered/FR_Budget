"""Tests des crédits par mission (lot 2.5) : périmètre, exécution, plage."""

from __future__ import annotations

import pytest

from fr_budget.agrege.credits_missions import (
    MISSIONS_EXCLUES,
    identifiant,
    mission,
    missions,
    plage_ecart_execution,
    programmes_budget_general,
    total_credits,
    total_execution,
)
from fr_budget.registres.acces import chiffrage, hypothese

PRECISION = 1e-3
EUROS_PAR_MILLIARD = 1e9


def test_perimetre_hors_collectivites_pensions_et_prelevements() -> None:
    libelles = {m.libelle for m in missions()}
    assert not libelles & set(MISSIONS_EXCLUES)
    assert not libelles & {"Pensions", "PSRCT", "PSRUE", "T3_CAS"}
    assert "Enseignement scolaire" in libelles
    assert all(m.credits > 0 for m in missions())
    # 117 (charge de la dette) est du budget général mais hors du budget vert.
    assert "117" in programmes_budget_general()


def test_identifiants_lisibles_et_uniques() -> None:
    assert identifiant("Action extérieure de l'État") == "action_exterieure_de_l_etat"
    assert mission("defense").libelle == "Défense"
    with pytest.raises(ValueError, match="absente"):
        mission("relations_avec_les_collectivites_territoriales")


def test_total_egal_a_la_somme_des_missions() -> None:
    assert total_credits() == pytest.approx(sum(m.credits for m in missions()))


@pytest.mark.parametrize("exercice", [2023, 2024, 2025])
def test_depenses_constatees_saisies_egales_aux_donnees(exercice: int) -> None:
    _, constatees = total_execution(exercice)
    reference = chiffrage(f"credits_missions_depenses_constatees_{exercice}")
    assert reference == pytest.approx(constatees / EUROS_PAR_MILLIARD, abs=PRECISION)


def test_plage_egale_a_l_hypothese() -> None:
    basse, haute = plage_ecart_execution()
    h = hypothese("credits_missions_ecart_execution")
    assert h.plage.basse == pytest.approx(basse, abs=PRECISION)
    assert h.plage.haute == pytest.approx(haute, abs=PRECISION)


def test_les_programmes_redonnent_les_credits_de_la_mission() -> None:
    """Aide au chiffrage du site : chaque mission se décompose en ses programmes (PLF 2026)."""
    from fr_budget.agrege.credits_missions import missions, programmes

    for m in missions():
        liste = programmes(m.identifiant)
        assert liste
        assert sum(p.credits for p in liste) == pytest.approx(m.credits)
