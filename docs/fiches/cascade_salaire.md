---
module: cascade_salaire
statut: en_cours
mise_a_jour: 2026-10-07
---

# Fiche : cascade du salaire d'un ménage type

Module transversal : il sert aux leviers qui touchent les salaires (cotisations, CSG, impôt sur le revenu, prime d'activité). Fiche rédigée sur le modèle `_modele.md`.

## 1. Question posée

Pour un ménage type, combien coûte le salaire à l'employeur, et combien en reste-t-il au salarié avant et après impôt ? Avant et après une réforme, ligne par ligne.

## 2. Ce que l'utilisateur règle

Rien sur cette fiche : le salaire brut et les hypothèses d'emploi sont ceux du ménage type. Les réglages viendront des leviers.

| Hypothèse d'emploi | Valeur pour le cas de validation | Source |
|--------------------|----------------------------------|--------|
| Effectif de l'entreprise | valeur par défaut du modèle Urssaf | `modele_social_11_1_0` |
| Taux de la cotisation AT/MP | taux moyen du modèle Urssaf | `modele_social_11_1_0` |
| Mutuelle d'entreprise (montant, part employeur) | valeur par défaut du modèle Urssaf, ou aucune | `modele_social_11_1_0` |

Les valeurs exactes sont dans `registres/references/menages/urssaf_modele_social.json`, relues dans le modèle Urssaf par script.

## 3. Méthode de calcul

- Moteur : OpenFisca-France 176.1.2, utilisé comme bibliothèque, avec les corrections de `registres/corrections_openfisca.yaml`.
- Fonction : `cascade_salaire_mensuelle` (`moteur/src/fr_budget/menages/openfisca.py`).
- Lignes calculées pour un mois :

| Ligne | Variable OpenFisca |
|-------|--------------------|
| Coût total employeur | `salaire_super_brut` |
| Salaire brut | `salaire_de_base` |
| Net avant impôt | `salaire_net_a_payer` |
| Net imposable | `salaire_imposable` |

- Pas encore calculé : net après impôt (impôt sur le revenu, prime d'activité). Voir « Limites ».

## 4. Données

Aucun jeu de données : la législation vient d'OpenFisca (`openfisca_france_176_1_2`).

## 5. Hypothèses

Aucune hypothèse au sens du registre (pas de plage) : les hypothèses d'emploi décrivent le cas type, elles ne portent pas d'incertitude.

L'incidence des cotisations patronales (part répercutée sur le salaire) sera une hypothèse avec plage, à sourcer avant d'afficher la seconde lecture prévue par la spécification.

## 6. Validation

- Référence : modèle de calcul de mon-entreprise.urssaf.fr (`modele_social_11_1_0`), exécuté par `outils/references_urssaf/generer.mjs`.
- Tolérance : 0,50 € par mois et par ligne (validée le 7 octobre 2026).
- Test : `moteur/tests/validation/test_menage_type_urssaf.py`.
- Résultat au 7 octobre 2026 : 12 comparaisons sur 12 dans la tolérance (célibataire au SMIC, janvier et juillet 2026, avec et sans mutuelle). Détail et écarts trouvés : `docs/validation/menage_type_smic.md`.
- Source indépendante : à faire (simulateurs officiels d'impots.gouv.fr et de la CAF pour le net après impôt).

## 7. Limites connues

- Un seul ménage type validé (célibataire au SMIC). Les autres profils de la spécification demandent une source pour le salaire médian.
- Net après impôt pas encore calculé ni validé.
- Les sources des corrections d'OpenFisca sont citées d'après des résultats de recherche et restent à confirmer sur les textes primaires.
- Convention d'heures du SMIC mensuel (OpenFisca et modèle Urssaf diffèrent de 0,04 €) : à choisir pour nos ménages types.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-07 | Première version : cascade sur 4 lignes, comparaison avec le modèle Urssaf | 12 tests de validation créés : 8 réussis avant corrections, 12 après |
| 2026-10-07 | Corrections AGS et mutuelle ; référence de juillet alignée sur le décret n° 2026-509 | 4 tests passés d'échec à réussite |
