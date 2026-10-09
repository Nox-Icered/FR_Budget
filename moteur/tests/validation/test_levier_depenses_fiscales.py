"""Validation du levier « dépenses fiscales » : coût prévu face au coût réalisé.

Le rendement du levier est, par construction, le coût officiel prévu (tome II de Voies et
moyens). Sa validation compare donc ce que le modèle aurait affiché avec un millésime antérieur
(coût prévu pour l'année en cours par le PLF de l'année N, convention du tome II) au coût
réalisé publié deux ans plus tard (registres/references/chiffrages.yaml) :

- PLF 2024 (prévision 2023) face au PLF 2025 (réalisation 2023) ;
- PLF 2025 (prévision 2024) face au PLF 2026 (réalisation 2024).

Impôts : impôt sur le revenu, impôt sur le revenu et impôt sur les sociétés, impôt sur les
sociétés (environ 85 % du coût du levier en 2026). Tolérance : ±10 % (règle de publication,
CLAUDE.md). Ce n'est pas une source indépendante : la comparaison à la Cour des comptes reste
à faire.
"""

from __future__ import annotations

import pytest

from fr_budget.agrege.depenses_fiscales import cout_par_impot
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10


@pytest.mark.validation
@pytest.mark.parametrize("impot", ["impot_revenu", "impot_revenu_et_societes", "impot_societes"])
@pytest.mark.parametrize(("plf", "annee"), [(2024, 2023), (2025, 2024)])
def test_cout_prevu_face_au_cout_realise(impot: str, plf: int, annee: int) -> None:
    identifiant = f"depenses_fiscales_{impot}_realisation_{annee}"
    reference = chiffrage(identifiant)
    modele = cout_par_impot(plf, annee)[impot]
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"{identifiant} : prévision du PLF {plf} {modele:.0f} M€, réalisation {reference:.0f} M€, "
        f"écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
