"""Effet d'un barème de l'impôt sur le revenu saisi sur le site, pour les ménages types.

Le site est statique : il ne peut pas lancer OpenFisca pour un barème quelconque. L'écart
d'impôt de chaque foyer est donc recalculé dans le navigateur (``web/lib/bareme-ir.ts``) avec
les étapes d'OpenFisca-France (176.1.2) qui dépendent du barème, à partir de grandeurs du foyer
calculées ici une fois pour toutes (revenu net imposable, parts, adultes, montant maximal de
l'avantage du quotient familial) :

1. impôt avec quotient familial : ``parts x barème(rni / parts)`` (``ir_brut``) ;
2. impôt sans quotient familial : ``adultes x barème(rni / adultes)`` (``ir_ss_qf``) ;
3. plafonnement : ``max(ir_brut, ir_ss_qf - plafond)``, où le plafond ne dépend pas du barème
   (``ir_plaf_qf``, première partie) ;
4. décote arrondie, puis impôt net arrondi (``decote``, ``decote_gain_fiscal``, ``ip_net``) ;
5. réductions et crédits du foyer inchangés, puis seuil de mise en recouvrement
   (``correction_ir_seuils_recouvrement``).

Ce calcul est contrôlé contre OpenFisca : une réforme d'OpenFisca qui remplace le barème et la
décote (``legislation_bareme``) redonne le même écart pour les barèmes de contrôle
(``fr_budget.agrege.bareme_ir.BAREMES_CONTROLE``). Les réductions complémentaires après
plafonnement (anciens combattants, invalides…) ne sont pas recalculées : aucun ménage type
n'est concerné.
"""

from __future__ import annotations

import copy
import warnings
from dataclasses import asdict, dataclass
from functools import cache
from typing import Any

from openfisca_core.periods import period as periode
from openfisca_core.reforms import Reform

from fr_budget.agrege.bareme_ir import BAREMES_CONTROLE, Bareme, bareme_openfisca, impot_par_part
from fr_budget.menages import types
from fr_budget.menages.openfisca import systeme_socio_fiscal

SEUIL_TRES_HAUT = 1e12
"""Seuil des tranches d'OpenFisca rendues inactives quand le barème saisi en compte moins."""


@dataclass(frozen=True)
class FoyerBareme:
    """Grandeurs d'un foyer fiscal qui ne dépendent pas du barème (année des ménages types)."""

    rni: float
    parts: float
    adultes: float
    plafond_qf: float
    """Avantage maximal du quotient familial, en euros (OpenFisca, ``ir_plaf_qf``)."""
    autres: float
    """Écart entre l'impôt net (``ip_net``) et l'impôt avant seuils de mise en recouvrement :
    réductions et crédits du foyer, supposés inchangés."""
    impot: float
    """Impôt payé avec le barème de référence, en euros (positif)."""


@cache
def seuil_recouvrement(annee: int = types.ANNEE) -> float:
    """Impôt sous lequel il n'est pas mis en recouvrement (OpenFisca, ``recouvrement``)."""
    p = systeme_socio_fiscal().parameters(f"{annee}-01-01").impot_revenu.calcul_impot_revenu
    return float(p.recouvrement.min_avant_credits_impots)


def _plafond_qf(sim: Any, annee: str) -> list[float]:
    """Plafond de l'avantage du quotient familial, première partie de la formule ``ir_plaf_qf``
    d'OpenFisca (B1, B2 ou B3 selon la situation du foyer)."""

    def v(nom: str) -> Any:
        return sim.calculate(nom, annee)

    p = sim.tax_benefit_system.parameters(f"{annee}-01-01").impot_revenu.calcul_impot_revenu
    plaf = p.plaf_qf.plafond_avantages_procures_par_demi_part
    parts, adultes = v("nbptr"), v("nb_adult")
    aa0 = (parts - adultes) * 2
    aa1 = [min((n - 1) * 2, 2) for n in parts]
    resultat = []
    for i in range(len(parts)):
        b1 = plaf.celib_enf * aa1[i] / 2 + plaf.general * (aa0[i] - aa1[i])
        b2 = plaf.general * aa0[i]
        b3 = plaf.celib
        celib = bool(v("celibataire_ou_divorce")[i])
        c61 = celib and bool(v("caseT")[i])
        c63 = (celib or bool(v("veuf")[i])) and v("nb_pac")[i] == 0 and bool(v("caseL")[i])
        b = b1 if c61 else (b3 if c63 else b2)
        resultat.append(float(b))
    return resultat


