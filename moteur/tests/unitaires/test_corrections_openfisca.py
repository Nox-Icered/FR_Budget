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
