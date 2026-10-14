---
module: depense_menages
statut: beta
mise_a_jour: 2026-10-14
---

# Fiche : dépense supplémentaire des ménages à consommation inchangée (TVA et accises)

Lot « indicateur de dépense » de la V1. La spécification (« Pouvoir d'achat ») le prévoit ainsi : le net après impôt n'inclut pas l'effet des prix ; pour les réformes de TVA et d'accises, un indicateur séparé estime la variation de dépense à partir des budgets de famille de l'Insee. Le plan l'appelait « indicateur de dépense incompressible » ; le site dit « dépense supplémentaire pour acheter les mêmes biens », qui décrit ce qui est calculé. Fait en autonomie (instruction du mainteneur) ; les choix du § 5 sont **à relire**.

## 1. Question posée

Pour une mesure du simulateur sur le taux normal de TVA, l'accise sur le gazole ou l'accise sur les essences, combien un ménage dépense-t-il de plus (ou de moins) par an pour acheter les mêmes biens, selon son niveau de vie (déciles) et son type de ménage ? En euros et en part de sa consommation.

## 2. Leviers concernés

| Levier | Unité | Postes de dépense touchés |
|--------|-------|---------------------------|
| Taux normal de TVA | point | part de chaque poste au taux normal (`registres/menages/bdf_postes_tva.csv`) |
| Accise sur le gazole | centime par litre | carburants (poste 07221), part du gazole |
| Accise sur les essences | centime par litre | carburants (poste 07221), part des essences |

## 3. Méthode

Code : `moteur/src/fr_budget/menages/depense.py`. Pipelines : `pipelines/menages/extraire_bdf.py`, `pipelines/accises/extraire_prix_sdes.py`. API : `GET /depense-menages` ; export `depense-menages.json` ; panneau du simulateur.

- **Dépenses** : dépense annuelle moyenne par ménage et par poste de l'enquête Budget de famille 2017 (tableaux TF105 et TF106), aux postes les plus fins publiés (138 postes, hors impôts, remboursements de prêts, gros travaux et transferts). Le pipeline vérifie que leur somme redonne le total publié pour chaque classe.
- **Passage à l'année simulée** : facteur de la dépense de consommation des ménages des comptes nationaux (P31, euros courants), de 2017 à la dernière année des comptes (2024), puis croissance du PIB nominal (même facteur que le levier d'indexation).
- **TVA** : une hausse de x points du taux normal t relève les prix TTC des biens au taux normal de x / (1 + t). Effet = dépense au taux normal × facteur × x / (1 + t). Le taux de l'année vient des paramètres d'OpenFisca.
- **Accises** : litres achetés en 2017 = dépense en carburants ÷ prix moyen TTC du litre en 2017 (SDES, données DGEC : gazole et SP95-E10, pondérés par la part du gazole). Les litres suivent ensuite le volume de produits pétroliers consommé par les ménages (comptes nationaux, euros chaînés). Un centime d'accise coûte un centime plus la TVA au taux normal.
- **Scénario** : effet d'une unité de chaque levier × valeur de la mesure, additionnés (calcul linéaire dans le navigateur, `web/lib/depense-menages.ts`).

## 4. Données

| Jeu (registre) | Usage |
|----------------|-------|
| `insee_bdf2017_tf105`, `insee_bdf2017_tf106`, `insee_bdf2017_metadonnees` | dépenses par poste, par type de ménage et par décile de niveau de vie |
| `insee_conso_produits_menages` | P31 et volume de produits pétroliers des ménages ; contrôle (part au taux normal) |
| `sdes_prix_produits_petroliers_2019_xls`, `sdes_prix_produits_petroliers_2025_xlsx` | prix TTC des carburants |

## 5. Choix faits en autonomie, et leurs limites

1. **Dépense à consommation inchangée.** Répercussion complète sur les prix, aucun changement d'achats. C'est une borne : un ménage qui achète moins d'un bien plus cher dépense moins que ce montant (mais consomme moins). Aucune élasticité sourcée n'est dans le registre.
2. **Taux normal par poste, bornes pour les postes mixtes.** Chaque poste est rattaché au taux normal en entier, pas du tout, ou en partie (31 postes mixtes : restauration, énergie du logement en 2017, médicaments, services culturels…). Un poste mixte va de 0 à 1 : c'est la fourchette. La valeur centrale est le milieu de la plage. Les rattachements et les articles du code général des impôts cités sont **à vérifier** (colonne `statut`).
3. **Valeur centrale confrontée aux comptes nationaux** (§ 6) : elle tombe à moins de 1,4 % de la part au taux normal de la consommation des ménages des comptes nationaux, hors loyers imputés.
4. **Structure de 2017.** La structure de consommation de chaque classe est celle de 2017 ; seuls les montants suivent la consommation nationale. Les changements depuis 2017 (prix de l'énergie, abonnements d'électricité et de gaz passés au taux normal) ne sont pas suivis poste par poste.
5. **Carburants.** Le poste 07221 comprend aussi l'électricité de recharge et les lubrifiants : il est compté en entier comme carburant (légère surestimation des litres). L'enquête ne sépare pas le gazole des essences : la part du gazole est celle de l'assiette nationale du levier (`fr_budget.agrege.accises.assiette_levier`), qui comprend des véhicules d'entreprises. Elle est la même pour toutes les classes ; un ménage roulant à l'essence paie en réalité davantage pour une mesure sur les essences et rien pour une mesure sur le gazole. Pas de fourchette pour cette part (aucune source par classe).
6. **Année.** Les effets sont calculés pour l'année de référence du simulateur (2025), quelle que soit l'année affichée pour la dette. Au-delà de 2024 (dernière année des comptes), le volume de carburants est tenu à son niveau de 2024.
7. **Champ.** L'enquête couvre la France avec les DOM, où les taux de TVA et l'accise diffèrent ; le calcul applique les taux de la métropole.
8. **Effets croisés négligés.** La TVA sur la hausse d'accise est comptée au taux de l'année ; l'effet d'une variation simultanée du taux de TVA sur la hausse d'accise (produit de deux mesures) est négligé.

## 6. Validation

Il n'existe pas de chiffrage officiel de cet indicateur. La donnée qui le porte, la part de la consommation au taux normal, est confrontée aux comptes nationaux de l'Insee (test `moteur/tests/validation/test_depense_menages_comptes_nationaux.py`, affiché dans le panneau du simulateur) :

| Grandeur | Budget de famille 2017 (central, plage) | Comptes nationaux | Écart |
|----------|------------------------------------------|-------------------|-------|
| Part de la consommation au taux normal, hors loyers imputés | 46,8 % (32,8 % à 60,7 %) | 47,4 % (2015) | −1,4 % |
| Même grandeur | 46,8 % | 46,8 % (2022) | −0,1 % |

Les comptes nationaux rattachent leurs produits aux taux par la table du levier TVA, indépendante de celle des postes de l'enquête. Limite : les deux sources diffèrent aussi de champ (assurances et services financiers mesurés autrement).

Tests unitaires (`moteur/tests/unitaires/test_depense_menages.py`) : parts bornées, un seul poste de carburants, facteurs égaux à 1 en 2017, identité de l'effet TVA, somme des deux accises égale à un centime TTC par litre, poste exonéré sans effet, ordre des classes.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-14 | Création : effet des mesures de TVA et d'accises sur la dépense des ménages, par décile et par type de ménage ; panneau du simulateur | 2 nouveaux tests de validation (comptes nationaux 2015 et 2022), réussis ; 9 tests unitaires ; 3 tests d'API ; 2 tests du site |
