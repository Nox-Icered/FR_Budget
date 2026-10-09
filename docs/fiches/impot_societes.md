---
levier: impot_societes
statut: beta
mise_a_jour: 2026-10-09
---

# Fiche : impôt sur les sociétés

Lot 2.3 du plan (phase 2). Deux leviers (décision du mainteneur du 9 octobre 2026, option (c)) ; effet compté en entier l'année d'entrée en vigueur (option (i)).

## 1. Question posée

Que rapporte une hausse (ou une baisse) de x points du taux normal de l'impôt sur les sociétés, ou une surtaxe de x % de l'impôt dû par les entreprises au chiffre d'affaires d'au moins 1 Md€, et quel est l'effet sur le solde et la dette ?

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Taux normal | 25 % en 2025 | de -10 à +10 points (la baisse s'arrête au taux réduit de 15 %) | `openfisca_france_176_1_2` |
| Surtaxe sur l'IS des grandes entreprises | en plus des contributions votées | de 0 à 41,2 % (`is_taux_contribution_exceptionnelle_haute`) | `plf2025_evaluations_prealables` |

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/impot_societes.py`).
- IS brut = taux normal * bénéfice imposable à 25 % + taux réduit * bénéfice imposable à 15 % (`is_brut`).
- Un point de taux normal : 1 % du bénéfice imposable au taux normal, soit 2,57 Md€ sur les bénéfices 2025 (`rendement_point_taux_normal`).
- Un point de surtaxe : 1 % de l'assiette de la contribution exceptionnelle sur les bénéfices des grandes entreprises (IS dû par les sociétés au chiffre d'affaires d'au moins 1 Md€), soit 0,20 Md€ en 2025 (`assiette_surtaxe`).
- Scénario : rendement rapporté au PIB de 2025 et tenu constant en points de PIB (`scenario_rendement_constant_pib`).

## 4. Données

| Jeu de données | Ce qu'il apporte | Millésime |
|----------------|------------------|-----------|
| `dgfip_stat_51_is_2025_xlsx` | bénéfice imposable par taux, assiette de la contribution exceptionnelle, 2022-2025 | septembre 2026 |
| `dgfip_stat_39_is_2024_xlsx` | IS brut 2024 | septembre 2025 |
| `plf2025_evaluations_prealables_pdf` | taux et rendement de la contribution exceptionnelle | PLF 2025 |

## 5. Hypothèses

Aucune hypothèse propre au levier pour l'instant : les bases sont publiées par la DGFiP. Les fourchettes de l'effet sont donc réduites à une valeur (voir limites).

## 6. Validation

| Référence | Millésime | Valeur de référence | Valeur du modèle | Écart | Dans la tolérance |
|-----------|-----------|---------------------|------------------|-------|-------------------|
| IS brut, DGFiP Statistiques n° 39 | 2024 | 69,05 Md€ | 67,94 Md€ | -1,6 % | oui |
| IS brut, DGFiP Statistiques n° 51 | 2025 | 70,47 Md€ | 68,79 Md€ | -2,4 % | oui |

Test : `moteur/tests/validation/test_levier_impot_societes.py`. **Cette validation n'est pas indépendante** : la base et l'IS brut viennent des mêmes notes ; elle contrôle la cohérence des taux et de la base. L'écart restant correspond aux taux particuliers (plus-values, redevances), absents de la base publiée.

**Surtaxe** : le rendement de la contribution exceptionnelle (8 Md€ selon l'évaluation préalable du PLF 2025, 7,5 Md€ réalisés en 2025 selon FIPECO) est compris entre 20,6 % et 41,2 % de l'assiette publiée (20,4 Md€), comme attendu ; la répartition entre les deux tranches n'est pas publiée, ce qui empêche une validation plus fine.

**Aucun chiffrage officiel récent d'un point de taux normal** n'a été trouvé : le levier reste en bêta.

## 7. Limites connues

- Effet compté en entier l'année d'entrée en vigueur ; en réalité acomptes dans l'année et solde l'année suivante.
- Aucun effet de comportement (localisation des bénéfices, investissement).
- Réductions et crédits d'impôt inchangés ; les taux particuliers (plus-values, redevances) ne sont pas modulés.
- Le bénéfice de 2025 est tenu constant en part du PIB, alors qu'il varie fortement d'une année à l'autre (-4,9 % en 2024, +3,2 % en 2025).
- Pas de fourchette : aucune plage sourcée n'est encore saisie pour la base.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-09 | IS brut reconstitué, leviers « taux normal » et « surtaxe sur les grandes entreprises » | 2 tests de validation (réussis, -1,6 % et -2,4 %), 5 tests unitaires de l'IS, 1 test unitaire du scénario ; test de cohérence du tableau des écarts étendu |
