# Levier TVA : rendement d'un point de TVA, premier modèle

Tâches 0.4 et 0.5 du plan. Rapport du 7 octobre 2026. Statut du levier : **non publié** (bêta en développement).

## Méthode

Reprise de la méthode du modèle de TVA théorique de la DG Trésor (Cahier n° 2016-02, parties 2.1 à 2.3), appliquée aux seules données publiques de l'INSEE (comptes nationaux annuels base 2020). Code : `moteur/src/fr_budget/agrege/tva.py`.

1. Consommation finale des ménages, des APU (individuelle) et des ISBLSM au niveau le plus fin publié (304 produits pour les ménages), chaque produit rattaché à un régime de TVA dans `registres/tva/correspondance_produits.csv`.
2. Consommation collective des APU, consommations intermédiaires et investissement au niveau A38 du TES, régime par produit dans `registres/tva/regimes_a38.csv`.
3. Investissement diminué de la production pour emploi final propre (opération P12), qui n'est pas vendue et ne porte pas de TVA.
4. TVA non déductible des producteurs : prorata de non-déductibilité de chaque branche égal à la part exonérée ou hors champ de la consommation finale de son produit (Cahier 2016-02, § 2.2.3).
5. Point brut = 1 % de l'assiette hors taxe de chaque taux ; point net = point brut moins la part payée par les APU.
6. Vieillissement 2022 → 2025 par l'évolution des recettes de TVA, comme la DG Trésor (Trésor-Éco n° 371, note 5), avec les recettes budgétaires publiées : 202,7 Md€ en 2022 (DG Trésor) et 210,0 Md€ prévus pour 2025 (PLF 2026).

Taux de TVA : paramètres d'OpenFisca-France. Données : `pipelines/tva/` → `data/processed/tva/`.

## Résultats

| Référence | Taux | Modèle (Md€) | Référence (Md€) | Écart | Statut |
|---|---|---|---|---|---|
| Point brut 2025 (DG Trésor, tableau 1) | Ensemble | 14,18 | 13,70 | +3,5 % | OK |
|  | 2,1 % | 0,62 | 0,40 | +55,3 % | Échec |
|  | 5,5 % | 1,95 | 2,40 | -18,8 % | Échec |
|  | 10 % | 2,01 | 1,90 | +5,7 % | OK |
|  | 20 % | 9,60 | 8,90 | +7,9 % | OK |
| Point net 2025 (DG Trésor, tableau 2) | Ensemble | 11,59 | 11,40 | +1,7 % | OK |
|  | 2,1 % | 0,22 | 0,40 | -44,7 % | Échec |
|  | 5,5 % | 1,84 | 2,00 | -8,2 % | OK |
|  | 10 % | 1,87 | 1,60 | +16,7 % | Échec |
|  | 20 % | 7,67 | 7,50 | +2,2 % | OK |
| Point brut 2015 (DG Trésor 2016, tableau 8) | Ensemble | 10,77 | 9,75 | +10,5 % | Échec |
|  | 2,1 % | 0,48 | 0,50 | -3,3 % | OK |
|  | 5,5 % | 1,55 | 1,75 | -11,5 % | Échec |
|  | 10 % | 1,46 | 1,25 | +16,8 % | Échec |
|  | 20 % | 7,28 | 6,50 | +12,1 % | Échec |
| Recette totale 2022 (DG Trésor, p. 2) | tous | 216,3 | 202,7 | +6,7 % | OK |
| Recette totale 2024 (PLF 2026, VM tome I, p. 33) | tous | 232,2 | 210,7 | +10,2 % | Échec |

Bilan : 8 comparaisons sur 17 dans la tolérance de ±10 %. Les totaux du point de TVA 2025 (brut et net) et la recette 2022 sont dans la tolérance ; la répartition par taux ne l'est pas encore.

## Écarts expliqués et suite

- **Produits mixtes affectés au taux dominant** (`statut: mixte_simplifie` dans les correspondances, 260 Md€ de consommation des ménages) : travaux dans les logements (10 % et 5,5 % affectés à 10 %), abonnements d'électricité et de gaz (5,5 % en 2022 affectés à 20 %), eau (affectée à 10 % au niveau A38), boissons servies, médicaments remboursables ou non. Ces simplifications déplacent de l'assiette du taux réduit vers les taux de 10 % et 20 %, ce que montrent les écarts (5,5 % sous-estimé, 10 % et 20 % surestimés). Prochaine étape : répartir ces produits avec le coût des taux réduits publié dans Voies et Moyens tome 2 (PLF 2024 pour l'année 2022).
- **Taux de 2,1 %** : le modèle attribue aux APU les médicaments remboursés (31 Md€ de consommation individuelle des APU) et les achats de médicaments des hôpitaux ; la DG Trésor affiche un point net égal au point brut sur ce taux, donc une part APU quasi nulle. La convention d'attribution reste à éclaircir avant toute correction.
- **Recette totale** : le modèle calcule une TVA théorique ; la recette réelle est plus faible (écart de TVA : fraude, erreurs, défaillances), que la DG Trésor corrige par un recalage que nous ne faisons pas. L'écart 2024 (+10,2 %) est juste au-dessus de la tolérance.
- **Banque et immobilier** : la TVA facturée par ces branches sur option (locations professionnelles, certaines commissions) n'est pas comptée ; les comptes nationaux en enregistrent 8 Md€ en 2022.
- **Correspondances à vérifier** : 747 Md€ de consommation des ménages ont un rattachement « à vérifier » (taux connu, texte non relu) ; seuls les taux de l'alimentation ont été vérifiés dans le BOFiP.

## Indépendance de la validation

La méthode reprend celle de la DG Trésor, mais aucun résultat de la DG Trésor n'entre dans le calcul de l'assiette : les seules valeurs de référence utilisées par le modèle sont les recettes de TVA servant au vieillissement. L'usage prévu du tome 2 de Voies et Moyens, dont certains chiffrages viennent du même modèle de la DG Trésor, réduira cette indépendance ; il sera signalé.

## Limites

- Données A38 pour les achats des producteurs et l'investissement, quand la DG Trésor travaille sur 138 produits et 138 branches non publiés.
- Pas d'effet de comportement, pas de taux particuliers (Corse, outre-mer, franchise en base).
- Résultat donné en valeur centrale seulement : la fourchette (règle 4 de `CLAUDE.md`) viendra avec les hypothèses de répartition des produits mixtes.
