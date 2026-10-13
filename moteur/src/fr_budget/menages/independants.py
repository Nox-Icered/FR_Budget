"""Cotisations et contributions sociales d'un artisan (travailleur indépendant non agricole,
entreprise individuelle à l'impôt sur le revenu, régime réel), à partir de 2025.

Réforme de l'assiette (loi n° 2023-1250, art. 18 ; décrets n° 2024-688 et n° 2025-708 ; pages
de l'Urssaf « Réforme de l'assiette sociale… » et « Taux de cotisations - Artisan… ») :

- revenu brut = chiffre d'affaires moins les charges, autres que les cotisations sociales et la
  CSG déductibles ;
- assiette unique des cotisations et de la CSG-CRDS = revenu brut moins un abattement de 26 %,
  compris entre 1,76 % et 130 % du plafond annuel de la Sécurité sociale (PSS) ;
- barèmes de 2025 (maladie, indemnités journalières, retraite de base et complémentaire,
  invalidité-décès, allocations familiales, formation professionnelle, CSG-CRDS).

OpenFisca-France 176.1.2 applique les nouveaux taux de retraite à l'ancienne assiette (le
résultat fiscal) et ne connaît pas l'abattement : ce module le remplace pour les cotisations ;
OpenFisca reste utilisé pour l'impôt sur le revenu (résultat fiscal en entrée). Toutes les
valeurs viennent de ``registres/references/chiffrages.yaml`` (identifiants ``independant_*``) ;
le PSS et le SMIC horaire, des paramètres d'OpenFisca.

Non représentés : début d'activité (ACRE, assiettes forfaitaires), conjoint collaborateur,
cotisations facultatives, revenus de remplacement, outre-mer.
"""

from __future__ import annotations

from dataclasses import dataclass

from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.registres.acces import chiffrage

ANNEE_REFORME = 2025
"""Premières cotisations dues sur l'assiette réformée (décret n° 2024-688, article 6)."""
PRECISION_EUROS = 0.01
ITERATIONS_MAX = 100


def _c(nom: str) -> float:
    return chiffrage(f"independant_{nom}")


def pss_annuel(annee: int) -> float:
    """Plafond annuel de la Sécurité sociale (paramètre OpenFisca
    ``prelevements_sociaux.pss.plafond_securite_sociale_annuel``) au 1er janvier."""
    pss = systeme_socio_fiscal().parameters.prelevements_sociaux.pss
    return float(pss.plafond_securite_sociale_annuel(f"{annee}-01-01"))


def smic_horaire(annee: int) -> float:
    """SMIC horaire brut au 1er janvier (paramètre OpenFisca)."""
    smic = systeme_socio_fiscal().parameters.marche_travail.salaire_minimum.smic
    return float(smic.smic_b_horaire(f"{annee}-01-01"))


def assiette(revenu_brut: float, pss: float) -> float:
    """Revenu brut moins l'abattement forfaitaire, borné (art. D. 136-5)."""
    abattement = min(
        max(_c("abattement_assiette") * revenu_brut, _c("abattement_plancher") * pss),
        _c("abattement_plafond") * pss,
    )
    return max(revenu_brut - abattement, 0.0)


def taux_maladie(a: float, pss: float) -> float:
    """Taux de la cotisation maladie-maternité pour une assiette sous 3 PSS (art. D. 621-2) :
    nul sous 20 % du PSS, puis interpolé entre les seuils jusqu'au taux de base."""
    seuils = [_c(f"maladie_seuil_s{i}") * pss for i in range(6)]
    taux = [0.0] + [_c(f"maladie_taux_t{i}") for i in range(1, 6)]
    if a <= seuils[0]:
        return 0.0
    for k in range(1, len(seuils)):
        if a <= seuils[k]:
            part = (a - seuils[k - 1]) / (seuils[k] - seuils[k - 1])
            return taux[k - 1] + (taux[k] - taux[k - 1]) * part
    return taux[-1]


def maladie(a: float, pss: float) -> float:
    plafond = _c("maladie_seuil_s5") * pss
    if a <= plafond:
        return taux_maladie(a, pss) * a
    return _c("maladie_taux_t5") * plafond + _c("maladie_taux_au_dela_3_pss") * (a - plafond)


def indemnites_journalieres(a: float, pss: float) -> float:
    base = min(max(a, _c("ij_assiette_minimale") * pss), _c("ij_plafond") * pss)
    return _c("ij_taux") * base


def retraite_base(a: float, pss: float, smic_h: float) -> float:
    base = max(a, _c("retraite_base_assiette_minimale_heures_smic") * smic_h)
    return _c("retraite_base_plafonnee") * min(base, pss) + _c("retraite_base_deplafonnee") * base


