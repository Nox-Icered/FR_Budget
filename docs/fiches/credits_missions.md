---
levier: credits_missions
statut: beta
mise_a_jour: 2026-10-09
---

# Fiche : crédits par mission du budget de l'État

Lot 2.5 du plan (phase 2). Décisions du mainteneur du 9 octobre 2026, options (a) :
- périmètre hors pensions, dotations aux collectivités et contribution à l'Union européenne ; borne de ±20 % et exclusion des régimes sociaux et de retraite confirmées ;
- crédits de personnel gardés dans les missions ;
- 1 € de crédit compte pour 1 € de solde ;
- base : le PLF 2026.

## 1. Question posée

Que change pour le solde et la dette une variation de x % des crédits de paiement d'une mission du budget général ? Exemple de réglage : « baisse de 10 % des crédits de la mission Justice ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Variation des crédits d'une mission (28 missions, 321,3 Md€ au total) | 0 % | de -20 à +20 %, par pas de 1 | `db_budget_vert_plf2026` |

La borne de ±20 % est un choix du lot, sans source, confirmé par le mainteneur. Une même mission ne peut être réglée deux fois (`verifier_double_compte`).

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/credits_missions.py`, leviers dans `moteur/src/fr_budget/scenario.py`).
- **Extraction** : `pipelines/credits_missions/extraire.py` somme par programme :
  - les crédits budgétaires du budget vert du PLF 2026 (exécution 2024, LFI 2025, PLF 2026) ;
  - les crédits votés et les dépenses constatées de l'annexe 1 des PLRG 2023 à 2025.
- **Périmètre** : programmes du budget général, c'est-à-dire ceux de l'annexe 1 des PLRG. En sont exclues :
  - la mission « Relations avec les collectivités territoriales », qui relève du futur levier des dotations ;
  - les « Crédits non répartis » : c'est une provision répartie en cours d'année entre les autres missions, et leur exécution vaut zéro par construction ;
  - la mission « Régimes sociaux et de retraite » (subventions aux régimes spéciaux), qui relève du futur levier de l'indexation des pensions.

  Le budget vert ne contient ni la charge de la dette, ni les remboursements et dégrèvements. Les pensions de l'État, les prélèvements sur recettes, les budgets annexes et les comptes spéciaux ne font pas partie du budget général.
- **Convention** : les crédits de personnel du budget vert excluent les cotisations versées au compte d'affectation spéciale « Pensions », qui sont un flux interne à l'État.
- **Effet** d'une variation de x % : -x % des crédits du PLF 2026, ramené en euros de 2025 par la croissance nominale 2026 du RESF 2027, rapporté au PIB 2025 et tenu constant en points de PIB (`scenario_rendement_constant_pib`). Exemple : +1 % des crédits de la Défense dégrade le solde de 0,56 Md€ (fourchette 0,48 à 0,60).
- **Site** : les missions réglées deviennent deux mesures sur le levier générique `credits_missions` (hausse de 1 Md€ de 2025), l'une pour la somme des hausses, l'autre pour la somme des baisses. Ainsi, la fourchette reste celle du moteur (test `api/tests/test_api_credits_missions.py`). L'API refuse ce levier générique : elle demande les missions par leur identifiant.

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `db_budget_vert_plf2026_csv` | crédits de paiement par action, PLF 2026 (assiette du levier) | PLF 2026 |
| `dgfip_plrg_2023_annexe1_etat_cp_csv`, `dgfip_plrg_2024_…`, `dgfip_plrg_2025_…` | crédits votés en LFI et dépenses constatées par programme | exercices 2023 à 2025 |

Le budget vert du PLF 2027 n'est pas encore publié : il faudra l'intégrer dès sa parution.

## 5. Hypothèses

| Hypothèse (`registres/hypotheses.yaml`) | Valeur centrale | Plage | Effet sur le résultat |
|-----------------------------------------|-----------------|-------|-----------------------|
| `credits_missions_ecart_execution` | 0 | -0,147 à +0,090 | effet d'une variation des crédits |

La plage reprend les 10e et 90e centiles de l'écart entre dépenses constatées et crédits votés, par mission, sur 2023-2025 (86 observations). Les tests unitaires la recalculent à partir des données.

## 6. Validation

La validation compare l'assiette que le modèle aurait retenue avec la loi de finances initiale (crédits votés) aux dépenses constatées de la même année, sur l'ensemble des missions du levier.

- Tolérance : ±10 % (règle de publication, `CLAUDE.md`).
- Test : `moteur/tests/validation/test_levier_credits_missions.py`.
- Les références (`credits_missions_depenses_constatees_*`, à relire) sont des sommes calculées par le moteur sur les fichiers officiels. Un test vérifie que la valeur saisie égale la somme recalculée.

| Exercice | Dépenses constatées (PLRG) | Crédits votés en LFI (modèle) | Écart | Dans la tolérance |
|----------|----------------------------|-------------------------------|-------|-------------------|
| 2023 | 377,7 Md€ | 375,3 Md€ | -0,6 % | oui |
| 2024 | 371,9 Md€ | 372,2 Md€ | +0,1 % | oui |
| 2025 | 375,1 Md€ | 369,0 Md€ | -1,6 % | oui |

Ces montants suivent la convention des PLRG, cotisations au compte « Pensions » comprises : ils sont plus élevés que l'assiette du budget vert. Les écarts par mission sont plus grands (par exemple « Investir pour la France de 2030 » : -37 % en 2025) ; ils fondent la plage.

**Source indépendante : manquante.** Le rapport de la Cour des comptes « Le budget de l'État en 2025 (résultats et gestion) » est à déposer, car le site de la Cour est inaccessible depuis l'environnement. Statut « bêta, non validé ».

## 7. Limites connues

- Un euro de crédit compte pour un euro de solde des administrations publiques. C'est faux quand le crédit finance un autre organisme public (opérateur, université, Sécurité sociale, collectivité) qui garde sa dépense.
- Les crédits de personnel restent dans chaque mission : ce levier recoupera le futur levier « rémunérations publiques ». La combinaison des deux sera refusée.
- Aucun effet sur la croissance ni sur les recettes (multiplicateur désactivé).
- La comptabilité budgétaire (crédits de paiement) n'est pas la comptabilité nationale : décalages de calendrier, opérations financières.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-09 | Création du levier : extraction du budget vert 2026 et des PLRG 2023 à 2025 | 3 nouvelles références de validation, toutes dans la tolérance |
| 2026-10-09 | Exclusion de « Régimes sociaux et de retraite » (décision du mainteneur) | références : 383,6 → 377,7, 378,0 → 371,9, 381,2 → 375,1 Md€ ; écarts inchangés au dixième (-0,6 %, +0,1 %, -1,6 %) ; plage -0,145/+0,076 → -0,147/+0,090 |
