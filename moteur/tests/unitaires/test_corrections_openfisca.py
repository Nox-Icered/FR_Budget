from importlib.metadata import version

from fr_budget.menages.corrections import charger_corrections
from fr_budget.menages.openfisca import HypothesesEmploi, cascade_salaire_mensuelle

HYPOTHESES_AVEC_MUTUELLE = HypothesesEmploi(
    effectif_entreprise=10,
    taux_accident_travail=0.01,
    mutuelle_montant_mensuel=50,
    mutuelle_part_employeur=0.6,
)


def test_registre_vise_la_version_installee() -> None:
    # Une montée de version d'OpenFisca impose de revoir chaque correction.
    assert charger_corrections()["openfisca_france_version"] == version("openfisca-france")


def test_part_patronale_mutuelle_ajoutee_au_seul_net_imposable() -> None:
    corrigee = cascade_salaire_mensuelle(3000, "2026-01", HYPOTHESES_AVEC_MUTUELLE)
    publiee = cascade_salaire_mensuelle(3000, "2026-01", HYPOTHESES_AVEC_MUTUELLE, corrige=False)
    part_patronale = 50 * 0.6
    assert abs(corrigee.net_imposable - publiee.net_imposable - part_patronale) < 0.01
    assert abs(corrigee.net_avant_impot - publiee.net_avant_impot) < 0.01


def test_correction_mutuelle_sans_effet_avant_2013() -> None:
    corrigee = cascade_salaire_mensuelle(3000, "2012-06", HYPOTHESES_AVEC_MUTUELLE)
    publiee = cascade_salaire_mensuelle(3000, "2012-06", HYPOTHESES_AVEC_MUTUELLE, corrige=False)
    assert corrigee == publiee


def test_taux_ags_corrige_hausse_le_cout_employeur() -> None:
    hypotheses = HypothesesEmploi(
        effectif_entreprise=10,
        taux_accident_travail=0.01,
        mutuelle_montant_mensuel=0,
        mutuelle_part_employeur=0,
    )
    corrigee = cascade_salaire_mensuelle(3000, "2026-01", hypotheses)
    publiee = cascade_salaire_mensuelle(3000, "2026-01", hypotheses, corrige=False)
    ecart_de_taux = 0.0025 - 0.002
    assert abs(corrigee.cout_employeur - publiee.cout_employeur - 3000 * ecart_de_taux) < 0.01


SANS_MUTUELLE = HypothesesEmploi(
    effectif_entreprise=4,
    taux_accident_travail=0.0208,
    mutuelle_montant_mensuel=0,
    mutuelle_part_employeur=0.5,
)


def test_chaque_correction_formule_a_sa_fonction() -> None:
    from fr_budget.menages.corrections_formules import FORMULES

    formules = {c["id"] for c in charger_corrections()["corrections"] if c["type"] == "formule"}
    assert formules == set(FORMULES)


def test_apprenti_contrat_ancien_exonere_sous_79_pourcent_du_smic() -> None:
    # 1 400 € en juin 2026 : environ 75 % du SMIC, sous le plafond de 79 % des contrats
    # conclus avant le 1er mars 2025. Net égal au brut ; sans correction, CSG et CRDS.
    corrigee = cascade_salaire_mensuelle(
        1400, "2026-06", SANS_MUTUELLE, apprentissage_debut="2024-09-01"
    )
    publiee = cascade_salaire_mensuelle(
        1400, "2026-06", SANS_MUTUELLE, apprentissage_debut="2024-09-01", corrige=False
    )
    assert abs(corrigee.net_avant_impot - 1400) < 0.01
    assert corrigee.net_imposable == 0
    assert publiee.net_avant_impot < 1400 - 100


def test_apprenti_contrat_recent_preleve_au_dela_de_50_pourcent_du_smic() -> None:
    from fr_budget.menages.openfisca import smic_mensuel_brut

    brut = 1400
    corrigee = cascade_salaire_mensuelle(
        brut, "2026-06", SANS_MUTUELLE, apprentissage_debut="2025-09-01"
    )
    au_dela = brut - 0.5 * smic_mensuel_brut("2026-06")
    preleve = brut - corrigee.net_avant_impot
    # Cotisations salariales, CSG et CRDS sur la seule part au-delà de 50 % du SMIC : entre
    # 10 et 30 % de cette part, et rien sur le reste.
    assert 0.10 * au_dela < preleve < 0.30 * au_dela
