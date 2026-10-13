"""Validation du calcul des cotisations de l'artisan contre les montants publiés par l'Urssaf.

Aucun simulateur accessible n'applique encore l'assiette réformée de 2025 (le modèle de calcul
de l'Urssaf, ``modele-social`` 11.1.0, garde l'ancienne). Les fonctions du barème sont donc
confrontées aux montants que l'Urssaf calcule elle-même sur sa page « Taux de cotisations -
Artisan, commerçant et profession libérale non réglementée » (source ``urssaf_taux_ac_plnr``,
mise à jour le 27 février 2026) : cotisations minimales et maximales de 2026, avec le plafond
annuel de la Sécurité sociale et le SMIC horaire de 2026 d'OpenFisca.

Tolérance : 1 € par an (montants publiés arrondis à l'euro).

L'impôt sur le revenu de l'artisan type est validé avec les autres ménages types contre le
simulateur d'impots.gouv.fr (``test_menages_impot_revenu.py``).
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

from fr_budget.menages import independants as ind
from fr_budget.registres.acces import chiffrage

TOLERANCE_EUROS = 1.0
ANNEE = 2026
PSS = ind.pss_annuel(ANNEE)
SMIC_H = ind.smic_horaire(ANNEE)

CAS: dict[str, Callable[[], float]] = {
    # Assiette nulle : les minima s'appliquent.
    "urssaf_retraite_base_minimale_2026": lambda: ind.retraite_base(0.0, PSS, SMIC_H),
    "urssaf_ij_minimale_2026": lambda: ind.indemnites_journalieres(0.0, PSS),
    "urssaf_formation_artisan_2026": lambda: ind.formation_professionnelle(PSS),
    # Assiette au-delà des plafonds : les maxima s'appliquent.
    "urssaf_retraite_complementaire_maximale_2026": lambda: ind.retraite_complementaire(
        10 * PSS, PSS
    ),
    "urssaf_ij_maximale_2026": lambda: ind.indemnites_journalieres(10 * PSS, PSS),
    "urssaf_invalidite_maximale_2026": lambda: ind.invalidite_deces(10 * PSS, PSS),
}


@pytest.mark.validation
@pytest.mark.parametrize("identifiant", sorted(CAS))
def test_montant_publie_par_l_urssaf(identifiant: str) -> None:
    reference = chiffrage(identifiant)
    modele = CAS[identifiant]()
    assert abs(modele - reference) <= TOLERANCE_EUROS, (
        f"{identifiant} : modèle {modele:.2f} €, Urssaf {reference:.0f} € "
        f"(tolérance ±{TOLERANCE_EUROS:.0f} €)"
    )
