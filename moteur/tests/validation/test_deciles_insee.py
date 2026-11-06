"""Validation de la répartition par décile : forme de la répartition face aux évaluations de
réformes par l'Insee (modèle Ines, France, portrait social), ``deciles.validation_insee``.

Références (``data/processed/deciles/validation_insee.csv``, voir
``pipelines/deciles/extraire_cnd.py``) :

- réforme de la prime d'activité de 2018 : France, portrait social 2019, dossier 3, figure 7
  (effet en euros par an, par dixième de niveau de vie), face à la clé du levier
  ``prime_activite_pente`` ;
- baisse de l'impôt sur le revenu de 2020 (taux de la première tranche imposable de 14 % à
  11 %, décote et seuils revus) : France, portrait social 2022, dossier 2, figure 4, face à la
  méthode des leviers de l'impôt sur le revenu : écart d'impôt par dixième fiscal du moteur du
  barème, le k-ième dixième fiscal assimilé au k-ième dixième de niveau de vie.

Comparaison : part de chaque dixième dans l'effet total (les dixièmes de l'Insee comptent le
même nombre de personnes, comme les déciles des comptes distribués). Tolérance : écart d'au plus
10 points de part sur chaque dixième (choix du lot, à relire : la règle de publication ne fixe
de tolérance que pour le rendement).
"""

from __future__ import annotations

import pytest

from fr_budget.menages import deciles as dc


@pytest.mark.validation
@pytest.mark.parametrize("reference", list(dc.VALIDATIONS))
def test_forme_de_la_repartition(reference: str) -> None:
    c = next(c for c in dc.validation_insee() if c.reference == reference)
    assert c.dans_la_tolerance, (
        f"{reference} : écart maximal {c.ecart_max_points:.1f} points de part"
    )
