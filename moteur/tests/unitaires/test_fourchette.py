import pytest

from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.registres.acces import hypothese


def test_fourchette_ordonnee() -> None:
    f = Fourchette(1.0, 2.0, 3.0)
    assert (f.bas, f.central, f.haut) == (1.0, 2.0, 3.0)


def test_fourchette_desordonnee_refusee() -> None:
    with pytest.raises(ValueError, match="bas"):
        Fourchette(2.0, 1.0, 3.0)


def test_encadrer_prend_les_extremes_des_variantes() -> None:
    assert encadrer(2.0, [2.5, 1.5, 2.2]) == Fourchette(1.5, 2.0, 2.5)
    # Des variantes toutes au-dessus du central laissent le bas au central.
    assert encadrer(2.0, [2.1, 2.3]) == Fourchette(2.0, 2.0, 2.3)


def test_hypothese_lue_dans_le_registre() -> None:
    h = hypothese("tva_ecart_territorial_stable")
    assert h.plage.basse <= h.valeur_centrale <= h.plage.haute
    with pytest.raises(KeyError):
        hypothese("inexistante")
