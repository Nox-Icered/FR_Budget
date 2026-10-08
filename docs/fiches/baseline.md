---
module: baseline
statut: non_publie
mise_a_jour: 2026-10-08
---

# Fiche : baseline des administrations publiques, 2025-2046

Lot 1.3 du plan (phase 1). Trajectoire de référence de la dette et du solde primaire, sans réforme, sur laquelle s'appliquent les effets des leviers.

## 1. Question posée

Sans changement de politique, comment évolueraient le solde primaire et la dette publique, en points de PIB, de 2025 à 2046 ?

## 2. Ce que l'utilisateur règle

Rien pour l'instant. Les hypothèses ci-dessous sont affichées avec leur plage.

## 3. Méthode

Deux segments raccordés en 2030 (décision du mainteneur du 8 octobre 2026, option B) :

- **2025-2030 : RESF du PLF 2027**, repris tel que publié (tableaux 4, 13, 14 et 21 et fiche 7). La charge d'intérêts n'est publiée que jusqu'en 2027 ; pour 2028-2030, elle est déduite du tableau 21 (ajustement structurel primaire moins ajustement structurel).
- **2031-2046 : projection** par la formule `d(t+1) = d(t) * (1 + r) / (1 + g) - pb + sfa` (fiche `dynamique_dette`) :

| Entrée | Valeur | Source |
|---|---|---|
| Croissance en volume | croissance potentielle | Ageing Report 2024, onglet FRa |
| Prix (déflateur du PIB) | IPCH, 2 % par an | Ageing Report 2024, onglet FRa ; la fiche France précise que le déflateur suit l'IPC à partir de 2027 |
| Taux de marché | taux d'intérêt nominal (3,6 % en 2031, 3,9 % en 2046) | Ageing Report 2024, onglet FRa |
| Taux apparent | refinancement progressif à partir du taux apparent 2030 du RESF (3,0 %) | hypothèse `baseline_part_refinancee` |
| Solde primaire | méthode (a) : solde primaire 2030 du RESF (1,3 point de PIB), moins la variation du coût du vieillissement depuis 2030 | Ageing Report 2024, onglet FRc ; décision du mainteneur du 8 octobre 2026 |
| Ajustement stock-flux | 0 | hypothèse `baseline_ajustement_stock_flux` |

## 4. Données

- `plf2027_resf` : `pipelines/baseline/extraire_resf.py` → `data/processed/baseline/resf_2027.csv`.
- `ce_ageing_report_2024` : `pipelines/baseline/extraire_ageing_report.py` → `data/processed/baseline/ageing_report_2024_fr.csv`.

## 5. Hypothèses et choix

- `baseline_part_refinancee`, `baseline_ajustement_stock_flux`, `baseline_cout_vieillissement_variantes` (registre des hypothèses).
- L'écart de production de 2030 (-0,5 % du PIB potentiel selon le RESF) est tenu constant : la croissance effective suit la croissance potentielle de l'Ageing Report.
- Fourchette : chaque hypothèse varie seule dans sa plage ; les bornes sont les extrêmes.

## 6. Validation

`moteur/tests/validation/test_baseline_resf.py` : avec les seules entrées publiées par le RESF, la formule redonne la dette de 2026 et 2027 à 0,35 point près (arrondis des sources).

## 7. Limites

- **Raccord en 2030.** L'Ageing Report (2023) prévoit une croissance potentielle de 0,6 % en 2030 et 2031, le RESF de 1,0 % en 2030. Le taux de marché de l'Ageing Report (3,5 % en 2030) est inférieur au taux à 10 ans prévu par le RESF pour 2027 (4,3 %).
- **Pas de fourchette sur la croissance ni sur le taux de marché** à ce stade : l'Ageing Report ne publie pas la croissance du PIB de ses variantes. Décision attendue du mainteneur.
- La part refinancée est celle de l'État, appliquée à toute la dette publique.
- Le coût du vieillissement de l'Ageing Report intègre la réforme des retraites de 2023 ; les mesures postérieures ne sont pas prises en compte.
- Le RESF 2025-2030 est une prévision du Gouvernement qui intègre ses mesures de redressement : ce n'est pas une trajectoire à politique inchangée.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-08 | Baseline RESF 2027 et Ageing Report 2024, méthode (a) | 2 tests de validation et 11 tests unitaires créés |
