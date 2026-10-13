"""Validation de la cascade du salaire contre le modèle de calcul de l'Urssaf.

Référence : modèle de calcul de mon-entreprise.urssaf.fr (paquet npm ``modele-social``),
version et cas dans ``registres/references/menages/urssaf_modele_social.json``,
générés par ``outils/references_urssaf/generer.mjs``.

Millésime : législation de janvier et juillet 2026.

Tolérance : 0,50 € par mois et par ligne de la cascade (proposée en phase 0, à valider).
OpenFisca reçoit le salaire brut calculé par le modèle Urssaf, pour comparer le même cas.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from fr_budget.menages.openfisca import HypothesesEmploi, cascade_salaire_mensuelle

TOLERANCE_EUROS_PAR_MOIS = 0.50

REFERENCE = (
    Path(__file__).parents[3] / "registres" / "references" / "menages" / "urssaf_modele_social.json"
)
CAS: list[dict[str, Any]] = json.loads(REFERENCE.read_text(encoding="utf-8"))["cas"]
LIGNES = ["salaire_brut", "cout_employeur", "net_avant_impot", "net_imposable"]


@pytest.mark.validation
@pytest.mark.parametrize("ligne", LIGNES)
@pytest.mark.parametrize("cas", CAS, ids=[c["id"] for c in CAS])
def test_cascade_salaire_egale_reference_urssaf(cas: dict[str, Any], ligne: str) -> None:
    reference = cas["resultats_mensuels"]
    apprentissage = cas.get("apprentissage")
    cascade = cascade_salaire_mensuelle(
        reference["salaire_brut"],
        cas["mois"],
        HypothesesEmploi(**cas["hypotheses"]),
        apprentissage_debut=apprentissage["contrat_debut"] if apprentissage else None,
    )
    modele = getattr(cascade, ligne)
    ecart = modele - reference[ligne]
    assert abs(ecart) <= TOLERANCE_EUROS_PAR_MOIS, (
        f"{ligne} : modèle {modele:.2f} €, référence Urssaf {reference[ligne]:.2f} €, "
        f"écart {ecart:+.2f} € (tolérance {TOLERANCE_EUROS_PAR_MOIS:.2f} €)"
    )
