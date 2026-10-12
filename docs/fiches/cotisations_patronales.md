---
levier: cotisations_patronales
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : cotisations patronales (taux du secteur privé, allègements généraux)

Lot 2.10 du plan (phase 2). Ce lot a été fait en autonomie (instruction du mainteneur du 12 octobre 2026). Les choix du § 5 sont **à relire**.

## 1. Question posée

Que changent pour le solde et la dette :
- une hausse (ou une baisse) de x points du taux de cotisation patronale sur les salaires du secteur privé ?
- une variation de x % des allègements généraux de cotisations ?

Exemple : « baisse de 10 % des allègements généraux ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source |
|-----------|-----------------|----------------------------|--------|
| Taux de cotisation patronale déplafonnée du secteur privé | un point vaut 7 590 M€ en 2026 | de -2 à +2 points, par pas de 0,1 | CCSS octobre 2026, encadré 2, page 51 |
| Allègements généraux (salariés, tous attributaires) | 75,6 Md€ en 2025 | de -20 à +20 %, par pas de 1 | CCSS octobre 2026, fiche 1.6, tableau 2, page 67 |

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/cotisations.py`, leviers dans `scenario.py`).
- **Taux.** Le rendement d'un point est la « valeur de point de cotisation déplafonnée » du secteur privé publiée par la CCSS pour 2026, ramenée en euros de 2025 par la croissance du PIB nominal : **7,44 Md€**. Borne basse : la valeur publiée pour 2025, 7,38 Md€.
- **Allègements.** Le coût retenu est celui des allègements généraux et des mesures de modulation des taux en 2025 (77 554 M€), moins les réductions de taux des travailleurs non salariés (811 et 1 100 M€), soit 75,6 Md€. Une hausse de 1 % coûte donc **0,76 Md€**. Bornes : coûts de 2024 (constaté) et de 2027 (prévu, après le gel du barème de la RGDU), tenus constants en part du PIB : de 0,68 à 0,79 Md€.
- **Effet dans le scénario.** Montant en Md€ de 2025, rapporté au PIB 2025 et tenu constant en points de PIB.

## 4. Données

| Jeu de données | Ce qu'il apporte |
|----------------|------------------|
| `ccss_octobre_2026_pdf` | valeur de point 2026 ; coût des allègements 2024, 2025 et 2027 |
| `ccss_octobre_2025_pdf` | valeur de point 2025 ; coût prévu des allègements pour 2025 |
| `ccss_octobre_2024_pdf` | coût prévu des allègements pour 2024 |
| `ccss_septembre_2018_pdf` | valeur de point 2017 |

Les 14 valeurs saisies dans `registres/references/chiffrages.yaml` sont à relire.

## 5. Choix faits en autonomie, et leurs limites

1. **Secteur privé seulement.** Les cotisations des employeurs publics sont payées et reçues par les administrations publiques : elles ne changent pas leur solde.
   - Limite : la hausse du taux CNRACL, par exemple, n'est pas modélisable ici. Elle relève des dépenses des collectivités et des hôpitaux.
2. **Hausse de taux hors du champ des allègements.** La valeur de point de la CCSS suppose compensée la hausse des exonérations qu'entraîne la hausse de taux. Pour les administrations publiques, la reprendre revient à supposer la hausse hors du champ de la réduction générale, comme une contribution nouvelle.
   - Limite : si la hausse portait sur une cotisation couverte par la réduction générale, une partie serait annulée sur les bas salaires. Le rendement serait plus faible, d'un montant non chiffré.
3. **Allègements en pourcentage du coût.** Une variation uniforme de x % ne correspond à aucun barème précis (point de sortie, coefficient maximal).
   - Limite : une réforme réelle du barème a des effets différents selon les salaires. Le gel du barème de la RGDU (2,8 Md€ en 2026, 5,6 Md€ en 2027 selon la CCSS) n'est pas reproductible avec ce curseur.
4. **Rendements bruts.** L'effet sur l'impôt sur les sociétés (charges déductibles), sur l'emploi et sur les salaires n'est pas compté, comme dans les chiffrages de la CCSS.
5. **Bornes** : ±2 points (comme la CSG) et ±20 % (comme les crédits des missions). Aucune source ne les fixe.
6. **Pas de blocage croisé** entre les deux curseurs. Combiner une hausse de taux et une baisse des allègements compte les deux effets séparément ; leur interaction est négligée.

## 6. Validation

Test : `moteur/tests/validation/test_levier_cotisations.py`. Tolérance : ±10 %.

| Référence | Millésime | Référence | Modèle | Écart | Dans la tolérance |
|-----------|-----------|----------:|-------:|------:|-------------------|
| Valeur d'un point, secteur privé, 2025 | CCSS 2025 | 7 380 M€ | 7 441 M€ | +0,8 % | oui |
| Valeur d'un point, secteur privé, 2017 | CCSS 2018 | 5 570 M€ | 5 701 M€ | +2,4 % | oui |
| Coût prévu des allègements généraux, 2024 | CCSS 2024 | 78,7 Md€ | 77,6 Md€ (constaté) | -1,4 % | oui |
| Coût prévu des allègements généraux, 2025 | CCSS 2025 | 74,5 Md€ | 75,6 Md€ (constaté) | +1,5 % | oui |

Lecture :
- Pour le taux, la validation vérifie que la valeur de point, tenue en part du PIB, reproduit les valeurs publiées d'autres années.
- Pour les allègements, elle compare le coût prévu au coût constaté, comme pour les dotations.
- Aucune ne valide l'hypothèse 2 (hausse hors allègements) ni l'absence d'effet sur l'impôt sur les sociétés.
- Aucune source indépendante n'est confrontée. Le levier reste en bêta.

## 7. Limites connues

- Les valeurs de point de la CCSS portent sur les régimes de base. Une hausse affectée à l'Agirc-Arrco ou à l'Unédic aurait une assiette différente (plafonnement).
- Aucun effet sur les ménages types ni sur les entreprises par taille : ces moteurs viendront avec les modules « ménages » et « entreprises ».

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-12 | Création du levier | 4 nouvelles références de validation, toutes dans la tolérance ; tableau : 48 sur 63 (avec les lots 2.8 et 2.9) |
