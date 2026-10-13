"""Validation du retraité type : CSG des pensions contre le barème publié.

Référence : service-public.gouv.fr, fiche F2971 (vérifiée le 1er juin 2026), taux de CSG sur
les pensions de retraite en 2026 selon le revenu fiscal de référence de 2024, saisis dans
``registres/references/chiffrages.yaml`` (``service_public_csg_pension_*_2026``), comparés aux
paramètres d'OpenFisca. Tolérance : égalité (montants publiés à l'euro, taux au dixième de
point).

L'impôt sur le revenu du retraité type est validé avec les autres ménages types contre le
simulateur d'impots.gouv.fr (``test_menages_impot_revenu.py``).
"""

from __future__ import annotations

from typing import Any

import pytest

from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage

DATE = "2026-06-01"


def _csg() -> Any:
    return systeme_socio_fiscal().parameters.prelevements_sociaux.contributions_sociales.csg


def _seuil(nom: str, champ: str) -> float:
    return float(getattr(getattr(_csg().remplacement.seuils, nom), champ)(DATE))


def _taux(nom: str) -> float:
    return float(getattr(_csg().remplacement.pensions_retraite_invalidite, nom)(DATE))


PARAMETRES = {
    "seuil_taux_zero_1_part": lambda: _seuil("seuil_rfr1", "seuil_rfr1"),
    "seuil_taux_reduit_1_part": lambda: _seuil("seuil_rfr2", "seuil_rfr2"),
    "seuil_taux_median_1_part": lambda: _seuil("seuil_rfr3", "seuil_rfr3"),
    "majoration_demi_part_taux_zero": lambda: _seuil("seuil_rfr1", "demi_part_suppl_rfr1"),
    "majoration_demi_part_taux_reduit": lambda: _seuil("seuil_rfr2", "demi_part_suppl_rfr2"),
    "majoration_demi_part_taux_median": lambda: _seuil("seuil_rfr3", "demi_part_suppl_rfr3"),
    "taux_reduit": lambda: _taux("taux_reduit"),
    "taux_median": lambda: _taux("taux_median"),
    "taux_normal": lambda: _taux("taux_plein"),
}


@pytest.mark.validation
@pytest.mark.parametrize("nom", sorted(PARAMETRES))
def test_bareme_csg_pensions(nom: str) -> None:
    reference = chiffrage(f"service_public_csg_pension_{nom}_2026")
    assert PARAMETRES[nom]() == pytest.approx(reference)
