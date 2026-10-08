# Levier TVA : rendement d'un point de TVA, premier modèle

Tâches 0.4 et 0.5 du plan. Rapport du 7 octobre 2026, mis à jour le 8 octobre 2026 (répartition des produits mixtes et écart territorial). Statut du levier : **non publié** (bêta en développement).

## Méthode

Reprise de la méthode du modèle de TVA théorique de la DG Trésor (Cahier n° 2016-02, parties 2.1 à 2.3), appliquée aux seules données publiques de l'INSEE (comptes nationaux annuels base 2020). Code : `moteur/src/fr_budget/agrege/tva.py`.

1. Consommation finale des ménages, des APU (individuelle) et des ISBLSM au niveau le plus fin publié (304 produits pour les ménages), chaque produit rattaché à un régime de TVA dans `registres/tva/correspondance_produits.csv`.
2. Consommation collective des APU, consommations intermédiaires et investissement au niveau A38 du TES, régime par produit dans `registres/tva/regimes_a38.csv`.
3. Investissement diminué de la production pour emploi final propre (opération P12), qui n'est pas vendue et ne porte pas de TVA.
4. TVA non déductible des producteurs : prorata de non-déductibilité de chaque branche égal à la part exonérée ou hors champ de la consommation finale de son produit (Cahier 2016-02, § 2.2.3).
5. Produits relevant de plusieurs taux : les travaux de construction spécialisés sont répartis entre 10 % et 5,5 % à l'aide du coût des deux taux réduits publié dans le tome II de Voies et Moyens du PLF 2025 (dépenses fiscales 730213 et 730223, réalisation 2023). L'assiette d'un taux réduit est son coût divisé par l'écart au taux normal ; sa part dans la consommation de 2023 est appliquée aux autres années (hypothèse `tva_repartition_produits_mixtes_stable`). Registre : `registres/tva/depenses_fiscales.yaml`.
6. Recette : diminuée de l'écart dû aux taux d'outre-mer et de Corse (dépenses fiscales 710103, 710105 et 730306, 2 297 M€ en 2023), que le modèle ne calcule pas lui-même (hypothèse `tva_ecart_territorial_stable`). Le point de TVA n'est pas corrigé.
7. Point brut = 1 % de l'assiette hors taxe de chaque taux ; point net = point brut moins la part payée par les APU.
8. Vieillissement 2022 → 2025 par l'évolution des recettes de TVA, comme la DG Trésor (Trésor-Éco n° 371, note 5), avec les recettes budgétaires publiées : 202,7 Md€ en 2022 (DG Trésor) et 210,0 Md€ prévus pour 2025 (PLF 2026).

Taux de TVA : paramètres d'OpenFisca-France. Données : `pipelines/tva/` → `data/processed/tva/`.

## Résultats

| Référence | Taux | Modèle (Md€) | Référence (Md€) | Écart | Statut | Écart au 7 octobre |
|---|---|---|---|---|---|---|
| Point brut 2025 (DG Trésor, tableau 1) | Ensemble | 14,18 | 13,70 | +3,5 % | OK | +3,5 % |
|  | 2,1 % | 0,62 | 0,40 | +55,3 % | Échec | +55,3 % |
|  | 5,5 % | 2,01 | 2,40 | -16,2 % | Échec | -18,8 % |
|  | 10 % | 1,95 | 1,90 | +2,6 % | OK | +5,7 % |
|  | 20 % | 9,60 | 8,90 | +7,9 % | OK | +7,9 % |
| Point net 2025 (DG Trésor, tableau 2) | Ensemble | 11,60 | 11,40 | +1,7 % | OK | +1,7 % |
|  | 2,1 % | 0,22 | 0,40 | -44,7 % | Échec | -44,7 % |
|  | 5,5 % | 1,90 | 2,00 | -5,1 % | OK | -8,2 % |
|  | 10 % | 1,81 | 1,60 | +12,9 % | Échec | +16,7 % |
|  | 20 % | 7,67 | 7,50 | +2,2 % | OK | +2,2 % |
| Point brut 2015 (DG Trésor 2016, tableau 8) | Ensemble | 10,78 | 9,75 | +10,5 % | Échec | +10,5 % |
|  | 2,1 % | 0,48 | 0,50 | -3,2 % | OK | -3,3 % |
|  | 5,5 % | 1,59 | 1,75 | -9,0 % | OK | -11,5 % |
|  | 10 % | 1,42 | 1,25 | +13,3 % | Échec | +16,8 % |
|  | 20 % | 7,28 | 6,50 | +12,1 % | Échec | +12,1 % |
| Recette totale 2022 (DG Trésor, p. 2) | tous | 213,8 | 202,7 | +5,5 % | OK | +6,7 % |
| Recette totale 2024 (PLF 2026, VM tome I, p. 33) | tous | 229,6 | 210,7 | +9,0 % | OK | +10,2 % |

