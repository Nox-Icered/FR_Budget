from __future__ import annotations

import pytest

from fr_budget.menages import independants as ind

PSS = 47100.0


def test_assiette_abattue_de_26_pourcent_entre_plancher_et_plafond() -> None:
    assert ind.assiette(40000, PSS) == pytest.approx(40000 * 0.74)
    # Plancher : 1,76 % du PSS.
    assert ind.assiette(1000, PSS) == pytest.approx(max(1000 - 0.0176 * PSS, 0))
    # Plafond : 130 % du PSS.
    assert ind.assiette(500000, PSS) == pytest.approx(500000 - 1.3 * PSS)


@pytest.mark.parametrize("part", [0.2, 0.4, 0.6, 1.1, 2.0, 3.0])
def test_taux_maladie_continu_aux_seuils(part: float) -> None:
    a = part * PSS
    assert ind.taux_maladie(a - 0.01, PSS) == pytest.approx(
        ind.taux_maladie(a + 0.01, PSS), abs=1e-6
    )


def test_taux_maladie_aux_seuils_du_decret() -> None:
    attendus = {0.2: 0.0, 0.4: 0.015, 0.6: 0.04, 1.1: 0.065, 2.0: 0.077, 3.0: 0.085}
    for part, taux in attendus.items():
        assert ind.taux_maladie(part * PSS, PSS) == pytest.approx(taux)


def test_maladie_au_dela_de_3_pss() -> None:
    a = 4 * PSS
    assert ind.maladie(a, PSS) == pytest.approx(0.085 * 3 * PSS + 0.065 * PSS)


def test_revenu_brut_retrouve_le_resultat_fiscal() -> None:
    brut = ind.revenu_brut_pour_resultat(33000, 2025)
    assert ind.cotisations_artisan(brut, 2025).resultat_fiscal == pytest.approx(33000, abs=0.05)


def test_csg_crds_au_taux_de_9_7_pourcent_de_l_assiette() -> None:
    c = ind.cotisations_artisan(40000, 2025)
    assert c.csg_crds == pytest.approx(0.097 * c.assiette)
    assert c.csg_deductible == pytest.approx(0.068 * c.assiette)


def test_pas_de_bareme_avant_la_reforme() -> None:
    with pytest.raises(ValueError):
        ind.cotisations_artisan(40000, 2024)
