---
module: deciles
statut: beta
mise_a_jour: 2026-11-06
---

# Fiche : effet des mesures par dixième de niveau de vie

Lot V2 « agrégats par décile issus de publications officielles ». Plan validé par le responsable du projet le 6 novembre 2026. Statut : **bêta, non validé**. Les deux confrontations du § 6 sont hors tolérance, dont l'une très largement pour l'impôt sur le revenu.

## 1. Question posée

Pour un scénario du simulateur, comment l'effet des mesures sur le revenu disponible se répartit-il entre les dixièmes de niveau de vie ? Le résultat est donné en euros par unité de consommation et par an, et en part du revenu disponible.

## 2. Données

- **Comptes nationaux distribués 2023 de l'Insee**, base 2020 (tableau CND.101, vingtièmes de niveau de vie usuel, 2020 à 2023, Md€).
  - Fichier brut : `data/raw/deciles/insee_cnd_2023_T_CND_101.xlsx`.
  - Pipeline : `pipelines/deciles/extraire_cnd.py`, qui regroupe les vingtièmes deux à deux et vérifie leur somme avec la colonne « Ensemble ».
  - Sortie : `data/processed/deciles/cnd_deciles.csv`.
- **Budget de famille 2017** (déjà au dépôt, `fr_budget.menages.depense`) : variante pour la TVA et les accises.

## 3. Méthode

Code : `moteur/src/fr_budget/menages/deciles.py`. Site : `web/lib/deciles.ts`, avec un export `deciles.json` qui redonne le calcul du moteur (test `api/tests/test_api_deciles.py`).

L'effet national d'une unité du levier (rendement en Md€ de 2025, année pleine) est réparti selon la part de chaque décile dans l'assiette. La variation du revenu vaut moins l'effet sur le solde public.

| Leviers | Clé (lignes des comptes distribués) | Variante |
|---|---|---|
| TVA, accises | taxes sur les produits | Budget de famille 2017 |
| CSG activité | salaires nets + revenus mixtes | CSG totale |
| CSG retraites | pensions de retraite | CSG totale |
| CSG capital | revenus nets de la propriété | CSG totale |
| IR : seuils, barème, quotient familial, dépenses fiscales de l'IR | impôt sur le revenu | — |
| IS : taux normal, surtaxe | impôt sur les sociétés (convention de l'Insee) | — |
| Taux de cotisation patronale, allègements | cotisations sociales (quatre lignes) | — |
| Contribution chômage | cotisations chômage | — |
| Indexation | pensions + invalidité + famille + exclusion sociale | — |
| Prime d'activité | exclusion sociale | — |
| Revalorisation et durée de l'assurance chômage | allocations chômage | — |
| Termes croisés (combinaison sans double compte) | clé du levier de CSG de la paire | — |

**Non répartis**, signalés sur le site :
- rémunérations publiques ;
- dotations ;
- crédits des missions ;
- dépenses fiscales hors IR ;
- âge de départ.

**Fourchette**, décile par décile : extrêmes du produit des bornes de l'effet national par les parts des années 2020 à 2023 et de chaque variante. La valeur centrale prend l'effet central et la part de 2023 de la clé centrale. Avec plusieurs mesures, on additionne les valeurs centrales, les bornes basses et les bornes hautes.

**Unités** :
- euros par unité de consommation (UC), l'effet en euros de 2025 étant divisé par les UC de 2023 ;
- part du revenu disponible net de 2023, porté en 2025 par le PIB nominal.

## 4. Hypothèses et limites

- La structure de 2023 est appliquée aux années suivantes, sans changement de comportement.
- **La part dans l'assiette n'est juste que pour un changement proportionnel de tout le prélèvement.** Une mesure ciblée (une tranche du barème, le plafond du quotient familial, une prestation particulière) ne touche pas les ménages au prorata de ce qu'ils paient ou reçoivent : voir le § 6.
- La CSG retraites ne vise que le taux plein, alors que la clé prend toutes les pensions.
- La ligne « exclusion sociale » inclut le RSA, plus concentré en bas que la prime d'activité.
- La source publie un impôt sur le revenu de −2,7 Md€ pour le premier décile (ménages à faible niveau de vie et à revenus du patrimoine élevés) ; la valeur est reprise telle quelle.
- Les dixièmes des comptes distribués comptent le même nombre de personnes, ceux du Budget de famille le même nombre de ménages.

## 5. Choix à relire

- Le tableau des clés et des variantes (§ 3).
- Les leviers non répartis.
- La tolérance de validation : au plus 10 points de part sur chaque dixième. La règle de publication ne fixe de tolérance que pour le rendement.

## 6. Validation

Forme de la répartition (part de chaque dixième dans l'effet total) comparée aux évaluations de réformes de l'Insee (modèle Ines, France, portrait social). Test : `moteur/tests/validation/test_deciles_insee.py`.

| Réforme (référence) | Clé | Écart maximal | Dernier dixième (modèle / Insee) |
|---|---|---|---|
| Réforme de la prime d'activité de 2018 (FPS 2019, dossier 3, figure 7) | exclusion sociale | 10,7 points | 1,2 % / 1,0 % |
| Baisse de l'IR de 2020, première tranche de 14 % à 11 % (FPS 2022, dossier 2, figure 4) | impôt sur le revenu | 50,7 points | 64,3 % / 13,7 % |

Les deux sont hors tolérance. Pour la prime d'activité, la forme est proche mais le premier dixième est trop chargé (29,6 % contre 20,2 %). Pour l'impôt sur le revenu, la clé ne convient pas à une mesure ciblée sur une tranche.
