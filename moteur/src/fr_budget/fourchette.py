"""Type des résultats : toute estimation est donnée en valeur basse, centrale et haute.

Règle 4 de CLAUDE.md : « Fourchettes, jamais un chiffre unique ». Les bornes viennent des
plages des hypothèses du registre (``registres/hypotheses.yaml``).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class Fourchette:
    bas: float
    central: float
    haut: float

    def __post_init__(self) -> None:
        if not self.bas <= self.central <= self.haut:
            msg = (
                f"fourchette désordonnée : bas {self.bas}, central {self.central}, haut {self.haut}"
            )
            raise ValueError(msg)


def encadrer(central: float, variantes: Iterable[float]) -> Fourchette:
    """Fourchette dont les bornes sont les extrêmes du central et des variantes calculées."""
    valeurs = [central, *variantes]
    return Fourchette(min(valeurs), central, max(valeurs))
