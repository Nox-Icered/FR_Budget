import pytest

from fr_budget.apu import ComptesApu, libelles_cofog, ratio_pib, solde_primaire


def test_solde_primaire_ajoute_les_interets_verses() -> None:
    assert solde_primaire(-150.0, 60.0) == pytest.approx(-90.0)


def test_ratio_au_pib_en_pourcentage() -> None:
    assert ratio_pib(3000.0, 2500.0) == pytest.approx(120.0)


def test_lecture_d_une_valeur() -> None:
    comptes = ComptesApu({(2025, "S13", "dette_maastricht"): 10.0})
    assert comptes.valeur(2025, "S13", "dette_maastricht") == 10.0
    assert comptes.annees("S13", "dette_maastricht") == [2025]
    with pytest.raises(KeyError):
        comptes.valeur(2024, "S13", "dette_maastricht")


def test_libelles_cofog() -> None:
    libelles = libelles_cofog()
    assert libelles["GF10"] == "Protection sociale"
    assert libelles["TOTAL"] == "Total"
