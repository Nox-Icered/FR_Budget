---
module: entreprises
statut: beta
mise_a_jour: 2026-10-14
---

# Fiche : effet des leviers sur la charge des entreprises, par taille et par secteur

Lot « entreprises » de la V1 (spécification : « Voir la charge par taille et secteur »). Fait en autonomie (instruction du mainteneur). Les choix du § 5 sont **à relire**.

## 1. Question posée

Pour une mesure du simulateur qui change la charge fiscale ou sociale des entreprises, quelle part revient à chaque taille d'entreprise et à chaque secteur, en millions d'euros par an et par salarié ou par entreprise ?

## 2. Leviers concernés

| Levier | Clé de répartition | Classes |
|--------|--------------------|---------|
| Taux de cotisation patronale du secteur privé | masse salariale du secteur privé, Urssaf, 2024 | 8 tranches de salariés ; 7 grands secteurs (Urssaf) |
| Allègements généraux | réduction générale et réductions des taux maladie et famille (catégories 11, 15 et 16), Urssaf, 2024 | mêmes classes |
| Taux normal de l'impôt sur les sociétés | impôt brut de 2025 (DGFiP Statistiques n° 51) ; fourchette de la part : impôt brut et résultat fiscal, 2025 et 2024 (DGFiP Statistiques n° 39) | 4 catégories d'entreprises ; 10 secteurs (DGFiP) |
| Surtaxe des entreprises de plus d'un milliard d'euros de chiffre d'affaires | toute la charge aux grandes entreprises | 4 catégories ; pas de répartition par secteur |

TVA et accises ne sont pas réparties : elles sont payées par les consommateurs. Les autres leviers ne portent pas sur la charge des entreprises.

## 3. Méthode

Effet d'une classe = effet national du levier pour une unité (rendement unitaire du simulateur, en fourchette, `fr_budget.scenario.rendement_unitaire`) × part de la classe dans l'assiette. Les fourchettes se combinent par leurs extrêmes (`repartition.produit`). La somme des classes redonne l'effet national du simulateur. Dans le simulateur, l'effet d'un scénario est la somme, classe par classe, de la valeur de chaque mesure multipliée par l'effet d'une unité ; c'est exact pour ce modèle, qui est linéaire.

Code : `moteur/src/fr_budget/entreprises/repartition.py`. Pipelines : `pipelines/entreprises/extraire_urssaf.py`, `pipelines/entreprises/extraire_dgfip.py`. Export : `entreprises.json` ; API : `GET /entreprises`.

## 4. Données

- Urssaf, open data, licence ODbL (registre des sources, identifiants `urssaf_open_data_*`) : masse salariale et effectifs par tranche de taille d'entreprise (annuel) et par secteur (trimestriel, somme des quatre trimestres) ; exonérations par tranche et par secteur. Année retenue : 2024, la dernière commune aux quatre jeux.
- DGFiP Statistiques n° 51 (impôt 2025) et n° 39 (impôt 2024) : impôt brut, résultat fiscal et nombre d'entreprises par catégorie et par secteur.

## 5. Choix faits en autonomie, et leurs limites

1. **Répartition proportionnelle à l'assiette, sans comportement.** Chaque classe supporte la mesure selon sa part de l'assiette ; pas de répercussion sur les prix, les salaires ou l'emploi. L'incidence des cotisations patronales sur les salaires est traitée pour les ménages types (fiche `menages_types.md`), pas ici.
2. **Cotisations : masse salariale entière.** La hausse d'un point porte sur toute la masse salariale du secteur privé, comme la valeur de point de la CCSS (hausse hors du champ des allègements). Limite : la masse salariale de l'Urssaf comprend les salaires au-dessus du plafond et les secteurs non marchands privés (associations), dont la cotisation réelle peut différer.
3. **Impôt sur les sociétés : clé de l'impôt brut, fourchette de la part.** La part des petites entreprises dans un point de taux normal est surestimée par l'impôt brut, qui comprend leur taux réduit de 15 % ; le résultat fiscal donne une autre clé. La fourchette de la part de chaque classe va du minimum au maximum de quatre clés (impôt brut et résultat fiscal, 2025 et 2024).
4. **Surtaxe : grandes entreprises au sens de la DGFiP.** La surtaxe vise les entreprises de plus d'un milliard d'euros de chiffre d'affaires ; les « grandes entreprises » de la DGFiP (environ 370 en 2025) en sont proches sans être identiques. Aucune donnée publiée ne permet de la répartir par secteur.
5. **Nomenclatures séparées.** Les cotisations restent dans les classes de l'Urssaf (tranches de salariés, grands secteurs), l'impôt dans celles de la DGFiP (catégories d'entreprises, secteurs). Aucune table de passage n'est inventée ; les deux tableaux ne s'additionnent pas.
6. **Années.** Données de l'Urssaf de 2024, de la DGFiP de 2025 (et 2024), appliquées à l'effet national de l'année de référence du simulateur : la structure par classe est supposée stable.
7. **Licence ODbL.** Les tables dérivées des données de l'Urssaf (`data/processed/entreprises/taille.csv`, `secteur.csv`, `masse_salariale_annuelle.csv`, et l'export `entreprises.json`) sont publiées sous licence ODbL, comme les jeux d'origine.

## 6. Validation

La répartition elle-même n'a pas de référence officielle. Les données qui la portent sont confrontées à une source indépendante, les comptes de la sécurité sociale (tests `moteur/tests/validation/test_entreprises_urssaf_ccss.py`, affichés sur la page Entreprises) :

| Grandeur | Urssaf | CCSS | Écart |
|----------|--------|------|-------|
| Un point de cotisation sur la masse salariale du secteur privé, 2025 | 7,40 Md€ | 7,38 Md€ (octobre 2025) | +0,3 % |
| Même grandeur, 2017 | 5,58 Md€ | 5,57 Md€ (septembre 2018) | +0,3 % |
| Allègements généraux des salariés, 2024 | 74,38 Md€ | 77,59 Md€ (octobre 2026) | −4,1 % |

L'écart sur les allègements vient sans doute du champ : l'Urssaf couvre les employeurs du secteur privé de son réseau, la CCSS tous les attributaires (y compris le régime agricole). Il reste dans la tolérance de ±10 %.

Tests unitaires (`moteur/tests/unitaires/test_entreprises.py`) : les parts somment à un, les effets redonnent l'effet national, la surtaxe va aux grandes entreprises, les allègements accrus baissent la charge de chaque classe.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-14 | Création : répartition de quatre leviers par taille et par secteur ; page Entreprises et panneau du simulateur | 3 nouveaux tests de validation (Urssaf contre CCSS), tous réussis ; 13 tests unitaires ; 4 tests d'API ; 2 tests du site |
