"""Comparaisons du modèle aux chiffrages de référence, pour la page Validation du site.

CLAUDE.md : « L'écart avec la référence est toujours affiché sur la page Validation, y compris
quand le modèle est moins bon. » Ce module calcule, pour chaque référence testée dans
``moteur/tests/validation/``, la valeur du modèle, la référence et l'écart relatif, avec les
mêmes fonctions et les mêmes paramètres que les tests (qui restent la vérification
exécutée par la CI).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import partial

from fr_budget.agrege.accises import recette_brute
from fr_budget.agrege.impot_societes import is_brut
from fr_budget.agrege.tva import estimer_point_tva, estimer_recette_totale
from fr_budget.dette import surcout_choc_taux_etat
from fr_budget.registres.acces import chiffrage

TOLERANCE_PUBLICATION = 0.10
"""Règle de publication d'un levier (CLAUDE.md) : ±10 % sur le rendement à 1 an."""

TAUX_TVA = ("ensemble", "taux_2_1", "taux_5_5", "taux_10", "taux_20")


@dataclass(frozen=True)
class Comparaison:
    reference: str
    """Identifiant du chiffrage (registres/references/chiffrages.yaml)."""
    modele: float
    valeur_reference: float
    ecart: float
    """Écart relatif (modèle - référence) / référence."""
    tolerance: float

    @property
    def dans_la_tolerance(self) -> bool:
        return abs(self.ecart) <= self.tolerance


def comparer(
    reference: str, modele: float, tolerance: float = TOLERANCE_PUBLICATION
) -> Comparaison:
    valeur = chiffrage(reference)
    return Comparaison(reference, modele, valeur, (modele - valeur) / valeur, tolerance)


def _point_tva(annee_comptes: int, annee_cible: int, nature: str, taux: str) -> float:
    point = estimer_point_tva(annee_comptes, annee_cible)
    return (point.brut if nature == "brut" else point.net)[taux]


def _choc_taux_premiere_annee() -> float:
    return surcout_choc_taux_etat(annee=1).central


def _choc_taux_cinquieme_annee() -> float:
    return surcout_choc_taux_etat(annee=5).central


def _definitions() -> list[tuple[str, Callable[[], float]]]:
    definitions: list[tuple[str, Callable[[], float]]] = []
    for taux in TAUX_TVA:
        definitions += [
            (f"tva_point_brut_2025_{taux}", partial(_point_tva, 2022, 2025, "brut", taux)),
            (f"tva_point_net_2025_{taux}", partial(_point_tva, 2022, 2025, "net", taux)),
            (f"tva_point_brut_2015_{taux}", partial(_point_tva, 2015, 2015, "brut", taux)),
        ]
    definitions += [
        ("tva_nette_totale_2022_dgtresor", partial(estimer_recette_totale, 2022)),
        ("tva_nette_totale_execution_2024", partial(estimer_recette_totale, 2024)),
        ("dette_etat_choc_taux_100pb_an_1", _choc_taux_premiere_annee),
        ("dette_etat_choc_taux_100pb_an_5", _choc_taux_cinquieme_annee),
        ("accises_ticpe_brute_totale_2023", partial(recette_brute, 2023)),
        ("accises_ticpe_brute_totale_2024", partial(recette_brute, 2024)),
        ("is_brut_2024_dgfip", partial(is_brut, 2024)),
        ("is_brut_2025_dgfip", partial(is_brut, 2025)),
    ]
    return definitions


def comparaisons() -> list[Comparaison]:
    """Toutes les comparaisons modèle-référence, dans l'ordre des tests de validation."""
    return [comparer(reference, calcul()) for reference, calcul in _definitions()]


def tableau_markdown(liste: list[Comparaison]) -> str:
    """Tableau des écarts, publié par la CI dans le résumé de chaque exécution."""
    hors = sum(not c.dans_la_tolerance for c in liste)
    lignes = [
        f"## Écarts aux références : {len(liste) - hors} sur {len(liste)} dans la tolérance",
        "",
        "| Référence | Modèle | Référence | Écart | Résultat |",
        "|---|---|---|---|---|",
    ]
    for c in liste:
        resultat = "dans la tolérance" if c.dans_la_tolerance else "**hors tolérance**"
        lignes.append(
            f"| {c.reference} | {c.modele:.3f} | {c.valeur_reference:.3f} | {c.ecart:+.1%} "
            f"(±{c.tolerance:.0%}) | {resultat} |"
        )
    return "\n".join(lignes) + "\n"


if __name__ == "__main__":
    print(tableau_markdown(comparaisons()))
