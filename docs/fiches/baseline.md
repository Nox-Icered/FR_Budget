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

- **2025-2030 : RESF du PLF 2027**, repris tel que publié (tableaux 4, 13, 14 et 21 et fiche 7). La charge d'intérêts n'est publiée que jusqu'en 2027 ; pour 2028-2030, elle est déduite du tableau 21 (ajustement structurel primaire moins ajustement structurel). Le taux apparent de 2026-2030 est la charge d'intérêts rapportée à la dette de l'année précédente, en euros : les deux étant publiées en % du PIB de leur année, le rapport est multiplié par (1 + croissance nominale). Il redonne le taux publié pour 2026 et 2027 (2,29 % et 2,50 %, contre 2,3 et 2,5 %).
- **2031-2046 : projection** par la formule `d(t+1) = d(t) * (1 + r) / (1 + g) - pb + sfa` (fiche `dynamique_dette`) :

| Entrée | Valeur | Source |
|---|---|---|
| Croissance en volume | croissance potentielle | Ageing Report 2024, onglet FRa |
| Prix (déflateur du PIB) | IPCH, 2 % par an | Ageing Report 2024, onglet FRa ; la fiche France précise que le déflateur suit l'IPC à partir de 2027 |
| Taux de marché | taux d'intérêt nominal (3,6 % en 2031, 3,9 % en 2046) | Ageing Report 2024, onglet FRa |
| Taux apparent | refinancement progressif à partir du taux apparent 2030 reconstitué du RESF (3,1 % : charge d'intérêts de 2030 rapportée à la dette de 2029, en euros) | hypothèse `baseline_part_refinancee` |
| Solde primaire | méthode (a) : solde primaire 2030 du RESF (1,3 point de PIB), moins la variation du coût du vieillissement depuis 2030 | Ageing Report 2024, onglet FRc ; décision du mainteneur du 8 octobre 2026 |
| Ajustement stock-flux | 0 | hypothèse `baseline_ajustement_stock_flux` |

## 4. Données

- `plf2027_resf` : `pipelines/baseline/extraire_resf.py` → `data/processed/baseline/resf_2027.csv`.
- `ce_ageing_report_2024` : `pipelines/baseline/extraire_ageing_report.py` → `data/processed/baseline/ageing_report_2024_fr.csv`.

## 5. Hypothèses et choix

- `baseline_part_refinancee`, `baseline_ajustement_stock_flux`, `baseline_cout_vieillissement_variantes`, `baseline_croissance_volume`, `baseline_taux_marche` (registre des hypothèses).
- Variantes de croissance et de taux (décision du mainteneur du 9 octobre 2026, options (i)) : croissance en volume maintenue à 1,0 % (croissance potentielle 2030 du RESF) ; taux de marché maintenu à 4,3 % (taux à 10 ans 2027 du RESF).
- L'écart de production de 2030 (-0,5 % du PIB potentiel selon le RESF) est tenu constant : la croissance effective suit la croissance potentielle de l'Ageing Report.
- Fourchette : chaque hypothèse varie seule dans sa plage ; les bornes sont les extrêmes.

## 6. Validation

`moteur/tests/validation/test_baseline_resf.py` : avec les seules entrées publiées par le RESF, la formule redonne la dette de 2026 et 2027 à 0,35 point près (arrondis des sources).

## 7. Limites

- **Raccord en 2030.** L'Ageing Report (2023) prévoit une croissance potentielle de 0,6 % en 2030 et 2031, le RESF de 1,0 % en 2030. Le taux de marché de l'Ageing Report (3,5 % en 2030) est inférieur au taux à 10 ans prévu par le RESF pour 2027 (4,3 %).
- **Croissance et taux : une seule variante chacun, à la hausse.** L'Ageing Report ne publie pas la croissance du PIB de ses variantes ; la variante de croissance (1,0 % maintenu) relève la croissance jusqu'en 2036 puis l'abaisse, l'Ageing Report dépassant 1,0 % à partir de 2037. Aucune variante de taux plus bas que l'Ageing Report.
- Les variantes jouent une à une ; leur combinaison n'est pas calculée.
- La part refinancée est celle de l'État, appliquée à toute la dette publique.
- Le coût du vieillissement de l'Ageing Report intègre la réforme des retraites de 2023 ; les mesures postérieures ne sont pas prises en compte.
- Le RESF 2025-2030 est une prévision du Gouvernement qui intègre ses mesures de redressement : ce n'est pas une trajectoire à politique inchangée.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-08 | Baseline RESF 2027 et Ageing Report 2024, méthode (a) | 2 tests de validation et 11 tests unitaires créés |
| 2026-10-09 | Variantes de croissance (1,0 %) et de taux (4,3 %) tirées du RESF | 3 tests unitaires créés ; dette 2046 : bas 103,6 %, central 108,3 %, haut 116,4 % (inchangés, la borne haute reste le scénario de risque santé et dépendance) ; 2031 : bas 119,7 % (contre 120,1 %) |
| 2026-10-28 | Revue de code : taux apparent 2026-2030 reconstitué en euros (le rapport des deux % du PIB est multiplié par 1 + g) ; taux de départ de la projection 3,035 → 3,121 % | dette 2046 centrale 108,25 → 108,67 % du PIB (bas 103,60 → 104,02 ; haut 116,45 → 116,87) ; 2 nouveaux tests de validation (taux apparent 2026 et 2027 contre le RESF), réussis ; aucun autre test ne bouge |
