---
levier: impot_revenu_structure
statut: beta
mise_a_jour: 2026-11-05
---

# Fiche : moteur de barème de l'impôt sur le revenu

Lot V2 « impôt sur le revenu (structure) », deuxième étape. Plan validé par le mainteneur le 5 novembre 2026, puis option A (décote explicite, correction du haut de la répartition). Cette première PR livre le moteur et sa validation ; l'éditeur de barème du site et l'effet sur les ménages types suivront. Les choix du § 5 et les valeurs saisies sont **à relire**.

## 1. Question posée

Combien rapporte ou coûte un autre barème de l'impôt sur le revenu : autre nombre de tranches, autres seuils, autres taux, autre décote ? Exemple : « taux de la tranche à 30 % porté à 32 % ».

## 2. Ce que l'utilisateur réglera (PR suivante)

Un barème de 1 à 8 tranches (seuils et taux libres) et la décote, à partir du barème des revenus de 2025 lu dans OpenFisca (`bareme_ir_depuis_1945.bareme`, `plaf_qf.decote`).

## 3. Méthode de calcul

- Moteur : agrégé, sans micro-données (`moteur/src/fr_budget/agrege/bareme_ir.py`).
- **Répartition des foyers** par revenu fiscal de référence (RFR) par part, pour chaque année de revenus : déciles publiés par la DGFiP (`pipelines/impot_revenu/extraire_deciles_dgfip.py`).
  - Dixièmes 1 à 9 : répartition uniforme entre les bornes.
  - Dernier dixième : trois segments (hors dernier centième, dernier centième hors millième, dernier millième), chacun selon une loi de Pareto qui redonne le RFR moyen par part publié pour 2024. Pour une autre année, les bornes du haut suivent la borne du dernier dixième.
  - Parts par foyer : moyenne de chaque dixième en 2024.
- **Correction du haut** : le RFR des foyers les plus aisés comprend des revenus imposés hors barème. Au-dessus de la borne du dernier dixième, le quotient est ramené à `borne x (q / borne) ** gamma`. gamma est choisi pour que le nombre de foyers au-dessus du seuil de la tranche à 45 % redonne celui de la DGFiP en 2024 (`ir_foyers_tranche_45_2024`).
- **Impôt d'un foyer** : parts x barème du quotient, moins la décote (formule d'avant 2014 ou d'après selon l'année) et la réduction sous condition de revenus de 2016 à 2019, pour un célibataire et pour un couple. La part des couples vient de la DGFiP par quantile de revenu (`ir_couples_*_2022`).
- **Calage (2024 seulement)** : pour chaque segment, rapport entre l'impôt au barème publié et l'impôt modélisé. Il absorbe ce que le modèle ne représente pas (écart entre RFR et revenu imposable, plafonnement du quotient familial, cas particuliers). Les dixièmes 1 à 4, où le barème et la décote ne laissent rien, ne sont pas calés.
- **Effet d'une réforme** : écart d'impôt entre le nouveau barème et le barème de référence, avec le calage de chaque segment.
- **Fourchette** : valeur centrale (calage par segment, part des couples par quantile) ; autres bouts : calage unique pour tous les segments, et part des couples uniforme (32 %).

## 4. Données

| Jeu de données | Ce qu'il apporte |
|----------------|------------------|
| `dgfip_ir_deciles_rfr_part_xlsx` | bornes et impôt moyen par décile de RFR par part, 2003-2024 ; pour 2024, parts, RFR et impôt au barème moyens par part, dernier centième et millième |
| `dgfip_ir_taux_marginal_xlsx` | foyers et impôt par taux marginal, 2019-2024 (correction du haut, contrôle) |
| `dgfip_analyses_08_2025_pdf` | part des foyers mariés ou pacsés par quantile de revenu, 2022 (tableau 3, page 5) |
| `plf2013_projet_loi_pdf`, `plf2015_projet_loi_pdf`, `plf2020_projet_loi_pdf`, `plf2025_evaluations_prealables_pdf` | chiffrages des réformes passées (§ 6) |

## 5. Choix à relire

1. **RFR par part comme quotient familial**, corrigé en haut de la répartition et absorbé par le calage ailleurs.
2. **Calage sur la seule année 2024**, supposé valable pour les autres années (validation hors échantillon).
3. **Part des couples** : quantiles de revenu de la DGFiP appliqués au rang des déciles de RFR par part. Les deux classements diffèrent : la variante uniforme (32 %) borne la fourchette.
4. **Parts par foyer** et forme du haut de la répartition de 2024 supposées stables.
5. **Non modélisés** : plafonnement du quotient familial (levier séparé), réductions et crédits d'impôt, contribution exceptionnelle sur les hauts revenus, changements de comportement.

## 6. Validation

Test : `moteur/tests/validation/test_levier_bareme_ir.py`. Tolérance : ±10 %. Chaque réforme est recalculée avec le barème, la décote et la répartition de son année.

| Référence | Millésime | Référence | Modèle | Écart | Dans la tolérance |
|-----------|-----------|----------:|-------:|------:|-------------------|
| Création de la tranche à 45 % | PLF 2013 (revenus 2012) | 0,30 Md€ | 0,26 Md€ | -12,5 % | non |
| Suppression de la tranche à 5,5 %, décote renforcée | PLF 2015 (revenus 2014) | 3,19 Md€ | 2,06 Md€ | -35,4 % | non |
| Taux de 14 % à 11 %, décote atténuée, seuils revus, fin de la réduction de 20 % | PLF 2020 (revenus 2020) | 5,00 Md€ | 5,06 Md€ | +1,2 % | oui |
| Absence d'indexation de 2 % (seuils et décote) | PLF 2025 (revenus 2024) | 3,70 Md€ | 2,59 Md€ | -30,1 % | non |

Lecture :
- Le chiffrage de 2020 est arrondi (« environ 5 milliards »).
- L'indexation officielle porte aussi sur les plafonds du quotient familial et d'autres seuils, que le moteur ne fait pas varier : une part de l'écart en vient.
- Sources indépendantes déjà au registre pour l'indexation (`docs/fiches/impot_revenu.md`) : IPP environ 1,1 Md€ pour un point, OFCE environ 1,2 Md€ pour 1,1 point ; le moteur donne 1,30 Md€ pour un point, entre ces estimations et le chiffrage officiel (1,85 Md€).
- Contrôle de la répartition (2024, foyers par taux marginal) : 6,84 M de foyers modélisés à 30 % contre 6,87 M publiés ; 0,35 M à 41 % contre 0,43 M (-20 %) ; tranche à 45 % calée.
- Le moteur reste en **bêta** : une référence sur quatre dans la tolérance.

## 7. Limites connues

- Sans comportement : un taux très élevé réduirait la base imposable.
- Le plafond du quotient familial n'est pas recalculé quand le barème change.
- Les barèmes très éloignés des réformes chiffrées (taux au-delà de 60 %, plus de 8 tranches) seront signalés par un avertissement sur le site.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-11-05 | Décote, réduction sous condition de revenus, part des couples et correction du haut (option A) | 45 % : +30,5 → -12,5 % ; 2015 : -82,8 → -35,4 % ; 2020 : +9,0 → +1,2 % ; indexation : -48,7 → -30,1 % |
| 2026-11-05 | Création du moteur | 4 nouvelles références de validation |
