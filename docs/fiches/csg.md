---
levier: csg
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : CSG (taux sur l'activité, les retraites et le capital)

Lot 2.9 du plan (phase 2). Le mainteneur a autorisé le 12 octobre 2026 l'avancée en autonomie : « arrête-toi uniquement si une source n'est pas accessible ; sinon avance et indique les choix et leurs limites ». Les choix ci-dessous sont donc ceux recommandés, **à relire** (§ 5).

## 1. Question posée

Que changent pour le solde et la dette une hausse (ou une baisse) de x points du taux de CSG sur les revenus d'activité, sur les pensions de retraite au taux plein, ou sur les revenus du capital ? Exemple : « hausse de 1 point de la CSG sur les revenus d'activité ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Taux sur les revenus d'activité | 9,2 % | de -2 à +2 points, par pas de 0,1 | CCSS octobre 2026, tableau 4 |
| Taux plein sur les pensions de retraite | 8,3 % (les taux médian de 6,6 % et réduit de 3,8 % ne bougent pas) | de -2 à +2 points | idem |
| Taux sur les revenus du capital | 9,2 % en 2025, 10,6 % pour la plupart de ces revenus depuis 2026 | de -2 à +2 points | idem |

Repère pour les bornes : la hausse de 1,7 point de la LFSS 2018.

## 3. Méthode de calcul

- Moteur : agrégé, avec OpenFisca pour la part du taux plein (`moteur/src/fr_budget/agrege/csg.py`, leviers dans `scenario.py`).
- **Rendement d'un point.** C'est le rendement constaté en 2025, tous affectataires, divisé par le taux de 2025 :
  - activité : 110 670 M€ / 9,2 = **12,03 Md€** (fourchette de 11,60 à 12,03) ;
  - capital : 17 590 M€ / 9,2 = **1,91 Md€** (de 1,72 à 1,95) ;
  - retraites au taux plein : 25 439 M€ × part prélevée au taux plein / 8,3 = **2,10 Md€** (de 1,78 à 2,49).
- **Part du taux plein sur les retraites.** Elle est calculée avec OpenFisca pour chaque tranche de 100 € de la distribution des pensions de l'EIR 2020 (DREES), avec la législation de 2020, l'année des pensions. Elle vaut 58,3 % pour une personne seule et 78,8 % pour un couple de retraités à la même pension. La valeur centrale est à mi-chemin.
- **Fourchette** :
  - rendements de 2024 (constatés) et de 2027 (prévus), rapportés au PIB de leur année, puis au PIB de 2025 ;
  - pour les retraites, en plus, la part du taux plein d'une personne seule ou d'un couple.

  La borne basse de l'activité vient de 2027 : la réforme de l'assiette des travailleurs indépendants réduit la CSG d'activité à partir de 2026 (CCSS 2026, page 54).
- **Effet dans le scénario.** Rendement en Md€ de 2025, rapporté au PIB 2025 et tenu constant en points de PIB.

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `ccss_octobre_2026_pdf` | rendements de la CSG par assiette (2024, 2025, 2027), dont la CSG sur les retraites ; taux par assiette | octobre 2026 |
| `ccss_septembre_2018_pdf` | rendements et taux de 2017 ; supplément de rendement de la hausse de 1,7 point de 2018, par assiette | septembre 2018 |
| `senat_rapport_plfss2026_tome1_pdf` | rendement du passage de 9,2 % à 10,6 % de la CSG sur le capital | 15 novembre 2025 |
| `drees_eir2020_distribution_pensions_xlsx` | distribution des pensions (part du taux plein) | fin 2020 |

Les 30 valeurs saisies dans `registres/references/chiffrages.yaml` sont à relire.

## 5. Choix faits en autonomie, et leurs limites

1. **Trois curseurs : activité, retraites au taux plein, capital.** Les revenus de remplacement autres que les pensions (chômage, indemnités journalières) et les jeux sont hors du levier.
   - Limite : une hausse uniforme sur tous les revenus de remplacement n'est pas proposée.
2. **Retraites : seul le taux plein bouge**, comme lors de la hausse de 2018.
   - Limite : une hausse des taux médian et réduit n'est pas modélisable avec ce curseur.
3. **Rendement brut.** La part déductible de la CSG réduit l'impôt sur le revenu ; cet effet n'est pas déduit, comme dans les chiffrages de la CCSS.
   - Limite : l'effet net pour les administrations publiques est surestimé de la baisse d'impôt induite. Elle n'est pas chiffrée ici ; elle relèverait d'un calcul OpenFisca sur des ménages types.
4. **Aucun comportement** : les revenus du capital ne réagissent pas au taux. La CCSS et le Sénat chiffrent aussi sans comportement.
5. **Capital : taux de 2025 (9,2 %).** Depuis 2026, la plupart des revenus du capital sont à 10,6 %. Une hausse d'un point s'applique à toute l'assiette.
   - Limite : un taux de 2027 pris à 10,6 % pour toute l'assiette donne la borne basse.
6. **Part du taux plein avec les pensions et la législation de 2020.** Ce choix évite de réindexer les pensions de l'EIR sans source sur les revalorisations de 2021 à 2023.
   - Limite : les seuils de 2025 et les pensions de 2025 ne sont pas exactement dans le même rapport qu'en 2020.
7. **Bornes de ±2 points** : choix sans source autre que le repère de 2018.
8. **Pas de blocage croisé.** La combinaison avec l'indexation ou avec les rémunérations publiques reste permise : les retours de CSG de ces leviers sont calculés au taux actuel, et l'interaction est négligée.

## 6. Validation

Le modèle applique la hausse à l'assiette de l'année précédente (rendement divisé par le taux), portée à l'année de la mesure par la croissance du PIB nominal. Test : `moteur/tests/validation/test_levier_csg.py`. Tolérance : ±10 %.

| Mesure | Millésime | Référence | Modèle | Écart | Dans la tolérance |
|--------|-----------|----------:|-------:|------:|-------------------|
| +1,7 point, revenus d'activité | CCSS 2018 (LFSS 2018) | 16 052 M€ | 16 031 M€ | -0,1 % | oui |
| +1,7 point, retraites au taux plein | CCSS 2018 | 4 181 M€ | 4 328 M€ | +3,5 % | oui |
| +1,7 point, revenus du capital | CCSS 2018 | 2,10 Md€ | 2,31 Md€ | **+10,2 %** | non |
| +1,4 point, revenus du capital | Sénat, PLFSS 2026 | 2,80 Md€ | 2,73 Md€ | -2,5 % | oui |
| CSG sur les retraites au taux plein en 2017 (contrôle de la part calculée) | CCSS 2018 | 15 780 M€ | 16 349 M€ | +3,6 % | oui |

Lecture :
- Deux millésimes (2018 et 2026) sont couverts pour le capital ; un seul pour l'activité et les retraites.
- Pour le capital en 2018, une explication possible, non vérifiée : une partie des revenus du patrimoine de 2017 a été taxée en 2018 à l'ancien taux.
- La CCSS d'octobre 2026 chiffre à 1,2 Md€ l'effet en 2026 de la hausse finalement votée. Cette hausse est limitée à « la plupart » des revenus du capital (contribution financière pour l'autonomie de 1,4 %), et le chiffrage porte sur le seul champ des régimes de base. Il n'est pas comparable et n'est pas retenu.

Aucune source indépendante n'est confrontée (Cour des comptes, IPP, OFCE). Le levier reste en bêta.

## 7. Limites connues

- Le rendement de l'activité dépend de la masse salariale de 2025 ; la réforme de l'assiette des indépendants n'est prise en compte que dans la borne basse.
- Aucune interaction avec les allègements de cotisations, la prime d'activité ou les prestations sous condition de ressources.
- Les retraites au taux plein comprennent les pensions complémentaires, car la CSG porte sur la pension totale.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-12 | Création du levier | 5 nouvelles références de validation, 4 dans la tolérance ; tableau : 40 sur 55 (avec le lot 2.8) |
