"""Contrôles des comptes des APU extraits (lot 1.1 du plan).

Référence : INSEE, comptes nationaux annuels base 2020, édition 2025 (tableaux 3.101, 3.106,
3.201 à 3.212, 1.101 ; registres/datasets.yaml). Ces tests vérifient que l'extraction
reproduit les publications de l'INSEE et ses identités comptables :

- capacité de financement = recettes - dépenses, pour chaque sous-secteur et chaque année
  (tolérance : 0,01 Md€, arrondi des tableaux) ;
- capacité de financement (tableaux 3.2xx) = déficit au sens de Maastricht (tableau 3.106),
  depuis 2014 (le déficit notifié ne s'en distingue plus depuis octobre 2014, note du
  tableau 3.106) ; tolérance 0,01 Md€ ;
- le besoin de financement des APU est la somme de ceux de l'administration centrale, des
  administrations locales et de la sécurité sociale (tolérance 0,01 Md€) ;
- dette en % du PIB recalculée avec le PIB du tableau 1.101 = ratio publié par l'INSEE
  (tableau 3.101). Tolérance 0,055 point : arrondi du ratio publié au dixième (0,05 point)
  plus effet de l'arrondi de la dette publiée au dixième de milliard (moins de 0,005 point
  depuis 2015). Avant 2020, la ligne « Série du PIB utilisée » du tableau 3.101 ne reproduit
  pas le ratio publié (écart jusqu'à 0,30 point en 2018) ; le PIB du tableau 1.101 le
  reproduit (constat publié dans docs/fiches/comptes_apu.md).
"""

from __future__ import annotations

from typing import Any

import pytest
from python_calamine import CalamineWorkbook

from fr_budget.apu import comptes_apu, depenses_par_fonction, ratio_pib
from fr_budget.registres.verification import RACINE_DEPOT

SECTEURS = ["S13", "S1311", "S13111", "S13112", "S1313", "S1314"]
TOLERANCE_MONTANT = 0.01
TOLERANCE_RATIO = 0.055
PREMIERE_ANNEE_MAASTRICHT = 2014
ANNEES_CONTROLEES = range(2015, 2026)


@pytest.mark.validation
@pytest.mark.parametrize("secteur", SECTEURS)
def test_capacite_egale_recettes_moins_depenses(secteur: str) -> None:
    c = comptes_apu()
    for an in c.annees(secteur, "capacite_financement"):
        ecart = c.valeur(an, secteur, "recettes") - c.valeur(an, secteur, "depenses")
        assert ecart == pytest.approx(
            c.valeur(an, secteur, "capacite_financement"), abs=TOLERANCE_MONTANT
        ), f"{secteur} {an}"


@pytest.mark.validation
@pytest.mark.parametrize("secteur", SECTEURS)
def test_capacite_egale_deficit_maastricht(secteur: str) -> None:
    c = comptes_apu()
    for an in c.annees(secteur, "solde_maastricht"):
        if an >= PREMIERE_ANNEE_MAASTRICHT:
            assert c.valeur(an, secteur, "capacite_financement") == pytest.approx(
                c.valeur(an, secteur, "solde_maastricht"), abs=TOLERANCE_MONTANT
            ), f"{secteur} {an}"


@pytest.mark.validation
def test_solde_des_apu_somme_des_sous_secteurs() -> None:
    c = comptes_apu()
    for an in ANNEES_CONTROLEES:
        somme = sum(c.valeur(an, s, "solde_maastricht") for s in ("S1311", "S1313", "S1314"))
        assert somme == pytest.approx(
            c.valeur(an, "S13", "solde_maastricht"), abs=TOLERANCE_MONTANT
        )


def _ratios_publies() -> dict[tuple[int, str], float]:
    fichier = RACINE_DEPOT / "data" / "raw" / "apu" / "insee" / "t_3101_fr.xlsx"
    lignes: list[list[Any]] = (
        CalamineWorkbook.from_path(fichier).get_sheet_by_name("T_3101").to_python()
    )
    en_tete = next(lg for lg in lignes if str(lg[2]).strip() == "1978")
    debut = next(i for i, lg in enumerate(lignes) if "En % du produit intérieur brut" in str(lg[1]))
    publies = {}
    for lg in lignes[debut + 1 :]:
        if not str(lg[0]).startswith("S13"):
            break
        for j, an in enumerate(en_tete):
            if str(an).strip().isdigit() and isinstance(lg[j], float):
                publies[(int(str(an)), str(lg[0]).strip())] = lg[j]
    return publies


@pytest.mark.validation
def test_dette_en_pourcentage_du_pib_egale_au_ratio_publie() -> None:
    c = comptes_apu()
    publies = _ratios_publies()
    for an in ANNEES_CONTROLEES:
        for secteur in SECTEURS:
            calcule = ratio_pib(
                c.valeur(an, secteur, "dette_maastricht"), c.valeur(an, "S1", "pib")
            )
            assert calcule == pytest.approx(publies[(an, secteur)], abs=TOLERANCE_RATIO), (
                f"{secteur} {an} : {calcule:.2f} % calculé, {publies[(an, secteur)]} % publié"
            )


@pytest.mark.validation
@pytest.mark.parametrize("secteur", ["S13", "S1311", "S1313", "S1314"])
def test_total_cofog_eurostat_egal_aux_depenses_insee(secteur: str) -> None:
    """Total COFOG (Eurostat) = total des dépenses (INSEE), 2010-2022, à 0,05 Md€ près.

    2023 et 2024 ne sont pas testées : l'INSEE a actualisé ses tableaux le 28 août 2026 (compte
    semi-définitif), après les données reprises par Eurostat ; écarts publiés dans
    docs/fiches/comptes_apu.md.
    """
    c = comptes_apu()
    cofog = depenses_par_fonction()
    for an in range(2010, 2023):
        assert cofog[(an, secteur, "TOTAL")] == pytest.approx(
            c.valeur(an, secteur, "depenses"), abs=0.05
        ), f"{secteur} {an}"