Bilan : 10 comparaisons sur 17 dans la tolérance de ±10 % (8 au 7 octobre). Passent désormais : point brut 2015 au taux de 5,5 % et recette 2024. Les deux recettes comprennent l'écart territorial de 2,3 Md€ ; sans lui, elles seraient de 216,1 Md€ en 2022 (+6,6 %) et 231,9 Md€ en 2024 (+10,1 %).

La répartition des travaux met toute la consommation de travaux des ménages aux taux réduits (77,0 % à 10 %, 23,0 % à 5,5 %) : l'assiette des deux dépenses fiscales dépasse de 5,5 % cette consommation en 2023. L'excès correspond probablement à des travaux comptés en investissement des ménages, que le modèle laisse au taux normal.

## Méthode écartée : restauration

Le même calcul appliqué à la restauration (dépenses fiscales 730221 et 730207, 2 000 et 171 M€ en 2023) donne une assiette de 21,7 Md€ hors taxe au taux de 10 %. La consommation de restauration des comptes nationaux est de 86,7 Md€ TTC en 2023, plus de trois fois plus. Mettre le reste au taux de 20 % dégrade la validation (essai non retenu, comptes 2022) : point brut 2025 au taux de 10 % à -22,0 % au lieu de +5,7 %, au taux de 20 % à +13,3 % au lieu de +7,9 %. Le coût publié de ces dépenses fiscales ne se laisse donc pas convertir en assiette de cette façon ; la restauration reste au taux de 10 %. L'origine de l'écart n'est pas élucidée.

La répartition des spectacles (730231, 730301) a aussi été essayée : effet inférieur à 0,01 Md€ sur chaque point, et le taux du reste n'est pas connu. Non retenue.

## Écarts expliqués et suite

- **Produits mixtes encore affectés au taux dominant** (`statut: mixte_simplifie` dans les correspondances) : abonnements d'électricité et de gaz (5,5 % en 2022 affectés à 20 %), eau (affectée à 10 % au niveau A38), boissons servies, médicaments remboursables ou non. Le tome II de Voies et Moyens ne les chiffre pas : ce ne sont pas des dépenses fiscales.
- **Taux de 2,1 %** : le modèle met tous les médicaments au taux de 2,1 % et attribue aux APU les médicaments remboursés (31 Md€ de consommation individuelle des APU) et les achats de médicaments des hôpitaux ; la DG Trésor affiche un point net égal au point brut sur ce taux, donc une part APU quasi nulle. Prochaine étape : séparer les médicaments remboursables (2,1 %) des non remboursables (10 %) avec les comptes de la santé de la DREES, fichier à déposer (site bloqué depuis l'environnement de calcul). La convention d'attribution aux APU reste à éclaircir.
- **Recette totale** : le modèle calcule une TVA théorique ; la recette réelle est plus faible (écart de TVA : fraude, erreurs, défaillances), que la DG Trésor corrige par un recalage que nous ne faisons pas.
- **Banque et immobilier** : la TVA facturée par ces branches sur option (locations professionnelles, certaines commissions) n'est pas comptée ; les comptes nationaux en enregistrent 8 Md€ en 2022.
- **Correspondances à vérifier** : 747 Md€ de consommation des ménages ont un rattachement « à vérifier » (taux connu, texte non relu) ; seuls les taux de l'alimentation ont été vérifiés dans le BOFiP.

## Indépendance de la validation

La méthode reprend celle de la DG Trésor. Le modèle utilise désormais cinq chiffrages du tome II de Voies et Moyens (PLF 2025) : deux pour répartir les travaux, trois pour l'écart territorial. Ces chiffrages viennent de l'administration fiscale (« reconstitution de base taxable à partir de données déclaratives fiscales » pour quatre d'entre eux, « données autres que fiscales » pour 710105) ; ils ne sont pas les résultats comparés par les tests. La comparaison reste donc indépendante sur l'assiette des autres produits, mais pas tout à fait sur la recette : l'écart territorial (2,3 Md€) en vient directement.

## Limites

- Données A38 pour les achats des producteurs et l'investissement, quand la DG Trésor travaille sur 138 produits et 138 branches non publiés.
- Pas d'effet de comportement. Les taux d'outre-mer et de Corse ne sont pris en compte que par l'écart global du tome II, sur la recette, pas sur le point de TVA ; franchise en base non modélisée.
- Résultat donné en valeur centrale seulement : la fourchette (règle 4 de `CLAUDE.md`) viendra avec les hypothèses de répartition des produits mixtes.
