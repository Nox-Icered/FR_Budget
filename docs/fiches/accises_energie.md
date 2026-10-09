---
levier: accises_energie
statut: beta
mise_a_jour: 2026-10-09
---

# Fiche : accises sur les carburants (gazole et essences)

Lot 2.2 du plan (phase 2). Première version : carburants routiers (décision du mainteneur du 9 octobre 2026, options (a)). Le gaz naturel et l'électricité feront un lot séparé.

## 1. Question posée

Que rapporte, par an, une hausse (ou une baisse) de x centimes par litre du tarif de l'accise sur le gazole, ou sur les essences SP95, SP95-E10 et SP98, et quel est l'effet sur le solde et la dette ?

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Tarif du gazole | 59,40 centimes par litre au 1er janvier 2025 | de -14 à +14 centimes | `openfisca_france_176_1_2` |
| Tarif des essences | 66,29 centimes par litre pour le SP95-E10 au 1er janvier 2025 | de -14 à +14 centimes | `openfisca_france_176_1_2` |

Bornes : la baisse du gazole s'arrête au tarif réduit du transport routier de marchandises (45,19 centimes, `accises_tarif_trm_2025`) ; au-delà, le remboursement des transporteurs changerait de sens. La hausse et le levier des essences reprennent la même amplitude (choix à valider par le mainteneur).

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/accises.py`).
- **Recette brute** = somme sur les produits des ventes (tonnes, converties en hectolitres par la masse volumique) × tarif (€/hl ; €/100 kg pour le GPL et le fioul lourd). Fonction `recette_brute`.
- **Assiette du levier** (`assiette_levier`) : gazole routier, moins les volumes des transporteurs routiers, du transport collectif et des taxis, dont le tarif réduit est fixe (une hausse du tarif normal leur est remboursée) ; essences SP95, SP95-E10 et SP98 (le superéthanol E85 a son propre tarif). Volumes remboursés = dépense fiscale / (tarif normal - tarif réduit) (`volumes_rembourses`).
- **Rendement d'un centime par litre**, ventes 2025 : 0,225 Md€ pour le gazole, 0,148 Md€ pour les essences. Dans le scénario, ce rendement est rapporté au PIB de 2025 et tenu constant en points de PIB (`scenario_rendement_constant_pib`), comme pour la TVA.

## 4. Données

| Jeu de données | Ce qu'il apporte | Millésime |
|----------------|------------------|-----------|
| `sdes_conso_produits_petroliers_csv` | ventes mensuelles de produits pétroliers, métropole, en tonnes | 2017 à 2025 |
| `ministere_guide_fiscalite_energies_2026_pdf` | tarifs du gazole non routier et tarifs réduits | 2026 |
| `ministere_guide_fiscalite_energies_2025_pdf` | coefficients de conversion légaux (annexe 3) | 2025 |
| `ademe_base_carbone_pci_masse_volumique_htm` | masses volumiques | non daté |
| `plf2025_voies_et_moyens_tome2_pdf` | dépenses fiscales 800220, 800221, 800222 | PLF 2025 |

## 5. Hypothèses

| Hypothèse | Valeur centrale | Plage | Effet sur le résultat |
|-----------|-----------------|-------|-----------------------|
| `accises_masses_volumiques` | Base Carbone | ±1,6 % | recette 2024 de 30,7 à 31,7 Md€ ; rendement du centime ±2 % |
| `accises_gpl_part_carburant` | 0 | 0 à 1 | recette 2024 jusqu'à +0,2 Md€ |
| `accises_tarif_moyen_gnr_2024` | 24,81 €/hl | 18,82 à 24,81 | recette 2024 jusqu'à -0,3 Md€ |

## 6. Validation

| Référence | Millésime | Valeur de référence | Valeur du modèle | Écart | Dans la tolérance |
|-----------|-----------|---------------------|------------------|-------|-------------------|
| Recette brute totale ex-TICPE, tome I de Voies et Moyens (PLF 2025) | 2023 | 31,7 Md€ | 30,9 Md€ | -2,5 % | oui |
| Recette brute totale ex-TICPE, tome I de Voies et Moyens (PLF 2026) | 2024 | 31,6 Md€ | 31,2 Md€ | -1,2 % | oui |

Test : `moteur/tests/validation/test_levier_accises.py` (tolérance ±10 %).

**Source indépendante** : FIPECO, « Les taxes sur les carburants » : produit de la TICPE en comptabilité nationale de 30,2 Md€ en 2024 et 30,5 Md€ en 2025. Le modèle donne 31,2 Md€ (+3,4 %) et 31,1 Md€ (+2,1 %). La comptabilité nationale et la comptabilité budgétaire ne retiennent pas exactement le même périmètre : l'écart est publié, pas corrigé.

**Ce qui est validé** : la recette totale, donc le produit volumes × tarifs. Le rendement d'un centime n'a pas de chiffrage officiel récent ; l'assiette nette des remboursements repose sur les dépenses fiscales, non validées séparément.

## 7. Limites connues

- Pas d'effet de comportement : une hausse de prix réduit la consommation, ce qui n'est pas pris en compte (élasticités en V3).
- Une hausse de l'accise augmente aussi la TVA payée sur le carburant ; cet effet n'est pas compté.
- Majorations régionales (jusqu'au 1er août 2025) et Corse non modélisées.
- Volumes remboursés aux taxis : dépense fiscale totale (gazole et essence) traitée comme du gazole.
- Les volumes de 2025 ne reflètent pas la baisse de la consommation de 2026 décrite par le PLF 2027.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-09 | Recette brute ex-TICPE, assiette du levier, leviers gazole et essences dans le scénario | 2 tests de validation créés (réussis, -2,5 % et -1,2 %), 7 tests unitaires des accises, 2 tests unitaires du scénario ; test de cohérence du tableau des écarts étendu au nouveau fichier de validation |