@cache
def foyers(identifiant: str, variante: str = types.CENTRAL) -> tuple[FoyerBareme, ...]:
    """Foyers fiscaux du ménage type (revenus de l'année des ménages types)."""
    sim = types._simulation(identifiant, types.ANNEE, variante)
    annee = str(types.ANNEE)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        rni, parts, adultes = (sim.calculate(n, annee) for n in ("rni", "nbptr", "nb_adult"))
        ip_net = sim.calculate("ip_net", annee)
        avant = -sim.calculate("impot_revenu_avant_seuils_mise_recouvrement", annee)
        paye = -sim.calculate("impot_revenu_restant_a_payer", annee)
        plafonds = _plafond_qf(sim, annee)
    return tuple(
        FoyerBareme(
            float(rni[i]),
            float(parts[i]),
            float(adultes[i]),
            plafonds[i],
            float(ip_net[i] - avant[i]),
            float(paye[i]),
        )
        for i in range(len(rni))
    )


def _arrondi(x: float) -> float:
    """Arrondi au plus proche, comme ``around`` de NumPy (moitiés vers le pair)."""
    return float(round(x))


def impot_foyer(bareme: Bareme, f: FoyerBareme, annee: int = types.ANNEE) -> float:
    """Impôt payé par le foyer avec ``bareme``, en euros (même calcul que le site)."""
    brut = f.parts * impot_par_part(bareme, f.rni / f.parts)
    sans_qf = f.adultes * impot_par_part(bareme, f.rni / f.adultes)
    plafonne = max(brut, max(0.0, sans_qf - f.plafond_qf))
    decote = 0.0
    if bareme.decote is not None:
        decote = _arrondi(bareme.decote.montant(plafonne, couple=f.adultes >= 2))  # noqa: PLR2004
        decote = _arrondi(min(decote, plafonne))
    net = _arrondi(plafonne - decote)
    avant = max(0.0, net - f.autres)
    return 0.0 if avant <= seuil_recouvrement(annee) else avant


def ecart_menage(bareme: Bareme, identifiant: str, variante: str = types.CENTRAL) -> float:
    """Écart d'impôt du ménage type entre ``bareme`` et le barème de référence, en euros par
    an (positif : l'impôt augmente)."""
    reference = bareme_openfisca(types.ANNEE)
    return sum(
        impot_foyer(bareme, f) - impot_foyer(reference, f) for f in foyers(identifiant, variante)
    )


class ReformeBareme(Reform):  # type: ignore[misc]
    """Réforme d'OpenFisca : barème et décote remplacés à partir du 1er janvier de l'année des
    ménages types (contrôle du calcul du site)."""

    name = "Barème de l'impôt sur le revenu saisi"

    def __init__(self, systeme: Any, bareme: Bareme) -> None:
        self._bareme = bareme
        super().__init__(systeme)

    def apply(self) -> None:
        b, debut = self._bareme, periode(f"{types.ANNEE}-01-01")

        def modifier(parametres: Any) -> Any:
            ir = parametres.impot_revenu
            echelle = ir.bareme_ir_depuis_1945.bareme
            while len(echelle.brackets) < len(b.seuils):
                echelle.brackets.append(copy.deepcopy(echelle.brackets[-1]))
            for i, tranche in enumerate(echelle.brackets):
                if i < len(b.seuils):
                    seuil, taux = b.seuils[i], b.taux[i]
                else:
                    seuil, taux = SEUIL_TRES_HAUT + i, b.taux[-1]
                tranche.threshold.update(start=debut, value=seuil)
                tranche.rate.update(start=debut, value=taux)
            d = ir.calcul_impot_revenu.plaf_qf.decote
            celib, couple, taux_decote = (
                (0.0, 0.0, 0.0)
                if b.decote is None
                else (b.decote.seuil_celibataire, b.decote.seuil_couple, b.decote.taux)
            )
            d.seuil_celib.update(start=debut, value=celib)
            d.seuil_couple.update(start=debut, value=couple)
            d.taux.update(start=debut, value=taux_decote)
            return parametres

        self.modify_parameters(modifier_function=modifier)


def legislation_bareme(bareme: Bareme) -> types.Legislation:
    return types.Legislation(systeme=ReformeBareme(systeme_socio_fiscal(), bareme))


def ecart_openfisca(bareme: Bareme, identifiant: str) -> float:
    """Même écart calculé par OpenFisca avec le barème réformé (contrôle), en euros."""
    apres = types.cascade_type_reformee(identifiant, legislation_bareme(bareme))
    return apres.impot_revenu - types.cascade_annuelle(identifiant).impot_revenu


def donnees_site() -> dict[str, object]:
    """Foyers des ménages types (revenu central, bas et haut) et écarts des barèmes de contrôle
    (calcul du site, égal à celui d'OpenFisca : ``test_menages_bareme``)."""
    reference = bareme_openfisca(types.ANNEE)
    variantes = (types.CENTRAL, types.BAS, types.HAUT)
    return {
        "seuil_recouvrement": seuil_recouvrement(),
        "menages": {
            ident: {v: [asdict(f) for f in foyers(ident, v)] for v in variantes}
            for ident in types.PROFILS
        },
        "controles": {
            nom: {ident: ecart_menage(construire(reference), ident) for ident in types.PROFILS}
            for nom, construire in BAREMES_CONTROLE
        },
    }
