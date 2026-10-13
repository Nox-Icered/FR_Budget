"""Ménage saisi par l'utilisateur : traduction de la saisie en profil et calcul de sa cascade.

Règle 5 de CLAUDE.md : la saisie n'est ni enregistrée ni journalisée. Ce module ne garde rien
(pas de cache, pas de journal) ; le calcul passe par :func:`fr_budget.menages.types.cascade_profil`,
sans cache lui aussi.

Choix (``docs/fiches/menages_types.md``, profil saisi) :

- un ou deux adultes ; deux adultes forment un couple marié ou pacsé (déclaration commune) ;
- chaque adulte est salarié (salaire brut mensuel), retraité (pension brute mensuelle) ou
  indépendant artisan (résultat fiscal mensuel) ; le montant est le même sur toutes les années
  de la simulation, comme pour les ménages types ;
- un adulte seul avec enfants coche la case T (parent isolé) ;
- seule l'année de naissance est demandée : la naissance est fixée au 1er janvier pour un
  adulte et au 1er juillet pour un enfant (milieu d'année, pour l'âge des prestations).
"""

from __future__ import annotations

from dataclasses import dataclass

from fr_budget.menages.types import (
    ANNEE,
    INDEPENDANT,
    RETRAITE,
    SMIC,
    Adulte,
    CascadeMenage,
    Profil,
    cascade_profil,
)

STATUTS = {"salarie": SMIC, "retraite": RETRAITE, "independant": INDEPENDANT}
"""Statut saisi → niveau du profil (le niveau d'un salarié est remplacé par son montant)."""
ADULTES_MAX = 2
ENFANTS_MAX = 8
MONTANT_MENSUEL_MAX = 100_000.0
AGE_MIN_ADULTE = 16
AGE_MAX = 110
AGE_MAX_ENFANT = 25
LIBELLE = "Ménage saisi"


@dataclass(frozen=True)
class AdulteSaisi:
    statut: str
    """« salarie », « retraite » ou « independant »."""
    montant_mensuel: float
    """Salaire brut, pension brute ou résultat fiscal, en euros par mois."""
    annee_naissance: int
    cadre: bool = False
    """Salarié cadre (cotisations des cadres)."""


@dataclass(frozen=True)
class MenageSaisi:
    adultes: tuple[AdulteSaisi, ...]
    annees_naissance_enfants: tuple[int, ...] = ()


class SaisieInvalideError(ValueError):
    """Saisie hors des bornes acceptées ; le message ne reprend aucune valeur saisie."""


def _verifier(menage: MenageSaisi, annee: int) -> None:
    if not 1 <= len(menage.adultes) <= ADULTES_MAX:
        msg = "un ou deux adultes"
        raise SaisieInvalideError(msg)
    if len(menage.annees_naissance_enfants) > ENFANTS_MAX:
        msg = f"au plus {ENFANTS_MAX} enfants"
        raise SaisieInvalideError(msg)
    for a in menage.adultes:
        if a.statut not in STATUTS:
            msg = "statut inconnu"
            raise SaisieInvalideError(msg)
        if not 0 <= a.montant_mensuel <= MONTANT_MENSUEL_MAX:
            msg = f"montant mensuel entre 0 et {MONTANT_MENSUEL_MAX:.0f} €"
            raise SaisieInvalideError(msg)
        if not annee - AGE_MAX <= a.annee_naissance <= annee - AGE_MIN_ADULTE:
            msg = "année de naissance d'un adulte hors bornes"
            raise SaisieInvalideError(msg)
        if a.cadre and a.statut != "salarie":
            msg = "seul un salarié peut être cadre"
            raise SaisieInvalideError(msg)
    for n in menage.annees_naissance_enfants:
        if not annee - AGE_MAX_ENFANT <= n <= annee:
            msg = "année de naissance d'un enfant hors bornes"
            raise SaisieInvalideError(msg)


def profil(menage: MenageSaisi, annee: int = ANNEE) -> Profil:
    """Profil OpenFisca du ménage saisi ; :class:`SaisieInvalideError` hors des bornes."""
    _verifier(menage, annee)
    adultes = tuple(
        Adulte(
            f"{a.annee_naissance}-01-01",
            STATUTS[a.statut],
            cadre=a.cadre,
            montant_mensuel=a.montant_mensuel,
        )
        for a in menage.adultes
    )
    enfants = tuple(f"{n}-07-01" for n in menage.annees_naissance_enfants)
    return Profil(LIBELLE, adultes, enfants, parent_isole=len(adultes) == 1 and bool(enfants))


def calculer(menage: MenageSaisi, annee: int = ANNEE) -> CascadeMenage:
    """Cascade annuelle du ménage saisi, sans rien garder de la saisie."""
    return cascade_profil(profil(menage, annee), annee)
