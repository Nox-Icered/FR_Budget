import pytest

from fr_budget.agrege.tva import (
    Assiette,
    assiette_consommation_finale,
    assiette_remanente,
    base_hors_taxe,
    point_tva,
    prorata_non_deductibilite,
    recette,
    taux_tva,
)

TAUX = {"super_reduit": 0.021, "reduit": 0.055, "intermediaire": 0.1, "normal": 0.2}


def test_base_hors_taxe_d_un_achat_ttc() -> None:
    assert base_hors_taxe(120.0, 0.2) == pytest.approx(100.0)
    # Achat d'une branche qui ne déduit que la moitié de la TVA : la moitié reste dans le prix.
    assert base_hors_taxe(110.0, 0.2, 0.5) == pytest.approx(100.0)


def test_prorata_part_non_taxee_de_la_consommation_finale() -> None:
    consommations = [("p1", "KZ", 30.0), ("p2", "KZ", 10.0), ("p3", "CA", 50.0)]
    regimes = {"p1": "exonere", "p2": "normal", "p3": "reduit"}
    pnd = prorata_non_deductibilite(
        consommations, regimes, {"KZ": "exonere", "CA": "reduit", "OZ": "hors_champ"}
    )
    assert pnd == {"KZ": pytest.approx(0.75), "CA": 0.0, "OZ": 1.0}


def test_assiette_consommation_finale_ignore_exonere() -> None:
    assiette = assiette_consommation_finale(
        [("p1", "CA", 105.5), ("p2", "KZ", 50.0)],
        {"p1": "reduit", "p2": "exonere"},
        TAUX,
        "menages",
    )
    assert dict(assiette) == {("reduit", "menages"): pytest.approx(100.0)}


def test_assiette_remanente_proportionnelle_a_la_part_non_deductible() -> None:
    assiette = assiette_remanente({"CG": 110.0}, {"CG": "normal"}, TAUX, 0.5)
    assert assiette["normal"] == pytest.approx(50.0)
    assert assiette_remanente({"CG": 110.0}, {"CG": "normal"}, TAUX, 0.0) == {}


def test_point_et_recette() -> None:
    assiette = Assiette(
        {
            ("normal", "menages"): 100_000.0,
            ("normal", "apu"): 50_000.0,
            ("reduit", "menages"): 20_000.0,
        }
    )
    point = point_tva(assiette)
    assert point.brut["taux_20"] == pytest.approx(1.5)
    assert point.net["taux_20"] == pytest.approx(1.0)
    assert point.brut["ensemble"] == pytest.approx(1.7)
    assert recette(assiette, TAUX) == pytest.approx(31.1)


def test_taux_2022_lus_dans_openfisca() -> None:
    assert taux_tva(2022) == TAUX
