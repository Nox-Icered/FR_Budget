from fr_budget.menages.openfisca import (
    HypothesesEmploi,
    cascade_salaire_mensuelle,
    systeme_socio_fiscal,
)


def test_systeme_charge_une_seule_fois() -> None:
    assert systeme_socio_fiscal() is systeme_socio_fiscal()


def test_cascade_ordonnee_sans_mutuelle() -> None:
    # Cas construit à la main : seule la cohérence de la cascade est testée ici,
    # la justesse des montants relève des tests de validation.
    hypotheses = HypothesesEmploi(
        effectif_entreprise=10,
        taux_accident_travail=0.01,
        mutuelle_montant_mensuel=0,
        mutuelle_part_employeur=0,
    )
    cascade = cascade_salaire_mensuelle(3000, "2026-01", hypotheses)
    assert cascade.salaire_brut == 3000
    assert cascade.cout_employeur > cascade.salaire_brut > cascade.net_avant_impot > 0
