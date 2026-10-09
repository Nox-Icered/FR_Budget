---
levier: dotations_collectivites
statut: beta
mise_a_jour: 2026-10-09
---

# Fiche : dotations de l'État aux collectivités

Lot 2.6 du plan (phase 2). Décisions du mainteneur du 9 octobre 2026, options (a) :
- effet sur le solde public par la réaction de l'investissement local ;
- deux curseurs, la DGF et les compensations ;
- borne de ±10 % ;
- validation des montants votés face aux montants exécutés.

## 1. Question posée

Que change pour le solde public et la dette une variation de x % de la dotation globale de fonctionnement (DGF), ou des compensations fiscales versées par l'État aux collectivités ? Exemple : « baisse de 5 % de la DGF ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Variation de la DGF (ligne 3101) | 32,58 Md€ en 2026 | de -10 à +10 %, par pas de 1 | `plf2026_voies_et_moyens_tome1` |
| Variation des compensations fiscales (14 lignes, voir § 3) | 6,93 Md€ en 2026 | de -10 à +10 %, par pas de 1 | `plf2026_voies_et_moyens_tome1` |

Repère pour la borne de ±10 % : la baisse de la DGF de 2014 à 2017 a été d'environ 3,5 Md€ par an (Caisse des dépôts, Éclairages n° 8, encadré 1).

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/dotations.py`, leviers dans `moteur/src/fr_budget/scenario.py`).
- **Extraction** : `pipelines/dotations_collectivites/extraire_psr.py` lit le tableau des prélèvements sur recettes au profit des collectivités dans les tomes I des PLF 2024, 2025 et 2026. Il repère les colonnes de chaque page. La somme des lignes redonne la ligne de total publiée, à l'arrondi près, pour les douze colonnes.
- **Compensations retenues** : lignes 3104, 3107, 3119 à 3123, 3130, 3135, 3145, 3146, 3159, 3163 et 3165, c'est-à-dire les compensations d'exonérations et de réformes fiscales.
  - Le fonds de compensation de la TVA (3106) est exclu : il rembourse la TVA payée sur l'investissement, et le réduire serait une autre réforme.
  - Le fonds de compensation des nuisances aéroportuaires (3133) est exclu également.
- **Pourquoi le solde public ne bouge pas de tout le montant.** L'État et les collectivités font tous deux partie des administrations publiques. Une baisse de dotation améliore le solde de l'État et dégrade d'autant celui des collectivités. Le solde public ne change que par leur réaction ; le modèle retient la baisse de leur investissement.
- **Calcul de cette réaction, par niveau de collectivité** (communes, groupements à fiscalité propre, départements, régions) :

  variation de l'investissement = élasticité × (investissement / dotations) × variation de la dotation reçue

  Les composantes :
  - élasticité de court terme de la Caisse des dépôts ;
  - investissement hors remboursements et « concours de l'État » de l'OFGL, exercice 2024 ;
  - partage de la variation entre niveaux au prorata de la DGF reçue (OFGL 2024, plus la DGF réintégrée des régions en 2026), ou des « péréquations et compensations fiscales » pour les compensations ;
  - taux par niveau plafonné à 1.
- **Taux de répercussion obtenus** :

| Dotation | Valeur centrale | Fourchette |
|----------|-----------------|------------|
| DGF | 0,44 | 0,19 à 0,72 |
| Compensations | 0,40 | 0,19 à 0,67 |

- **Effet d'une variation de x %** : x % du montant 2026, ramené en euros de 2025 par la croissance nominale 2026 du RESF 2027, multiplié par le taux de répercussion, puis tenu constant en points de PIB. L'effet sur le seul budget de l'État (`effet_etat_unitaire`) est exporté et affiché à part. Exemple : -1 % de DGF améliore le budget de l'État de 0,32 Md€ et le solde public de 0,14 Md€.
- **Régions** : depuis 2018, elles recevaient des fractions de TVA au lieu de la DGF. En 2026, 5 172 M€ sont réintégrés dans la DGF (`dotations_dgf_regions_reintegree_2026`). Ce montant est ajouté à leurs dotations, pour la répartition comme pour le ratio, faute de quoi le ratio décrirait des régions presque sans dotation.

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `plf2026_voies_et_moyens_tome1_pdf`, `plf2025_…`, `plf2024_voies_et_moyens_tome1_pdf` | prélèvements par ligne : exécution N-2, LFI et révisé N-1, PLF N | PLF 2024 à 2026 |
| `ofgl_communes_agregats_json`, `ofgl_gfp_…`, `ofgl_departements_…`, `ofgl_regions_…` | investissement hors remboursements, concours de l'État, DGF, péréquations et compensations, par niveau | exercices 2023 à 2025 |
| `cdc_eclairages_8_pdf` | élasticités de l'investissement aux dotations | 2015 (données 2001-2013) |

## 5. Hypothèses

| Hypothèse (`registres/hypotheses.yaml`) | Valeur centrale | Plage |
|-----------------------------------------|-----------------|-------|
| `dotations_elasticite_investissement_communes` | 0,14 | 0,10 à 0,40 |
| `dotations_elasticite_investissement_gfp` | 0,19 | 0,10 à 0,22 |
| `dotations_elasticite_investissement_departements` | 0,40 | 0,10 à 0,62 |
| `dotations_elasticite_investissement_regions` | 0,32 | 0,10 à 0,32 |

Les bornes s'expliquent ainsi :
- **basse** : 0,1, le bas de la fourchette générale annoncée par l'étude ;
- **haute** : le coefficient estimé sur les seules baisses de dotations pour les groupements et les départements, l'effet de trois baisses successives pour les communes (0,40), et l'estimation centrale pour les régions, dont le coefficient sur les baisses n'est pas significatif.

## 6. Validation

L'assiette du levier est un montant voté. Sa validation compare le montant inscrit en loi de finances initiale (tome I du PLF suivant) à l'exécution (tome I du PLF de N+2).

- Tolérance : ±10 %.
- Test : `moteur/tests/validation/test_levier_dotations.py`.

| Référence | Exécution | Voté en LFI (modèle) | Écart | Dans la tolérance |
|-----------|-----------|----------------------|-------|-------------------|
| DGF 2023 | 26 929,6 M€ | 26 931,4 M€ | +0,0 % | oui |
| DGF 2024 | 27 238,5 M€ | 27 245,0 M€ | +0,0 % | oui |
| Compensations 2023 | 8 091,4 M€ | 7 809,7 M€ | -3,5 % | oui |
| Compensations 2024 | 8 389,3 M€ | 8 012,0 M€ | -4,5 % | oui |

**Ce qui n'est pas validé : le taux de répercussion.** Il repose sur une seule étude, ancienne (2001-2013), qui ne mesure que l'investissement à un an. Aucune source indépendante ne l'a encore confronté ; le rapport de la Cour des comptes sur les finances publiques locales serait la référence à déposer. Statut « bêta, non validé ».

## 7. Limites connues

- Seule la réaction de l'investissement est comptée. Les collectivités peuvent aussi réduire leurs dépenses de fonctionnement, augmenter leurs impôts ou emprunter ; l'effet sur le solde public peut donc être plus fort ou plus faible.
- L'élasticité est celle de la première année. Elle est tenue constante en points de PIB ensuite.
- La répartition des compensations entre niveaux suit l'agrégat OFGL « péréquations et compensations fiscales », qui contient aussi des péréquations entre collectivités.
- Les exercices OFGL 2024 et la DGF 2026 sont d'années différentes.
- La combinaison avec le levier des crédits par mission ne compte pas deux fois : la mission « Relations avec les collectivités territoriales » est exclue de ce dernier.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-09 | Création du levier : extraction des tomes I des PLF 2024 à 2026 et des agrégats OFGL | 4 nouvelles références de validation, toutes dans la tolérance ; tableau : 30 sur 38 |
