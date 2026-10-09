"""Validation du taux apparent : surcoût d'un choc de taux sur la dette de l'État.

Référence : PLF 2027, projet annuel de performances « Engagements financiers de l'État »,
page 40 (registres/references/chiffrages.yaml, module « dynamique_dette ») : un choc de
+1 point sur toute la courbe au 1er janvier 2027 coûte 3,4 Md€ la première année et
« environ 19 Md€ » la cinquième (2031). Millésime : PLF 2027. Tolérance : ±10 % (règle de
publication, CLAUDE.md).

La cinquième année est calculée avec l'encours de fin 2026 tenu constant (modèle actuel) ; la
référence est arrondie (« environ »).
"""

from __future__ import annotations

import pytest

from fr_budget.dette import surcout_choc_taux_etat
from fr_budget.registres.acces import chiffrage

TOLERANCE = 0.10


@pytest.mark.validation
def test_surcout_premiere_annee_d_un_choc_de_taux() -> None:
    reference = chiffrage("dette_etat_choc_taux_100pb_an_1")
    modele = surcout_choc_taux_etat(annee=1).central
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"dette_etat_choc_taux_100pb_an_1 : modèle {modele:.2f} Md€, référence "
        f"{reference:.2f} Md€, écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )


@pytest.mark.validation
def test_surcout_cinquieme_annee_d_un_choc_de_taux() -> None:
    reference = chiffrage("dette_etat_choc_taux_100pb_an_5")
    modele = surcout_choc_taux_etat(annee=5).central
    ecart = (modele - reference) / reference
    assert abs(ecart) <= TOLERANCE, (
        f"dette_etat_choc_taux_100pb_an_5 : modèle {modele:.2f} Md€, référence "
        f"{reference:.2f} Md€, écart {ecart:+.1%} (tolérance ±{TOLERANCE:.0%})"
    )
