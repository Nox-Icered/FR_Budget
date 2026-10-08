import re

import pytest

from fr_budget.registres.verification import RACINE_DEPOT
from fr_budget.validation import Comparaison, _definitions, comparer


def test_ecart_et_tolerance() -> None:
    c = Comparaison("x", 3.0, 2.5, 0.2, 0.1)
    assert not c.dans_la_tolerance
    assert Comparaison("x", 2.6, 2.5, 0.04, 0.1).dans_la_tolerance


def test_comparer_lit_la_reference_du_registre() -> None:
    c = comparer("dette_etat_choc_taux_100pb_an_1", 3.74)
    assert c.valeur_reference == pytest.approx(3.4)
    assert c.ecart == pytest.approx(0.1)


def test_memes_references_que_les_tests_de_validation_des_leviers() -> None:
    """Le résumé couvre exactement les références des tests de validation TVA et dette."""
    textes = "".join(
        (RACINE_DEPOT / "moteur" / "tests" / "validation" / f).read_text(encoding="utf-8")
        for f in ("test_levier_tva.py", "test_dette_choc_taux.py")
    )
    attendues = set(re.findall(r'"((?:tva|dette)_[a-z0-9_]+)"', textes))
    attendues |= {
        f"tva_point_{nature}_{annee}_{taux}"
        for nature, annee in (("brut", 2025), ("net", 2025), ("brut", 2015))
        for taux in ("ensemble", "taux_2_1", "taux_5_5", "taux_10", "taux_20")
    }
    attendues = {a for a in attendues if not a.endswith("_") and "{" not in a}
    assert {r for r, _ in _definitions()} == attendues