def retraite_complementaire(a: float, pss: float) -> float:
    plafond = _c("retraite_complementaire_plafond") * pss
    return _c("retraite_complementaire_t1") * min(a, pss) + _c("retraite_complementaire_t2") * min(
        max(a - pss, 0.0), plafond - pss
    )


def invalidite_deces(a: float, pss: float) -> float:
    base = min(max(a, _c("invalidite_assiette_minimale") * pss), pss)
    return _c("invalidite_deces") * base


def allocations_familiales(a: float, pss: float) -> float:
    bas = _c("allocations_familiales_seuil_bas") * pss
    haut = _c("allocations_familiales_seuil_haut") * pss
    taux_plein = _c("allocations_familiales_taux")
    if a <= bas:
        return 0.0
    taux = taux_plein if a >= haut else taux_plein * (a - bas) / (haut - bas)
    return taux * a


def formation_professionnelle(pss: float) -> float:
    """Contribution forfaitaire d'un artisan, assise sur le PSS."""
    return _c("formation_artisan") * pss


@dataclass(frozen=True)
class CotisationsIndependant:
    """Montants annuels, en euros."""

    revenu_brut: float
    assiette: float
    maladie: float
    indemnites_journalieres: float
    retraite_base: float
    retraite_complementaire: float
    invalidite_deces: float
    allocations_familiales: float
    formation: float
    csg_deductible: float
    csg_non_deductible: float
    crds: float

    @property
    def cotisations(self) -> float:
        """Cotisations sociales obligatoires, formation professionnelle comprise."""
        return (
            self.maladie
            + self.indemnites_journalieres
            + self.retraite_base
            + self.retraite_complementaire
            + self.invalidite_deces
            + self.allocations_familiales
            + self.formation
        )

    @property
    def csg_crds(self) -> float:
        return self.csg_deductible + self.csg_non_deductible + self.crds

    @property
    def resultat_fiscal(self) -> float:
        """Revenu imposable : revenu brut moins les cotisations et la CSG déductibles."""
        return self.revenu_brut - self.cotisations - self.csg_deductible

    @property
    def revenu_net(self) -> float:
        """Revenu après toutes les cotisations et contributions sociales."""
        return self.revenu_brut - self.cotisations - self.csg_crds


def cotisations_artisan(
    revenu_brut: float, annee: int, ecart_csg_deductible: float = 0.0
) -> CotisationsIndependant:
    """Cotisations et contributions dues au titre de ``annee`` (2025 ou après) sur un revenu
    brut annuel. La CSG-CRDS (9,7 %, Urssaf) est répartie entre CSG déductible (6,8 %) et CRDS
    (0,5 %) d'après les taux des revenus d'activité de service-public.gouv.fr (fiche F2971).

    ``ecart_csg_deductible`` : variation du taux de CSG déductible (en fraction), pour l'effet
    d'un levier sur la CSG des revenus d'activité (``fr_budget.menages.leviers``)."""
    if annee < ANNEE_REFORME:
        msg = f"{annee} : barème des indépendants antérieur à la réforme non codé"
        raise ValueError(msg)
    pss, smic_h = pss_annuel(annee), smic_horaire(annee)
    a = assiette(revenu_brut, pss)
    csg_crds = (_c("csg_crds") + ecart_csg_deductible) * a
    taux_deductible = chiffrage("service_public_csg_activite_deductible") + ecart_csg_deductible
    csg_deductible = taux_deductible * a
    crds = chiffrage("service_public_crds_activite") * a
    return CotisationsIndependant(
        revenu_brut=revenu_brut,
        assiette=a,
        maladie=maladie(a, pss),
        indemnites_journalieres=indemnites_journalieres(a, pss),
        retraite_base=retraite_base(a, pss, smic_h),
        retraite_complementaire=retraite_complementaire(a, pss),
        invalidite_deces=invalidite_deces(a, pss),
        allocations_familiales=allocations_familiales(a, pss),
        formation=formation_professionnelle(pss),
        csg_deductible=csg_deductible,
        csg_non_deductible=csg_crds - csg_deductible - crds,
        crds=crds,
    )


def revenu_brut_pour_resultat(resultat_fiscal: float, annee: int) -> float:
    """Revenu brut dont le résultat fiscal vaut ``resultat_fiscal`` (dichotomie)."""
    bas, haut = resultat_fiscal, 3 * resultat_fiscal
    for _ in range(ITERATIONS_MAX):
        milieu = (bas + haut) / 2
        if cotisations_artisan(milieu, annee).resultat_fiscal < resultat_fiscal:
            bas = milieu
        else:
            haut = milieu
        if haut - bas < PRECISION_EUROS:
            break
    return (bas + haut) / 2
