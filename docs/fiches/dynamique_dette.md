---
module: dynamique_dette
statut: non_publie
mise_a_jour: 2026-10-08
---

# Fiche : dynamique de la dette publique

Lot 1.2 du plan (phase 1). Formules seulement : les hypothèses (croissance, taux de marché, part refinancée) restent à sourcer.

## 1. Question posée

Comment évolue le ratio de dette publique au PIB d'une année à l'autre, selon le solde primaire, la croissance en valeur et le taux d'intérêt apparent ?

## 2. Ce que l'utilisateur règle

Rien directement : la dynamique reçoit le solde primaire de la baseline et des réformes. L'effet de croissance des réformes (multiplicateur) est un interrupteur désactivé par défaut (phase 3).

## 3. Méthode

Code : `moteur/src/fr_budget/dette.py` (fonctions pures).

    d(t+1) = d(t) * (1 + r) / (1 + g) - pb + sfa

- d : dette au sens de Maastricht en ratio de PIB ; r : taux apparent (intérêts versés rapportés à la dette de l'année précédente) ; g : croissance du PIB en valeur ; pb : solde primaire en ratio de PIB ; sfa : ajustement stock-flux.
- Taux apparent : chaque année, la part refinancée de la dette (titres arrivant à échéance et emprunts nouveaux) prend le taux de marché, le reste garde son taux : r(t+1) = (1 - s) * r(t) + s * i(t).
- Solde primaire stabilisant : pb* = d * (r - g) / (1 + g).
- Ajustement stock-flux implicite : ce qui referme la formule sur une dette observée.

## 4. Données

Comptes des APU (fiche `comptes_apu.md`). Pour la part refinancée chaque année, il faudra le profil de remboursement de la dette de l'État, publié par l'Agence France Trésor (bulletin mensuel). Son site est protégé par une page anti-robots qui bloque l'environnement de calcul : fichier à déposer par le mainteneur.

## 5. Hypothèses

À créer : part refinancée chaque année, taux de marché à l'émission, croissance en valeur, ajustement stock-flux (zéro ou moyenne historique, avec plage).

## 6. Validation

- Cas analytiques (`moteur/tests/unitaires/test_dette.py`) : dette stable si r = g et pb = 0 ; effet boule de neige si r > g ; solde primaire stabilisant ; trajectoire sur plusieurs années ; convergence géométrique du taux apparent vers le taux de marché.
- Reste à faire : reproduire une trajectoire officielle de dette (programme de stabilité ou plan budgétaire et structurel de moyen terme ; Commission européenne) avec les hypothèses de cette trajectoire.

**Décomposition observée de la dette des APU, 2015-2025** (données INSEE, solde primaire selon la convention A de `comptes_apu.md`) :

| Année | Dette (% PIB) | r apparent (%) | g (%) | Solde primaire (% PIB) | Ajustement stock-flux implicite (points de PIB) |
|---|---|---|---|---|---|
| 2015 | 97,0 | 2,16 | 2,2 | -1,86 | -1,00 |
| 2016 | 98,1 | 1,99 | 1,4 | -1,86 | -1,27 |
| 2017 | 98,8 | 1,87 | 2,7 | -1,57 | -0,19 |
| 2018 | 98,5 | 1,84 | 2,8 | -0,55 | +0,12 |
| 2019 | 98,2 | 1,59 | 3,3 | -0,88 | +0,35 |
| 2020 | 114,9 | 1,25 | -4,7 | -7,65 | +2,99 |
| 2021 | 112,8 | 1,31 | 8,2 | -5,20 | -0,01 |
| 2022 | 111,4 | 1,80 | 5,8 | -2,82 | +0,04 |
| 2023 | 109,5 | 1,81 | 6,8 | -3,48 | -0,15 |
| 2024 | 112,6 | 1,94 | 3,6 | -3,71 | +1,15 |
| 2025 | 115,7 | 1,99 | 1,9 | -2,87 | +0,08 |

L'ajustement stock-flux n'est pas négligeable certaines années (+3,0 points en 2020, +1,2 en 2024, -1,0 et -1,3 en 2015 et 2016). Une hypothèse d'ajustement nul sous-estimerait l'incertitude de la trajectoire ; la plage devra en tenir compte. Les causes (trésorerie, primes et décotes à l'émission, intérêts courus) ne sont pas analysées ici.

## 7. Limites

- Le taux apparent d'une seule catégorie de dette : pas de distinction entre dette à taux fixe, dette indexée sur l'inflation et dette à court terme.
- Le PIB en valeur est exogène : pas d'effet du solde primaire sur la croissance tant que l'interrupteur de multiplicateur est désactivé.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-08 | Formules de la dynamique de la dette et du taux apparent ; décomposition observée 2015-2025 | 10 tests unitaires créés, tous réussis |
