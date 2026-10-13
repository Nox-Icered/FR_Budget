"""Validation des prestations des ménages types : barèmes publiés et simulateur officiel.

1. Barèmes : montants publiés par service-public.gouv.fr au 1er avril 2026 (fiches F2882,
   F13213, F1878, F815 et actualité A16506, saisis dans ``registres/references/chiffrages.yaml``)
   comparés aux paramètres d'OpenFisca et aux montants calculés pour les ménages types en 2026.
   Les montants publiés des prestations familiales sont nets de CRDS : le montant d'OpenFisca
   est multiplié par (1 - taux de la CRDS). Tolérance : 0,02 €, arrondi au centime du montant
   publié et du montant net.
2. Simulateur : prime d'activité estimée par le simulateur RSA - prime d'activité de
   mesdroitssociaux.gouv.fr (source ``mesdroitssociaux_simulateur_rsa_pa``), législation et
   ressources de 2026, cas saisis par ``outils/references_prestations/generer.mjs``
   (``registres/references/menages/mesdroitssociaux_pa_2026.json``), comparée à la prime
   d'activité nette de CRDS d'OpenFisca. Tolérance : 2 € par mois ; le simulateur reçoit des
   ressources arrondies à l'euro et donne un montant à l'euro.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from fr_budget.menages.openfisca import systeme_socio_fiscal
from fr_budget.menages.prestations import (
    ANNEE_SIMULATEUR,
    MOIS_RESULTAT,
    PRIME_ACTIVITE_VERSEE,
    PROFILS_AVEC_PRESTATIONS,
    calcul,
    cas_simulateur,
    taux_crds,
)
from fr_budget.registres.acces import chiffrage

TOLERANCE_BAREME = 0.02
TOLERANCE_SIMULATEUR = 2.0
DATE_2026 = f"{ANNEE_SIMULATEUR}-06-01"
REFERENCE = (
    Path(__file__).parents[3]
    / "registres"
    / "references"
    / "menages"
    / "mesdroitssociaux_pa_2026.json"
)
CAS: list[dict[str, Any]] = json.loads(REFERENCE.read_text(encoding="utf-8"))["cas"]


def _parametres() -> Any:
    return systeme_socio_fiscal().parameters


def _ppa() -> Any:
    return _parametres().prestations_sociales.solidarite_insertion.minima_sociaux.ppa.pa_m


def _bmaf(date: str) -> float:
    return float(_parametres().prestations_sociales.prestations_familiales.bmaf.bmaf(date))


def _seuil_bonification() -> float:
    """Seuil de la bonification, exprimé par OpenFisca en heures de SMIC brut."""
    smic = _parametres().marche_travail.salaire_minimum.smic.smic_b_horaire(DATE_2026)
    return float(_ppa().bonification.seuil_bonification(DATE_2026) * smic)


PARAMETRES = {
    "service_public_bmaf_2026": lambda: _bmaf(DATE_2026),
    "service_public_bmaf_2025": lambda: _bmaf(f"{ANNEE_SIMULATEUR - 1}-06-01"),
    "service_public_pa_montant_forfaitaire_2026": lambda: float(_ppa().montant_de_base(DATE_2026)),
    "service_public_pa_part_revenus_professionnels_2026": lambda: float(
        _ppa().majoration_ressources_revenus_activite(DATE_2026)
    ),
    "service_public_pa_seuil_bonification_2026": _seuil_bonification,
}


def _net_crds(montant: float) -> float:
    return montant * (1 - taux_crds(MOIS_RESULTAT))


MONTANTS = {
    # Deux enfants de 7 et 10 ans en octobre 2026, ressources du couple sous le premier seuil.
    "service_public_af_deux_enfants_2026": lambda: _net_crds(
        calcul("couple_2_enfants", "af", MOIS_RESULTAT)[0]
    ),
    # Enfants de 9 et 6 ans au 31 décembre 2025 : deux allocations de la tranche 6 à 10 ans.
    "service_public_ars_6_10_ans_2026": lambda: _net_crds(
        calcul("couple_2_enfants", "ars", str(ANNEE_SIMULATEUR))[0] / 2
    ),
    "service_public_asf_2026": lambda: _net_crds(
        calcul("parent_isole_1_enfant", "asf", MOIS_RESULTAT)[0]
    ),
}


@pytest.mark.validation
@pytest.mark.parametrize("identifiant", sorted(PARAMETRES | MONTANTS))
def test_bareme_publie(identifiant: str) -> None:
    modele = (PARAMETRES | MONTANTS)[identifiant]()
    reference = chiffrage(identifiant)
    assert abs(modele - reference) <= TOLERANCE_BAREME, (
        f"{identifiant} : modèle {modele:.4f}, service-public.gouv.fr {reference:.4f}"
    )


def test_cas_saisis_dans_le_simulateur_a_jour() -> None:
    """Les ressources, enfants et logement saisis sont ceux du ménage type aujourd'hui."""
    assert {c["id"] for c in CAS} <= set(PROFILS_AVEC_PRESTATIONS)
    for c in CAS:
        attendu = cas_simulateur(c["id"])
        for cle in ("mois_ressources", "mois_resultat", "couple", "enfants", "logement"):
            assert c[cle] == attendu[cle], (c["id"], cle)
        assert c["autres_ressources"] == attendu["autres_ressources"], c["id"]
        assert [a["salaires"] for a in c["adultes"]] == [
            a["salaires"] for a in attendu["adultes"]
        ], c["id"]


@pytest.mark.validation
@pytest.mark.parametrize("cas", CAS, ids=[c["id"] for c in CAS])
def test_prime_activite_egale_au_simulateur(cas: dict[str, Any]) -> None:
    reference = cas["resultats"]["prime_activite"]
    modele = calcul(cas["id"], PRIME_ACTIVITE_VERSEE, cas["mois_resultat"])[0]
    assert abs(modele - reference) <= TOLERANCE_SIMULATEUR, (
        f"{cas['id']} : modèle {modele:.2f} €, mesdroitssociaux.gouv.fr {reference} € "
        f"(tolérance ±{TOLERANCE_SIMULATEUR:.0f} €)"
    )
