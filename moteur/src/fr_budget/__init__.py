"""Moteur de calcul du simulateur public du budget des administrations publiques françaises.

Les calculs sont des fonctions pures. Toute valeur numérique vient du registre de données
ou du registre d'hypothèses (voir ``registres/``), jamais du code.
"""

from importlib.metadata import version

__version__ = version("fr-budget")
