---
module: comptes_apu
statut: non_publie
mise_a_jour: 2026-10-08
---

# Fiche : comptes des administrations publiques

Lot 1.1 du plan (phase 1). Socle observé du tableau de bord et point de départ de la baseline et de la dynamique de la dette.

## 1. Question posée

Quels sont, par année et par sous-secteur (État, organismes divers d'administration centrale, administrations locales, sécurité sociale), les dépenses, les recettes, le solde, les intérêts et la dette des administrations publiques, en milliards d'euros et en points de PIB ?

## 2. Ce que l'utilisateur règle

Rien : ce sont des données observées.

## 3. Méthode

- Extraction : `pipelines/apu/extraire_comptes_apu.py` lit les tableaux de l'INSEE tels que téléchargés (`data/raw/apu/insee/`) et écrit `data/processed/apu/comptes_apu.csv` (format long, montants repris sans arrondi).
- Lecture : `moteur/src/fr_budget/apu.py` (`comptes_apu`, `ratio_pib`, `solde_primaire`).

| Indicateur | Définition | Tableau INSEE |
|---|---|---|
| `depenses`, `recettes` | Total des dépenses, total des recettes | 3.201 (APU), 3.202 à 3.205, 3.212 (sous-secteurs) |
| `capacite_financement` | Capacité (+) ou besoin (-) de financement (B9NF) | idem |
| `interets_verses`, `interets_recus` | Intérêts (D41) en dépenses et en recettes | idem |
| `solde_maastricht` | Déficit au sens de Maastricht | 3.106 |
| `dette_maastricht` | Dette au sens de Maastricht | 3.101 |
| `pib` | Produit intérieur brut (B1GQ) | 1.101 |

Les dépenses et recettes de chaque sous-secteur sont consolidées à l'intérieur du sous-secteur, pas entre sous-secteurs : leur somme ne donne pas celle des APU (note du tableau 3.215). Les soldes, eux, s'additionnent.

## 4. Données

Source `insee_comptes_nationaux_2025` et jeux `insee_cna2025_*` dans les registres (édition 2025 des comptes nationaux, compte semi-définitif des APU actualisé le 28 août 2026). Années : de 1949 à 2025 selon les tableaux.

## 5. Hypothèses et choix

**Solde primaire : deux conventions.** Le solde primaire retire les intérêts du solde. Deux définitions existent :

| Convention | Formule | APU 2025 |
|---|---|---|
| A. Intérêts versés | capacité de financement + intérêts versés | -85,9 Md€ (-2,87 % du PIB) |
| B. Intérêts nets | capacité de financement + intérêts versés - intérêts reçus | -89,3 Md€ (-2,99 % du PIB) |

Calcul à partir des données 2025 du tableau 3.201 : capacité de financement -151,6 Md€, intérêts versés 65,7 Md€, intérêts reçus 3,5 Md€, PIB 2 991,1 Md€. Convention A retenue par le mainteneur le 8 octobre 2026, cohérente avec la formule de la dette de `CLAUDE.md`, où le terme d'intérêts porte sur la dette brute.

## 6. Validation

Tests `moteur/tests/validation/test_comptes_apu.py` (reproduction des publications de l'INSEE, pas encore une validation contre une source indépendante) :

- capacité de financement = recettes - dépenses, chaque sous-secteur, chaque année (0,01 Md€) ;
- capacité de financement = déficit au sens de Maastricht depuis 2014 (0,01 Md€) ;
- solde des APU = somme des soldes de l'administration centrale, des administrations locales et de la sécurité sociale, 2015-2025 (0,01 Md€) ;
- dette en % du PIB recalculée = ratio publié, 2015-2025 (0,055 point : arrondi du ratio au dixième et de la dette au dixième de milliard).

Constat : avant 2020, la ligne « Série du PIB utilisée » du tableau 3.101 ne reproduit pas le ratio de dette publié dans le même tableau (écart jusqu'à 0,30 point en 2018) ; le PIB du tableau 1.101 le reproduit. Le modèle utilise donc le PIB du tableau 1.101.

## 7. Limites

- Données annuelles seulement ; l'année la plus récente (2025) est un compte semi-définitif, révisable.
- Dépenses par fonction (COFOG) pas encore extraites : le fichier n'est pas proposé sur la page de l'INSEE ; à reprendre depuis Eurostat (tableau gov_10a_exp, alimenté par l'INSEE).

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-08 | Extraction des comptes des APU 2025 et premiers contrôles | 14 tests de contrôle créés, tous réussis |
| 2026-10-08 | Convention du solde primaire : intérêts versés (décision du mainteneur) | aucun |
