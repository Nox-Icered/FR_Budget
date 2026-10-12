import re

import pytest

from fr_budget.registres.verification import RACINE_DEPOT
from fr_budget.validation import Comparaison, _definitions, comparer, tableau_markdown


def test_ecart_et_tolerance() -> None:
    c = Comparaison("x", 3.0, 2.5, 0.2, 0.1)
    assert not c.dans_la_tolerance
    assert Comparaison("x", 2.6, 2.5, 0.04, 0.1).dans_la_tolerance


def test_comparer_lit_la_reference_du_registre() -> None:
    c = comparer("dette_etat_choc_taux_100pb_an_1", 3.74)
    assert c.valeur_reference == pytest.approx(3.4)
    assert c.ecart == pytest.approx(0.1)


def test_memes_references_que_les_tests_de_validation_des_leviers() -> None:
    """Le résumé couvre exactement les références des tests de validation des leviers et de la
    dette."""
    textes = "".join(
        (RACINE_DEPOT / "moteur" / "tests" / "validation" / f).read_text(encoding="utf-8")
        for f in (
            "test_levier_tva.py",
            "test_dette_choc_taux.py",
            "test_levier_accises.py",
            "test_levier_impot_societes.py",
            "test_levier_depenses_fiscales.py",
            "test_levier_credits_missions.py",
            "test_levier_dotations.py",
            "test_levier_remunerations.py",
        )
    )
    attendues = set(re.findall(r'"((?:tva|dette)_[a-z0-9_]+)"', textes))
    attendues |= {
        f"tva_point_{nature}_{annee}_{taux}"
        for nature, annee in (("brut", 2025), ("net", 2025), ("brut", 2015))
        for taux in ("ensemble", "taux_2_1", "taux_5_5", "taux_10", "taux_20")
    }
    attendues |= {f"accises_ticpe_brute_totale_{annee}" for annee in (2023, 2024)}
    attendues |= {f"is_brut_{annee}_dgfip" for annee in (2024, 2025)}
    attendues |= {
        f"depenses_fiscales_{impot}_realisation_{annee}"
        for impot in ("impot_revenu", "impot_revenu_et_societes", "impot_societes")
        for annee in (2023, 2024)
    }
    attendues |= {
        "depenses_fiscales_ccomptes_total_2024_revise",
        "depenses_fiscales_ccomptes_total_2023_definitif",
    }
    attendues |= {f"credits_missions_depenses_constatees_{e}" for e in (2023, 2024, 2025)}
    attendues |= {
        f"dotations_{d}_execution_{a}" for d in ("dgf", "compensations") for a in (2023, 2024)
    }
    attendues |= {
        f"remunerations_point_{m}_{v}_{a}"
        for m, a in (("3_5", 2023), ("1_5", 2024))
        for v in ("fpe", "fpt", "fph", "total")
    }
    attendues = {a for a in attendues if not a.endswith("_") and "{" not in a}
    assert {r for r, _ in _definitions()} == attendues


def test_tableau_markdown() -> None:
    tableau = tableau_markdown(
        [Comparaison("a", 1.0, 1.0, 0.0, 0.1), Comparaison("b", 1.5, 1.0, 0.5, 0.1)]
    )
    assert "1 sur 2 dans la tolérance" in tableau
    assert "| b | 1.500 | 1.000 | +50.0% (±10%) | **hors tolérance** |" in tableau
