"""Validation de la répartition par décile : forme de la répartition face aux évaluations de
réformes par l'Insee (modèle Ines, France, portrait social).

Références (``data/processed/deciles/validation_insee.csv``, voir
``pipelines/deciles/extraire_cnd.py``) :

- réforme de la prime d'activité de 2018 : France, portrait social 2019, dossier 3, figure 7
  (effet en euros par an, par dixième de niveau de vie), face à la clé du levier
  ``prime_activite_pente`` ;
- baisse de l'impôt sur le revenu de 2020 (taux de la première tranche imposable de 14 % à
  11 %, décote et seuils revus) : France, portrait social 2022, dossier 2, figure 4, face à la
  méthode des leviers de l'impôt sur le revenu : écart d'impôt par dixième fiscal du moteur du
  barème (même réforme que ``bareme_ir.validation_classes_moyennes_2020``), le k-ième dixième
  fiscal assimilé au k-ième dixième de niveau de vie.

Comparaison : part de chaque dixième dans l'effet total (les dixièmes de l'Insee comptent le
même nombre de personnes, comme les déciles des comptes distribués). Tolérance : écart d'au plus
10 points de part sur chaque dixième (choix du lot, à relire : la règle de publication ne fixe
de tolérance que pour le rendement).
"""

from __future__ import annotations

import csv

import numpy as np
import pytest

from fr_budget.agrege import bareme_ir
from fr_budget.menages import deciles as dc
from fr_budget.registres.verification import RACINE_DEPOT

TOLERANCE_POINTS = 10.0
FICHIER = RACINE_DEPOT / "data" / "processed" / "deciles" / "validation_insee.csv"


def _baisse_impot_revenu_2020() -> np.ndarray:
    apres, avant = bareme_ir.bareme_openfisca(2020), bareme_ir.bareme_openfisca(2019)
    revalorise = bareme_ir._indexe(avant, apres.seuils[-1] / avant.seuils[-1])
    v = np.array(bareme_ir.ecart_par_dixieme(revalorise, apres, 2020)[0])
    return np.asarray(v / v.sum())


CAS = {
    "fps2019_prime_activite_2018": lambda: dc.part_centrale("prime_activite_pente"),
    "fps2022_baisse_impot_revenu_2020": _baisse_impot_revenu_2020,
}


def _reference(ident: str) -> np.ndarray:
    with FICHIER.open(encoding="utf-8") as f:
        ligne = next(r for r in csv.DictReader(f) if r["reference"] == ident)
    v = np.array([float(ligne[f"d{i}"]) for i in range(1, dc.NOMBRE + 1)])
    return np.asarray(v / v.sum())


def ecart_max_points(ident: str) -> float:
    return float(100 * np.max(np.abs(CAS[ident]() - _reference(ident))))


@pytest.mark.validation
@pytest.mark.parametrize("ident", list(CAS))
def test_forme_de_la_repartition(ident: str) -> None:
    ecart = ecart_max_points(ident)
    assert ecart <= TOLERANCE_POINTS, f"{ident} : écart maximal {ecart:.1f} points de part"
