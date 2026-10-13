"""Validation de l'impôt sur le revenu des ménages types contre le simulateur d'impots.gouv.fr.

Référence : simulateur officiel de calcul de l'impôt 2026 sur les revenus 2025, modèle
simplifié (source ``impots_gouv_simulateur_ir_2026``). Les déclarations des ménages types
(``pipelines/menages/cas_impot.py``) y sont saisies par ``outils/references_impots/generer.mjs``,
qui relève la page de résultat dans ``registres/references/menages/impots_gouv_ir2026.json``.

Millésime : impôt 2026 sur les revenus 2025.

Tolérance : 2 € par an sur l'impôt et le revenu fiscal de référence (le simulateur reçoit des
salaires arrondis à l'euro et arrondit l'impôt à l'euro) ; nombre de parts identique.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from fr_budget.menages.types import ANNEE, PROFILS, cascade_annuelle, revenu_fiscal_et_parts

TOLERANCE_EUROS = 2.0
REFERENCE = (
    Path(__file__).parents[3] / "registres" / "references" / "menages" / "impots_gouv_ir2026.json"
)
CAS: list[dict[str, Any]] = json.loads(REFERENCE.read_text(encoding="utf-8"))["cas"]


def test_un_cas_par_menage_type() -> None:
    assert sorted(c["id"] for c in CAS) == sorted(PROFILS)
    assert all(c["revenus"] == ANNEE for c in CAS)


@pytest.mark.validation
@pytest.mark.parametrize("cas", CAS, ids=[c["id"] for c in CAS])
def test_impot_egal_au_simulateur(cas: dict[str, Any]) -> None:
    reference = cas["resultats"]["restant_a_payer"]
    modele = cascade_annuelle(cas["id"]).impot_revenu
    assert abs(modele - reference) <= TOLERANCE_EUROS, (
        f"{cas['id']} : modèle {modele:.0f} €, impots.gouv.fr {reference:.0f} € "
        f"(tolérance ±{TOLERANCE_EUROS:.0f} €)"
    )


@pytest.mark.validation
@pytest.mark.parametrize("cas", CAS, ids=[c["id"] for c in CAS])
def test_parts_et_revenu_fiscal_de_reference(cas: dict[str, Any]) -> None:
    rfr, parts = revenu_fiscal_et_parts(cas["id"])
    assert parts == cas["resultats"]["nombre_parts"]
    assert abs(rfr - cas["resultats"]["revenu_fiscal_reference"]) <= TOLERANCE_EUROS
