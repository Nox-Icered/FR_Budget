import pytest

from fr_budget.agrege.tva import (
    Assiette,
    assiette_consommation_finale,
    assiette_depense_fiscale,
    assiette_remanente,
    base_hors_taxe,
    point_tva,
    prorata_non_deductibilite,
    recette,
    repartition_par_taux,
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


def test_assiette_deduite_du_cout_d_un_taux_reduit() -> None:
    # Coût de 2 150 M€ d'un taux de 10 % par rapport au taux normal de 20 % : 21 500 M€ HT.
    assert assiette_depense_fiscale(2150.0, 0.1, 0.2) == pytest.approx(21_500.0)


def test_repartition_avec_reste_au_taux_normal() -> None:
    # 100 M€ HT au taux de 10 % (110 TTC) dans une consommation de 330 TTC.
    repartition = repartition_par_taux(330.0, {"intermediaire": 100.0}, TAUX)
    assert repartition.parts == {
        "intermediaire": pytest.approx(1 / 3),
        "normal": pytest.approx(2 / 3),
    }
    assert repartition.exces == 0.0


def test_repartition_quand_les_taux_reduits_depassent_la_consommation() -> None:
    # 110 TTC au taux de 10 % et 105,5 TTC au taux de 5,5 %, pour 200 TTC consommés :
    # tout est aux taux réduits, au prorata, et l'excès est signalé.
    repartition = repartition_par_taux(200.0, {"intermediaire": 100.0, "reduit": 100.0}, TAUX)
    assert repartition.parts == {
        "intermediaire": pytest.approx(110 / 215.5),
        "reduit": pytest.approx(105.5 / 215.5),
    }
    assert repartition.exces == pytest.approx(215.5 / 200 - 1)


def test_assiette_consommation_finale_d_un_produit_reparti() -> None:
    assiette = assiette_consommation_finale(
        [("p1", "FZ", 330.0)],
        {"p1": "intermediaire"},
        TAUX,
        "menages",
        {"p1": {"intermediaire": 1 / 3, "normal": 2 / 3}},
    )
    assert dict(assiette) == {
        ("intermediaire", "menages"): pytest.approx(100.0),
        ("normal", "menages"): pytest.approx(183.33, abs=0.01),
    }
