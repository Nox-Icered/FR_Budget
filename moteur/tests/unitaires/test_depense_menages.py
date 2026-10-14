"""Tests de la dépense supplémentaire des ménages à consommation inchangée
(fr_budget.menages.depense)."""

from __future__ import annotations

import pytest

from fr_budget.agrege import tva
from fr_budget.menages import depense as d

ANNEE = 2025


def test_parts_bornees_et_un_seul_poste_carburants() -> None:
    parts = d.parts_postes()
    assert all(0 <= p.basse <= p.haute <= 1 for p in parts.values())
    assert [k for k, p in parts.items() if p.carburant] == [d.POSTE_CARBURANTS]


@pytest.mark.parametrize("nomenclature", d.NOMENCLATURES)
def test_chaque_classe_a_tous_les_postes(nomenclature: str) -> None:
    for postes in d.depenses(nomenclature).values():
        assert set(postes) == set(d.parts_postes())


def test_facteurs_valent_un_en_2017() -> None:
    assert d.facteur_consommation(d.ANNEE_ENQUETE) == pytest.approx(1.0)
    assert d.facteur_volume_carburants(d.ANNEE_ENQUETE) == pytest.approx(1.0)


def test_effet_tva_identite() -> None:
    """Un point de taux normal : dépense au taux normal portée à l'année, divisée par 1 + t."""
    postes = d.depenses("decile")["1"]
    effet = d.effet_classe(postes, ANNEE).effets[d.TVA_NORMAL]
    normal = d.depense_taux_normal(postes)
    taux = tva.taux_tva(ANNEE)["normal"]
    attendu = normal.central * d.facteur_consommation(ANNEE) * 0.01 / (1 + taux)
    assert effet.central == pytest.approx(attendu)
    assert effet.bas <= effet.central <= effet.haut


def test_accises_somme_des_deux_leviers() -> None:
    """Un centime sur le gazole et sur les essences : un centime TTC sur tous les litres."""
    postes = d.depenses("type_menage")[d.ENSEMBLE]
    effets = d.effet_classe(postes, ANNEE).effets
    litres = d.litres_carburants(postes[d.POSTE_CARBURANTS], ANNEE)
    taux = tva.taux_tva(ANNEE)["normal"]
    total = effets[d.ACCISE_GAZOLE].central + effets[d.ACCISE_ESSENCES].central
    assert total == pytest.approx(litres * 0.01 * (1 + taux))


def test_poste_sans_taux_normal_sans_effet() -> None:
    """Un ménage qui ne dépense qu'en loyer (exonéré) ne paie rien de plus."""
    effet = d.effet_classe({"04111": 1000.0}, ANNEE).effets
    assert effet[d.TVA_NORMAL].haut == 0
    assert effet[d.ACCISE_GAZOLE].central == 0


def test_effet_croissant_avec_le_niveau_de_vie() -> None:
    """Les ménages plus aisés dépensent davantage : l'effet en euros du dixième décile dépasse
    celui du premier."""
    effets = {e.classe: e for e in d.effets("decile", ANNEE)}
    assert effets["10"].effets[d.TVA_NORMAL].central > effets["1"].effets[d.TVA_NORMAL].central


def test_classes_dans_l_ordre() -> None:
    assert [e.classe for e in d.effets("decile", ANNEE)] == [*map(str, range(1, 11)), d.ENSEMBLE]
