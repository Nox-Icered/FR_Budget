---
levier: remunerations_publiques
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : rémunérations publiques (point d'indice, effectifs)

Lot 2.7 du plan (phase 2). Décisions du mainteneur du 12 octobre 2026, options (a) pour tout et bornes de ±5 % :
- coût calculé à partir de la masse salariale ;
- effet net des retours aux administrations publiques, avec l'effet brut affiché à côté ;
- un curseur pour les effectifs ;
- combinaison avec les crédits des missions refusée.

## 1. Question posée

Que changent pour le solde et la dette une hausse (ou une baisse) de x % de la valeur du point d'indice des trois fonctions publiques, ou de x % de leurs effectifs ? Exemple : « hausse de 1 % du point d'indice ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Valeur du point d'indice | gelée depuis juillet 2023 | de -5 à +5 %, par pas de 0,5 | décret n° 2023-519 |
| Effectifs des trois fonctions publiques | masse de 317,6 Md€ en 2025 (D1 - D122) | de -5 à +5 %, par pas de 0,5 | `insee_comptes_nationaux_2025` |

La borne de ±5 % vaut pour les deux curseurs ; elle a été confirmée par le mainteneur pour les effectifs le 12 octobre 2026. Ces curseurs ne peuvent pas être combinés avec les crédits des missions, qui contiennent les rémunérations de l'État : le moteur refuse la combinaison, et le site bloque l'un quand l'autre est réglé.

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/remunerations.py`, leviers dans `scenario.py`).
- **Assiette par versant.** C'est la rémunération des salariés (D1) moins les cotisations sociales imputées (D122) du sous-secteur correspondant, en 2025 (comptes de l'INSEE ; `pipelines/apu/extraire_comptes_apu.py` reprend désormais ces deux lignes). La correspondance est la suivante :
  - fonction publique de l'État ↔ administration centrale (S1311) ;
  - territoriale ↔ administrations locales (S1313) ;
  - hospitalière ↔ sécurité sociale (S1314).

  Les cotisations imputées sont surtout la contribution de l'État au compte des pensions, un flux interne à l'État.
- **Coût brut d'un point de 1 %** : 1 % × assiette × part du traitement indiciaire dans le salaire brut des fonctionnaires. Cette part vient de la DGAFP (rapport annuel 2025, figure 9) : 75,3 % dans la FPE, 74,7 % dans la FPT, 76,5 % dans la FPH. On obtient 2,40 Md€ pour 2025.
- **Coût net pour les administrations publiques.** Les cotisations patronales et salariales, la CSG, la CRDS et l'impôt sur le revenu reviennent aux administrations publiques. Seule la hausse du revenu après impôt des agents est une dépense nette.
  - La part qui reste à l'agent est calculée avec OpenFisca (législation 2025) pour un fonctionnaire célibataire sans enfant, avec le traitement et les primes moyens de la DGAFP.
  - Pour l'État, la contribution au compte des pensions est retirée du coût, comme dans l'assiette.
  - Valeur centrale : ensemble des fonctionnaires ; fourchette : catégories A, B et C.
  - Résultat : 1,06 Md€ (1,01 à 1,20) pour 1 % de point.
- **Effectifs** : 1 % × assiette, soit 3,18 Md€ brut. Le net se calcule de la même façon, sur l'agent entier (traitement et primes) : 1,90 Md€ (1,84 à 1,96).
- **Effet dans le scénario** : coût net, en Md€ de 2025, rapporté au PIB 2025 et tenu constant en points de PIB. L'effet brut est exporté (`effet_brut_unitaire`) et affiché à part.

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `insee_cna2025_t_3202`, `insee_cna2025_t_3205`, `insee_cna2025_t_3212` | rémunération des salariés et cotisations imputées par sous-secteur | comptes 2025 |
| `dgafp_rapport_annuel_2025_pdf` | traitement brut et primes moyens des fonctionnaires, par versant et catégorie | données 2023 |
| `senat_avis_plf2024_fonction_publique_pdf` | coûts officiels des hausses du point de 2022 et 2023 (validation) | 2023 |

Les 24 valeurs de la figure 9 et les 8 coûts du Sénat sont saisis dans `registres/references/chiffrages.yaml`, à relire.

## 5. Hypothèses et choix

- **Correspondance entre versants et sous-secteurs.** C'est une approximation : S1311 inclut les opérateurs de l'État, et S1314 le personnel des caisses de sécurité sociale, qui n'est pas payé au point.
- **Part indiciaire.** Celle des fonctionnaires est appliquée à toute la masse, contractuels compris.
- **Agent type** : célibataire sans enfant. Sa situation familiale change l'impôt, donc la part nette ; la fourchette par catégorie n'en tient pas compte.

## 6. Validation

Références : Sénat, avis n° 134 (2023-2024), tableau page 8, à partir des réponses du Gouvernement au questionnaire budgétaire. Le modèle applique chaque hausse à la masse de sa première année pleine.

| Mesure | Versant | Référence | Modèle | Écart | Dans la tolérance |
|--------|---------|-----------|--------|-------|-------------------|
| +3,5 % (coût 2023) | total | 7,60 Md€ | 7,61 Md€ | +0,1 % | oui |
| | FPE | 3,60 | 3,19 | -11,4 % | non |
| | FPT | 2,40 | 2,31 | -3,8 % | oui |
| | FPH | 1,60 | 2,11 | +31,8 % | non |
| +1,5 % (coût 2024) | total | 3,20 Md€ | 3,48 Md€ | +8,6 % | oui |
| | FPE | 1,50 | 1,49 | -1,0 % | oui |
| | FPT | 0,90 | 1,04 | +15,8 % | non |
| | FPH | 0,71 | 0,95 | +33,6 % | non |

Les totaux passent, sur deux millésimes, mais quatre comparaisons par versant sont hors tolérance.
- **FPH** : le modèle surestime. Le sous-secteur S1314 contient aussi le personnel des caisses de sécurité sociale et les médecins hospitaliers, qui ne sont pas rémunérés au point.
- **FPE 2022** : le modèle sous-estime. La référence de 3,6 Md€ est en outre peu cohérente avec celle de 1,5 Md€ pour une hausse de 1,5 %.

Sources indépendantes (`docs/validation/confrontations_independantes.md`) : Cour des comptes, « La situation et les perspectives des finances publiques », juin 2017, hausse de 1 % du point : 2,07 Md€ (modèle 2017 : 1,88, −9,2 %), dont État 0,88 (−9,0 %), territoriale 0,64 (−9,6 %), hôpitaux 0,55 (−9,3 %) ; Fipeco, juillet 2026, 2,5 Md€ hors cotisations des employeurs (modèle 2025 : 2,37, −5,1 %). Toutes dans la tolérance. Le levier reste en bêta (comparaisons par versant aux références officielles hors tolérance).

## 7. Limites connues

- L'effet net ne compte que les prélèvements sur la hausse de salaire. Il ignore l'effet sur la consommation, la TVA et les pensions futures des agents.
- Une baisse des effectifs ne compte ni les allocations chômage éventuelles ni la perte de services rendus.
- Un changement du point ne modifie pas les primes indexées sur le traitement, comme l'indemnité de résidence : elles ne sont pas dans la part indiciaire.
- Les montants de 2025 sont tenus constants en part du PIB.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-14 | Confrontation à la Cour des comptes (2017) et à Fipeco (2026) sur le point d'indice, `docs/validation/confrontations_independantes.md` | 5 nouvelles références indépendantes, dans la tolérance (de −9,6 % à −5,1 %) |
| 2026-10-12 | Création du levier ; extraction de D1 et D122 ajoutée aux comptes des APU (indicateurs existants inchangés) | 8 nouvelles références de validation, 4 dans la tolérance (dont les 2 totaux) ; tableau : 34 sur 46 |
