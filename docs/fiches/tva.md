---
levier: tva
statut: non_publie
mise_a_jour: 2026-10-08
---

# Fiche : TVA

Fiche en préparation. Méthode retenue le 7 octobre 2026 : modèle de TVA théorique de la DG Trésor appliqué aux données publiques de l'INSEE, validé contre le point de TVA publié par la DG Trésor et contre la recette totale de Voies et Moyens. Premiers résultats et écarts : [`docs/validation/levier_tva.md`](../validation/levier_tva.md).

## 1. Question posée

Combien rapporte ou coûte aux administrations publiques une variation d'un taux de TVA, la première année et en année pleine ? Exemple de réglage : « hausse de 1 point du taux normal de TVA ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Source de la valeur actuelle |
|-----------|-----------------|------------------------------|
| Taux normal | à relever | législation (OpenFisca-France ou code général des impôts) |
| Taux intermédiaire | à relever | idem |
| Taux réduit | à relever | idem |
| Taux super-réduit | à relever | idem |

Les taux particuliers (Corse, outre-mer) ne sont pas réglables en V1. Leur effet sur la recette est retranché à partir du tome II de Voies et Moyens (§ 5 et 7).

## 3. Méthode de calcul (proposée, à valider)

Rendement statique, sans changement de comportement :

> variation de recette = variation du taux × assiette taxée à ce taux

L'assiette est hors taxe, au même taux, pour l'année de référence.

Deux choix de méthode sont à trancher. Je présente les deux options sans en retenir une.

**A. Périmètre de l'assiette**

| Option | Contenu | Avantage | Inconvénient |
|--------|---------|----------|--------------|
| A1 | Consommation des ménages par produit (comptes nationaux), affectée au taux applicable | Données publiques détaillées ; lien direct avec l'indicateur de pouvoir d'achat | Oublie la TVA non déductible payée par les administrations, les entreprises exonérées et sur le logement neuf |
| A2 | Assiette totale déduite des recettes de TVA par taux | Couvre toute la TVA collectée | Dépend de la publication des recettes par taux |

La comparaison des deux options avec le chiffrage officiel fera partie du rapport de validation.

**B. Première année et année pleine**

La TVA est encaissée avec un décalage. Une hausse au 1er janvier rapporte donc moins la première année qu'en année pleine. Le coefficient de montée en charge sera une hypothèse du registre, avec sa source. Je n'ai aucune valeur sourcée à ce stade.

## 4. Données à réunir

| Donnée | Source visée | Usage |
|--------|--------------|-------|
| Taux de TVA en vigueur et historiques | OpenFisca-France ; code général des impôts | Paramètres |
| Consommation des ménages par produit | INSEE, comptes nationaux | Assiette (option A1) |
| Correspondance produit → taux de TVA | Code général des impôts ; travaux publiés (IPP, Cour des comptes) | Assiette (option A1) |
| Recettes de TVA, par taux si publié | Voies et Moyens (PLF) ; comptes publics (DGFiP) | Assiette (option A2) et contrôle |

## 5. Hypothèses

Dans `registres/hypotheses.yaml` :

- `tva_repartition_produits_mixtes_stable` : la répartition des travaux entre 10 % et 5,5 %, calculée sur 2023 à partir du tome II de Voies et Moyens (PLF 2025), vaut pour les autres années ;
- `tva_ecart_territorial_stable` : l'écart dû aux taux d'outre-mer et de Corse (2 297 M€ en 2023) est retranché de la recette de chaque année.

Leurs plages serviront au calcul des fourchettes. Restent à créer, une fois sourcées : coefficient de première année ; fourchette d'incertitude sur le reste de l'assiette.

## 6. Validation

- Constat : l'annexe Voies et Moyens ne chiffre pas le rendement d'une variation de taux ; elle donne la recette totale.
- Références retenues (`registres/references/chiffrages.yaml`) : point de TVA brut et net 2025 (DG Trésor, Trésor-Éco n° 371), point de TVA 2015 (DG Trésor, Cahier 2016-02), recette totale 2022 (DG Trésor) et 2024 (PLF 2026, Voies et Moyens tome I).
- Tolérance : ±10 % sur le rendement à 1 an, sur au moins deux millésimes.
- Source indépendante visée : IPP (TAXIPP), Cour des comptes ou Commission européenne.
- Test : à écrire avant le code, dans `moteur/tests/validation/`.

## 7. Limites connues

- Rendement statique : aucune réaction des prix ni des quantités consommées.
- Taux particuliers (Corse, outre-mer) non modélisés en V1 : leur effet global sur la recette est retranché (tome II de Voies et Moyens), mais pas leur effet sur le point de TVA.
- Médicaments tous au taux de 2,1 %, restauration toute au taux de 10 % : voir `docs/validation/levier_tva.md`.
- L'effet sur le pouvoir d'achat (indicateur séparé de la spécification) demande les budgets de famille de l'INSEE.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-07 | Fiche créée : méthode proposée, données à réunir | aucun |
| 2026-10-07 | Premier modèle (`agrege/tva.py`) | 17 tests de validation créés : 8 réussis, 9 échoués |
| 2026-10-08 | Travaux répartis entre 10 % et 5,5 % et écart d'outre-mer et de Corse retranché de la recette (tome II de Voies et Moyens, PLF 2025) ; répartition de la restauration essayée et écartée | 2 tests passent (point brut 2015 au taux de 5,5 % : -11,5 % → -9,0 % ; recette 2024 : +10,2 % → +9,0 %) ; 10 réussis, 7 échoués ; détail dans `docs/validation/levier_tva.md` |
| 2026-10-08 | Séparation des médicaments non remboursables (comptes de la santé de la DREES) essayée et non retenue ; diagnostic publié dans `docs/validation/levier_tva.md` | aucun (modèle inchangé) |
