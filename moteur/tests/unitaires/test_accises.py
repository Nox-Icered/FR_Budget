"""Tests unitaires du module des accises sur les produits énergétiques (lot 2.2)."""

from __future__ import annotations

import pytest

from fr_budget.agrege.accises import (
    MASSES_VOLUMIQUES,
    assiette_levier,
    hectolitres,
    recette_brute,
    tarifs,
    ventes,
    volumes_rembourses,
)
from fr_budget.registres.acces import chiffrage


def test_conversion_tonnes_en_hectolitres() -> None:
    # 832 kg/m³ : 832 tonnes font 1 000 m³, soit 10 000 hl.
    assert hectolitres(832.0, 832.0) == pytest.approx(10_000.0)


def test_masses_volumiques_de_la_base_carbone() -> None:
    assert MASSES_VOLUMIQUES == {"gazole": 832.0, "essence": 747.0, "fod": 845.0}


def test_tarifs_openfisca_et_gnr_2024() -> None:
    t2023, t2024 = tarifs(2023), tarifs(2024)
    assert t2023["gazole"] == pytest.approx(59.40)
    assert t2023["gnr"] == pytest.approx(18.82)
    assert t2024["gnr"] == chiffrage("accises_tarif_gnr_non_agricole_2024")
    assert t2024["e10"] == pytest.approx(66.29)


def test_ventes_annuelles_sdes() -> None:
    v = ventes(2024)
    assert v["gazole"] == pytest.approx(27_654_619.675)
    assert "super_sans_plomb" not in v


def test_recette_brute_lineaire_dans_les_tarifs() -> None:
    """Hausse de 1 €/hl du gazole : la recette brute augmente du volume de gazole en hl."""
    base = recette_brute(2024)
    plus = recette_brute(2024, hausse_gazole=1.0)
    volume = hectolitres(ventes(2024)["gazole"], MASSES_VOLUMIQUES["gazole"])
    assert plus - base == pytest.approx(volume / 1e9)


def test_volumes_rembourses_par_la_depense_fiscale() -> None:
    """Volume remboursé au transport routier = dépense fiscale / écart de tarif."""
    v = volumes_rembourses(2025)
    ecart = tarifs(2025)["gazole"] - chiffrage("accises_tarif_trm_2025")
    assert v["transport_routier_marchandises"] == pytest.approx(
        chiffrage("accises_remboursement_trm_2025") * 1e6 / ecart
    )


def test_assiette_du_levier_nette_des_remboursements() -> None:
    a = assiette_levier(2025)
    brut = hectolitres(ventes(2025)["gazole"], MASSES_VOLUMIQUES["gazole"])
    assert a["gazole"] == pytest.approx(brut - sum(volumes_rembourses(2025).values()))
    assert 0 < a["gazole"] < brut
    assert a["essences"] > 0
