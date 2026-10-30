"""Tests des dépenses fiscales (lot 2.4) : extraction, convention du tome II, catalogue, plages."""

from __future__ import annotations

import pytest

from fr_budget.agrege.depenses_fiscales import (
    IMPOTS_EXCLUS,
    IMPOTS_LEVIER,
    catalogue,
    codes,
    cout,
    cout_impot_levier,
    cout_par_impot,
    depense,
    ecart_par_impot,
    ecarts_prevision,
    ligne,
    plage_ecart_par_depense,
)
from fr_budget.registres.acces import chiffrage, hypothese

DEMI_MILLION = 0.5
PRECISION_PLAGE = 1e-3


@pytest.mark.parametrize("plf", [2024, 2025, 2026])
def test_extraction_redonne_les_totaux_publies(plf: int) -> None:
    """Somme des fiches, convention du tome II = ligne « Total » du tableau par impôt."""
    for annee in (plf - 2, plf - 1, plf):
        total = sum(cout_par_impot(plf, annee).values())
        reference = chiffrage(f"depenses_fiscales_total_plf{plf}_{annee}")
        assert total == pytest.approx(reference, abs=DEMI_MILLION)


def test_nombre_de_fiches_par_tome() -> None:
    """Nombre de dépenses fiscales annoncé par chaque tome (467, 474, 465)."""
    assert [len(codes(p)) for p in (2024, 2025, 2026)] == [467, 474, 465]


def test_non_chiffree_reprend_le_dernier_montant() -> None:
    """940102 : « nc » en 2026 dans le PLF 2026, reprend le montant de 2025."""
    assert ligne(2026, 2026, "940102").statut == "nc"  # type: ignore[union-attr]
    c = cout(2026, 2026, "940102")
    assert c is not None
    assert c.annee_chiffrage == 2025
    assert c.valeur == ligne(2026, 2025, "940102").cout  # type: ignore[union-attr]


def test_remboursements_des_accises_egaux_aux_fiches() -> None:
    """Les chiffrages saisis pour le levier des accises égalent les fiches du PLF 2026."""
    for identifiant, code in (
        ("accises_remboursement_trm_2025", "800221"),
        ("accises_remboursement_transport_collectif_2025", "800222"),
        ("accises_remboursement_taxis_2025", "800220"),
    ):
        assert chiffrage(identifiant) == ligne(2026, 2025, code).cout  # type: ignore[union-attr]


def test_catalogue_hors_tva_et_accises_et_cout_positif() -> None:
    liste = catalogue()
    assert liste
    assert all(d.impot not in IMPOTS_EXCLUS and d.cout > 0 for d in liste)
    assert len({d.code for d in liste}) == len(liste)
    # 800221 (accise sur les énergies) : hors du levier, déjà couverte par le levier des accises.
    with pytest.raises(ValueError, match="absente"):
        depense("800221")


def test_cout_par_impot_du_levier_egale_le_tableau_publie() -> None:
    """Coût 2026 des dépenses d'un impôt dans le levier = coût 2026 de la partie du tome."""
    publie = cout_par_impot(2026, 2026)
    for impot in IMPOTS_LEVIER:
        assert cout_impot_levier(impot) == pytest.approx(publie[impot])
    with pytest.raises(ValueError, match="hors du levier"):
        cout_impot_levier("tva")


def test_plage_par_depense_egale_l_hypothese() -> None:
    basse, haute = plage_ecart_par_depense(2024, 2026, 2024)
    h = hypothese("depenses_fiscales_ecart_depense")
    assert h.plage.basse == pytest.approx(basse, abs=PRECISION_PLAGE)
    assert h.plage.haute == pytest.approx(haute, abs=PRECISION_PLAGE)
    assert len(ecarts_prevision(2024, 2026, 2024)) == 274


def test_plages_par_impot_egales_aux_hypotheses() -> None:
    comparaisons = ((2024, 2025, 2023), (2025, 2026, 2024), (2024, 2026, 2024))
    for impot in IMPOTS_LEVIER:
        ecarts = [ecart_par_impot(*c)[impot] for c in comparaisons]
        h = hypothese(f"depenses_fiscales_ecart_{impot}")
        assert h.valeur_centrale == 0.0
        assert h.plage.basse == pytest.approx(min(0.0, *ecarts), abs=PRECISION_PLAGE)
        assert h.plage.haute == pytest.approx(max(0.0, *ecarts), abs=PRECISION_PLAGE)


def test_fiche_descriptive_telle_que_publiee() -> None:
    """Fiche 120113 du tome II du PLF 2026 (page de la « Liste des dépenses fiscales ») :
    finalité, bénéficiaires, création et mission reprises telles que publiées."""
    from fr_budget.agrege.depenses_fiscales import catalogue, fiches_descriptives

    fiches = fiches_descriptives()
    f = fiches["120113"]
    assert f.finalite == (
        "Inciter les salariés à utiliser les transports en commun pour le trajet domicile-travail"
    )
    assert f.beneficiaires == "6 100 000 Ménages"
    assert (f.creation, f.modification) == ("1948", "2025")
    assert f.mission.startswith("Travail, emploi et administration des ministères sociaux")
    assert all(d.code in fiches for d in catalogue())
