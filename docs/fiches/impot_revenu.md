---
levier: impot_revenu
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : impôt sur le revenu (revalorisation des seuils du barème)

Lot 2.11 du plan (phase 2). Ce lot a été fait en autonomie (instruction du mainteneur du 12 octobre 2026). Les choix du § 5 sont **à relire**.

## 1. Question posée

Que changent pour le solde et la dette des seuils du barème de l'impôt sur le revenu relevés de x % de plus (ou de moins) que l'inflation ? Exemple : « gel du barème », soit environ -1 % quand l'inflation est de 1 %.

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source |
|-----------|-----------------|----------------------------|--------|
| Revalorisation des limites des tranches du barème et des seuils associés (décote, plafonds du quotient familial), par rapport à l'inflation | 0 (indexation sur l'inflation) | de -3 à +3 %, par pas de 0,1 | évaluation préalable de l'article 2 du PLF 2025 (définition du champ) |

Repères : le gel de 2026 proposé par le PLF 2026 (-1,0 %) ; l'indexation de 4,8 % de la LFI 2024.

## 3. Méthode de calcul

- Moteur : agrégé, barème d'OpenFisca (`moteur/src/fr_budget/agrege/impot_revenu.py`, levier dans `scenario.py`).
- **Valeur centrale.** La sensibilité vient de l'évaluation préalable de l'article 2 du PLF 2025 : l'absence d'indexation de 2 % aurait majoré l'impôt d'environ 3,7 Md€ en 2025, soit 1,85 Md€ pour 1 % (revenus de 2024). C'est déjà un rendement de 2025 (avis d'imposition et prélèvement à la source) : **1,85 Md€**, sans conversion (correction après la revue de la PR).
- **Borne basse.** Elle vient d'un calcul structurel à partir de DGFiP Statistiques n° 41, tableau 2, revenus 2024, qui donne l'impôt au barème et le RFR par part par décile, avec le dernier dixième découpé en centième et millième.
  - Pour un foyer dont le quotient q est dans la tranche k, relever les seuils de i réduit l'impôt d'une part de i × (q × t_k − τ(q)), où τ(q) est l'impôt d'une part.
  - Ce rapport est appliqué à l'impôt au barème de chaque segment, avec le RFR par part moyen comme quotient. Le barème des revenus de 2024 vient d'OpenFisca (seuils de 11 497, 29 315, 83 823 et 180 294 €).
  - Résultat : **1,09 Md€** pour 1 %. Ce calcul ignore la décote, les plafonds du quotient familial et l'entrée de foyers dans l'impôt au sein d'un décile : il sous-estime l'effet de 42 % par rapport à la sensibilité officielle.
- **Effet dans le scénario** : un relèvement de 1 % de plus coûte de 1,09 à 1,85 Md€. Le montant est rapporté au PIB 2025 et tenu constant en points de PIB.

## 4. Données

| Jeu de données | Ce qu'il apporte |
|----------------|------------------|
| `plf2025_evaluations_prealables_pdf` (lot de l'IS) | sensibilité de 3,7 Md€ pour 2 %, page 18 ; taux de 2 %, page 15 |
| `dgfip_statistiques_41_xlsx` et `_pdf` | impôt au barème et RFR par part par décile, revenus 2024 |
| `senat_rapport_general_plf2026_tome1_pdf` | gel du barème de 2026 : +1,9 Md€ (pages 149 et 150) |
| `plfss2026_projet_loi_pdf` (lot de l'indexation) | inflation hors tabac prévue pour 2025 : 1,0 % |

Les 34 valeurs saisies dans `registres/references/chiffrages.yaml` sont à relire.

## 5. Choix faits en autonomie, et leurs limites

1. **Un seul curseur, sur les seuils.** Les taux, la décote seule et le plafond du quotient familial ne sont pas proposés séparément : aucun chiffrage officiel récent ne permettrait de les valider.
2. **Valeur centrale calée sur un chiffrage officiel.** Elle reprend la sensibilité du PLF 2025 plutôt que le calcul structurel, qui sous-estime de 42 %. Ce chiffrage officiel sert donc de calage, pas de validation : il reste une seule référence hors calage (§ 6).
3. **Linéarité.** Un écart de x % rapporte x fois l'effet d'1 %. Un relèvement important ferait sortir plus de foyers de l'impôt que ne le dit cette règle.
4. **Calendrier.** L'effet est compté en année pleine dès l'année d'entrée, comme dans le chiffrage du PLF 2025, qui additionne l'avis d'imposition et le prélèvement à la source.
5. **Seuils non fiscaux.** De nombreux seuils (CSG des retraités, impôts locaux) suivent le barème : leur effet n'est pas compté.
6. **Inflation de 2025.** La prévision de 1,0 % est celle du PLFSS 2026, préparé avec le même jeu d'hypothèses que le PLF 2026.

## 6. Validation

Test : `moteur/tests/validation/test_levier_impot_revenu.py`. Tolérance : ±10 %.

| Référence | Millésime | Référence | Modèle | Écart | Dans la tolérance |
|-----------|-----------|----------:|-------:|------:|-------------------|
| Gel du barème de 2026 (1,0 %) | PLF 2026 (rapport général du Sénat) | 1,90 Md€ | 1,89 Md€ | -0,7 % | oui |

Lecture :
- Le chiffrage du PLF 2025 sert au calage ; il n'est pas compté en validation.
- Le PLF 2024 (indexation de 4,8 %) donnerait un deuxième millésime hors calage, mais son évaluation préalable n'a pas été trouvée sur les sites accessibles (Assemblée nationale : adresse introuvable ; budget.gouv : bloqué). **À déposer** pour compléter la validation.
- Comparaison structurelle : le calcul par décile donne 1,09 Md€ pour 1 %, contre 1,85 Md€ dans le chiffrage officiel. L'écart (-41 %) est publié ici et tient aux limites du § 3.
- Sources indépendantes (`docs/validation/confrontations_independantes.md`) : gel du barème de 2026, IPP 1,1 Md€ pour une inflation de 1 % et 1,4 Md€ pour 1,3 %, OFCE 1,2 Md€ pour 1,1 %. Le modèle, qui reprend le chiffrage officiel, est au-dessus de 71,5 %, 75,2 % et 73,0 %. Le calcul par décile du § 3 (1,09 Md€ pour 1 %) est, lui, proche de l'IPP et de l'OFCE : l'écart porte sur le chiffrage officiel plutôt que sur la méthode. Le levier reste en bêta ; le choix entre le chiffrage officiel et le calcul par décile revient au mainteneur.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-14 | Confrontation à l'IPP et à l'OFCE (gel du barème 2026), `docs/validation/confrontations_independantes.md` | 3 nouvelles références indépendantes, hors tolérance (+71,5 %, +75,2 %, +73,0 %) |
| 2026-10-12 | Revue de la PR : le chiffrage du PLF 2025, déjà en euros de 2025, n'est plus converti une seconde fois | gel de 2026 : -0,8 % → -0,7 % |
| 2026-10-12 | Création du levier | 1 nouvelle référence de validation, dans la tolérance ; tableau : 49 sur 64 |
