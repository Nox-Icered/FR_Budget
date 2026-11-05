"""Impôt sur le revenu, structure : plafond de l'avantage procuré par le quotient familial.

Levier : variation de x % des plafonds de l'avantage en impôt procuré par chaque demi-part de
quotient familial (article 197 du code général des impôts ; paramètre OpenFisca
``impot_revenu.calcul_impot_revenu.plaf_qf.plafond_avantages_procures_par_demi_part``, 1 807 €
par demi-part pour les revenus de 2025). Une baisse des plafonds augmente l'impôt des foyers
dont l'avantage est plafonné.

Rendement d'une baisse de 1 % (plan validé le 5 novembre 2026, ``docs/fiches/
quotient_familial.md``, choix à relire) :

- valeur centrale : chiffrage de l'IGF et de l'IGAS (revue de dépenses de juin 2026, annexe IV,
  tableau 15) : 580 M€ pour une baisse de 10 % des plafonds, législation 2026, soit 58 M€ par
  point, tenu constant en part du PIB nominal ;
- plage : les deux baisses votées, chiffrées par le Gouvernement (PLF 2013 : 0,5 Md€ pour
  -14,4 % ; PLF 2014 : 1 Md€ pour -25 %), rapportées au point de baisse et portées en 2025 par
  le PIB nominal.

La réponse est supposée linéaire dans la plage du curseur (±25 %, la plus forte baisse chiffrée)
: une baisse plus forte touche plus de foyers, la limite est écrite dans la fiche.
"""

from __future__ import annotations

from fr_budget.agrege.indexation import facteur_pib
from fr_budget.fourchette import Fourchette, encadrer
from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage

ANNEE_REFERENCE = 2025
ANNEE_IGF = 2026
"""Législation du chiffrage de l'IGF et de l'IGAS, dont le rendement est pris pour 2026."""
BORNE = 25.0
"""Borne du curseur, en % des plafonds : la plus forte baisse chiffrée (PLF 2014, -25 %)."""
MILLIONS_PAR_MILLIARD = 1000.0
POURCENT = 100.0
ANNEES_HISTORIQUES = (2013, 2014)
PLAFONDS = {
    2013: ("qf_plafond_2012", "qf_plafond_2013"),
    2014: ("qf_plafond_2013", "qf_plafond_2014"),
}


def baisse_historique(annee: int) -> float:
    """Baisse des plafonds votée pour l'impôt de ``annee``, en % du plafond précédent."""
    avant, apres = (chiffrage(c) for c in PLAFONDS[annee])
    return POURCENT * (avant - apres) / avant


def _central_un_pourcent_2026() -> float:
    """Chiffrage de l'IGF et de l'IGAS rapporté à un point de baisse, en Md€ de 2026."""
    rendement = chiffrage("qf_baisse_10_rendement_igf_2026") / MILLIONS_PAR_MILLIARD
    return rendement / chiffrage("qf_baisse_10_taux_igf_2026")


def rendement_transpose(annee: int) -> float:
    """Chiffrage du Gouvernement de la baisse de ``annee``, rapporté à un point de baisse et
    porté en Md€ de 2025 par le PIB nominal."""
    rendement = chiffrage(f"qf_baisse_plafond_rendement_{annee}")
    par_point = rendement / baisse_historique(annee)
    return par_point * facteur_pib(ANNEE_REFERENCE) / facteur_pib(annee)


def rendement_un_pourcent() -> Fourchette:
    """Rendement d'une baisse de 1 % des plafonds, en Md€ de 2025 (fourchette)."""
    central = _central_un_pourcent_2026() * facteur_pib(ANNEE_REFERENCE) / facteur_pib(ANNEE_IGF)
    return encadrer(central, [rendement_transpose(a) for a in ANNEES_HISTORIQUES])


def rendement_baisse(pourcent: float, annee: int) -> float:
    """Rendement en ``annee`` d'une baisse de ``pourcent`` % des plafonds, valeur centrale, en
    Md€ courants (validation). Sensibilité de 2026 tenue constante en part du PIB nominal."""
    central = rendement_un_pourcent().central
    return pourcent * central * facteur_pib(annee) / facteur_pib(ANNEE_REFERENCE)


def plafond_general(annee: int) -> float:
    """Plafond général de l'avantage par demi-part pour les revenus de ``annee``, en €
    (OpenFisca, ``plaf_qf.plafond_avantages_procures_par_demi_part.general``)."""
    p = systeme_socio_fiscal().parameters(f"{annee}-01-01").impot_revenu.calcul_impot_revenu
    return float(p.plaf_qf.plafond_avantages_procures_par_demi_part.general)
