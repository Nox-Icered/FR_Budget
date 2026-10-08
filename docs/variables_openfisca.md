# Variables et paramètres OpenFisca utilisés

Relevés dans le paquet installé `openfisca-france` 176.1.2 (`openfisca-core` 44.7.1), le 7 octobre 2026. Une montée de version d'OpenFisca impose de revérifier cette liste.

## Variables

| Variable | Entité | Période | Libellé OpenFisca | Valeur par défaut | Usage |
|----------|--------|---------|-------------------|-------------------|-------|
| `salaire_de_base` | individu | mois | Salaire de base | 0 | Entrée : salaire brut |
| `effectif_entreprise` | individu | mois | Effectif de l'entreprise | 0 | Entrée : hypothèse du cas type |
| `taux_accident_travail` | individu | mois | Approximation du taux accident à partir de l'exposition au risque donnée | 0 | Entrée : hypothèse du cas type |
| `complementaire_sante_montant` | individu | mois | Montant de la complémentaire santé obligatoire retenue par l'employeur | 0 | Entrée : hypothèse du cas type |
| `complementaire_sante_part_employeur` | individu | mois | Part de la complémentaire santé obligatoire payée par l'employeur | 0 | Entrée : hypothèse du cas type |
| `categorie_salarie` | individu | mois | Catégorie de salarié | `prive_non_cadre` | Laissée par défaut |
| `contrat_de_travail` | individu | mois | Type de durée de travail | `temps_plein` | Laissée par défaut |
| `salaire_super_brut` | individu | mois | Coût du travail à court terme. Inclut les exonérations et allègements de charges | 0 | Sortie : coût employeur |
| `salaire_net_a_payer` | individu | mois | Salaire net à payer (fiche de paie) | 0 | Sortie : net avant impôt |
| `salaire_imposable` | individu | mois | Salaires imposables | 0 | Sortie : net imposable (corrigée, voir `registres/corrections_openfisca.yaml`) |
| `allegement_general` | individu | mois | Réduction générale des cotisations patronales (dite réduction Fillon) | 0 | Diagnostic |
| `ags` | individu | mois | Contribution AGS (employeur) | 0 | Diagnostic |
| `complementaire_sante_employeur` | individu | mois | Couverture complémentaire santé collective d'entreprise - part employeur (montant négatif) | 0 | Correction du net imposable |
| `cout_du_travail` | individu | mois | Coût du travail à long terme. Inclut les charges, aides et crédits différés | 0 | Non utilisée (voir ci-dessous) |
| `salaire_net` | individu | mois | Salaires nets d'après définition INSEE | 0 | Corrigée en même temps que `salaire_imposable`, dont elle dépend |
| `impot_revenu_restant_a_payer` | foyer fiscal | année | Impôt sur le revenu restant à payer | 0 | Prochaine étape : net après impôt |
| `ppa` | famille | mois | Prime pour l'activité | 0 | Prochaine étape : net après impôt |
| `revenu_disponible` | ménage | année | Revenu disponible du ménage | 0 | Prochaine étape |

Noms supposés qui n'existent pas dans ce paquet : `irpp`, `prime_activite`.

Deux définitions du coût employeur existent : `salaire_super_brut` (court terme, allègements déduits) et `cout_du_travail` (long terme, avec les crédits différés). La spécification définit le coût total employeur comme le brut plus les cotisations patronales, moins les allègements : c'est `salaire_super_brut`. Les deux sont égales sur les cas testés.

## Paramètres

| Paramètre | Contenu | Source citée par OpenFisca |
|-----------|---------|----------------------------|
| `marche_travail.salaire_minimum.smic.smic_b_horaire` | SMIC horaire brut | Décrets et arrêtés de revalorisation (Légifrance), dans les métadonnées du paramètre |
| `marche_travail.salaire_minimum.smic.nb_heures_travail_mensuel` | Heures mensuelles à temps plein | Métadonnées du paramètre |
| `prelevements_sociaux.reductions_cotisations_sociales.allegement_general.ensemble_des_entreprises.smic_reference` | SMIC horaire retenu pour la réduction générale 2026 | Article D241-7 du code de la sécurité sociale ; décret n° 2026-509 du 12 juin 2026 ; décret n° 2025-1228 du 17 décembre 2025 |
| `prelevements_sociaux.cotisations_regime_assurance_chomage.ags.employeur.ags` | Taux AGS employeur | Métadonnées du paramètre ; dernière vérification notée par OpenFisca : 14 mars 2024. Corrigé par le projet (0,25 % au 1er juillet 2024) |
