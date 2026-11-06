---
module: deciles
statut: beta
mise_a_jour: 2026-11-06
---

# Fiche : effet des mesures par dixième de niveau de vie

Lot V2 « agrégats par décile issus de publications officielles ». Plan validé par le responsable du projet le 6 novembre 2026. Statut : **bêta, non validé**. Pour l'impôt sur le revenu, le responsable du projet a retenu l'option C (§ 3 bis), qui ramène l'écart à l'Insee de 50,6 à 5,6 points. La prime d'activité reste hors tolérance (10,1 points).

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
| IR : seuils du barème, barème saisi | moteur du barème, voir § 3 bis | variantes du moteur du barème |
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
- dépenses fiscales, y compris celles de l'IR ;
- plafond du quotient familial ;
- âge de départ.

## 3 bis. Impôt sur le revenu : moteur du barème (option C)

Une clé au prorata de l'impôt payé ne vaut que pour un changement proportionnel de tout l'impôt. Sur la baisse de 2020, ciblée sur une tranche, elle donnait un écart de 50,6 points à l'Insee (64,3 % au dernier dixième contre 13,7 %).

- **Calcul par dixième fiscal** : le moteur du barème (`fr_budget.agrege.bareme_ir`, `ecart_par_dixieme`) calcule l'écart d'impôt par dixième de foyers, classés selon le revenu fiscal de référence par part (déciles de la DGFiP, haut de la répartition en loi de Pareto, calage sur l'impôt publié).
- **Hypothèse de correspondance** : le k-ième dixième fiscal est assimilé au k-ième dixième de niveau de vie. Les deux classements ne sont pas identiques : les foyers ne sont pas des ménages, les parts ne sont pas des unités de consommation et le revenu fiscal ne compte pas les prestations. Aucune source publiée ne donne le passage de l'un à l'autre ; l'hypothèse est éprouvée sur la baisse de 2020 (§ 6).
- **Revalorisation des seuils** : l'effet national (chiffrage du levier) est réparti selon les parts d'une revalorisation de 1 % du barème de 2025, seuils et décote. Les variantes du moteur (calage unique, part des couples uniforme) donnent la fourchette.
- **Barème saisi sur le site** : écart d'impôt par dixième de ce barème, calculé dans le navigateur (`web/lib/bareme-ir.ts`, `ecartParDixieme`) avec les mêmes segments que son effet total. Les bornes combinent les variantes du moteur et la plage de l'écart à la validation du levier générique.
- **Plafond du quotient familial et dépenses fiscales de l'IR** : non répartis. Le moteur du barème ne traite pas le plafonnement, et aucune source ne répartit les dépenses fiscales par niveau de vie.

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
- La correspondance entre dixièmes fiscaux et dixièmes de niveau de vie (§ 3 bis).
- Le plafond du quotient familial et les dépenses fiscales de l'IR non répartis.

## 6. Validation

Forme de la répartition comparée aux évaluations de réformes de l'Insee (modèle Ines, France, portrait social). L'Insee publie l'effet moyen sur le niveau de vie (euros par unité de consommation, moyenne sur les personnes) ; le montant du modèle par dixième est ramené en euros par unité de consommation (unités de consommation des comptes distribués de 2023), puis chaque profil est normalisé (part de chaque dixième dans la somme des dix moyennes). Approximation restante : l'Insee pondère les ménages par leur nombre de personnes, le modèle par leurs unités de consommation (relevé par la revue de code de la PR, 6 novembre 2026). Test : `moteur/tests/validation/test_deciles_insee.py`.

| Réforme (référence) | Clé | Écart maximal | Dernier dixième (modèle / Insee) |
|---|---|---|---|
| Réforme de la prime d'activité de 2018 (FPS 2019, dossier 3, figure 7) | exclusion sociale | 10,1 points | 1,2 % / 1,0 % |
| Baisse de l'IR de 2020, première tranche de 14 % à 11 % (FPS 2022, dossier 2, figure 4) | moteur du barème (§ 3 bis) | 5,6 points | 14,6 % / 13,7 % |

Avec la clé au prorata de l'impôt payé, l'écart était de 50,6 points (64,3 % / 13,7 %).

La prime d'activité est hors tolérance : la forme est proche, mais le premier dixième est trop chargé (29,6 % contre 20,2 %), car la ligne « exclusion sociale » inclut le RSA. Pour l'impôt sur le revenu, le moteur du barème concentre un peu plus la baisse sur les 7e et 8e dixièmes que l'Insee (24,4 % et 30,3 % contre 19,7 % et 24,8 %), et laisse à zéro les 3e et 4e (0,9 % et 1,7 % pour l'Insee). C'est l'effet attendu de la correspondance entre dixièmes fiscaux et dixièmes de niveau de vie.
