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
- Choc de taux : la part de la dette au nouveau taux après t années est 1 - (1 - s)^t. L'exposition de l'année k pondère deux calendriers par p, la part du refinancement faite le 1er janvier : refinancement continu, dont le surcoût est la moyenne exacte sur l'année, 1 - ((1 - s)^k - (1 - s)^(k-1)) / ln(1 - s) ; refinancement au 1er janvier, 1 - (1 - s)^k. Décision du mainteneur du 8 octobre 2026 : moyenne exacte, qui remplace l'évaluation en milieu d'année (celle-ci la dépassait de 1,7 % la première année).
- Ajustement stock-flux implicite : ce qui referme la formule sur une dette observée.

## 4. Données

- Comptes des APU (fiche `comptes_apu.md`).
- Dette négociable de l'État : PLF 2027, projet annuel de performances « Engagements financiers de l'État » (source `plf2027_pap_engagements_financiers_etat`, chiffrages `dette_etat_*`, pages 32 à 34 et 40) : encours fin 2025, tableau de financement 2026-2027, scénario de taux, choc de taux.
- Le site de l'Agence France Trésor (profil de remboursement détaillé) est protégé par une page anti-robots qui bloque l'environnement de calcul.

## 5. Hypothèses

- `dette_part_refinancement_debut_annee` : part du refinancement de l'année réalisée dès le 1er janvier ; 0 (refinancement continu), plage 0 à 1. Remplace `dette_fraction_premiere_annee_exposee` (0,5, plage 0,5 à 1) avec la moyenne exacte.
- À créer : taux de marché au-delà de 2027, croissance en valeur, ajustement stock-flux (zéro ou moyenne historique, avec plage).

Part refinancée de la dette de l'État en 2027, calculée par `surcout_choc_taux_etat` : (émissions à moyen et long terme 2027 + titres à court terme fin 2026 + leur variation 2027) / encours fin 2026 = (340,0 + 205,5 + 2,2) / 2 822,4 = 19,4 %. L'encours fin 2026 est reconstitué en valeur nominale (encours fin 2025 + émissions 2026 - amortissements nominaux 2026 + variation des titres courts 2026) ; les émissions sont comptées à leur montant publié, sans correction des primes et décotes.

## 6. Validation

- Cas analytiques (`moteur/tests/unitaires/test_dette.py`) : dette stable si r = g et pb = 0 ; effet boule de neige si r > g ; solde primaire stabilisant ; trajectoire sur plusieurs années ; convergence géométrique du taux apparent vers le taux de marché.
- Choc de taux (`moteur/tests/validation/test_dette_choc_taux.py`) : un choc de +1 point au 1er janvier 2027 coûte 3,4 Md€ la première année selon le PLF 2027 (page 40). Modèle : **2,84 Md€, écart -16,6 % : échec** (tolérance ±10 % ; -15,1 % avec l'ancienne évaluation en milieu d'année). Fourchette selon la part du refinancement faite le 1er janvier : 2,84 à 5,48 Md€, qui contient la référence. L'écart vient du calendrier des émissions et du renouvellement des titres courts dans l'année, que le modèle à une seule part refinancée ne distingue pas.
- Cinquième année, à titre indicatif (non testée, encours tenu constant) : 17,5 Md€ (fourchette 17,5 à 18,6) pour « environ 19 Md€ » dans la source ; avec un encours croissant, le modèle donnerait davantage. Le test attend la trajectoire de dette 2027-2031 du rapport économique, social et financier du PLF 2027, pas encore en ligne.
- Reste à faire : reproduire une trajectoire officielle de dette avec ses hypothèses.

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
| 2026-10-08 | Part refinancée et choc de taux sur la dette de l'État (PLF 2027) | 2 tests unitaires créés, réussis ; 1 test de validation créé, en échec (-15,1 %) |
| 2026-10-08 | Relecture finale : description de la formule du choc de taux précisée (approximation en milieu d'année, écart à la moyenne exacte publié) | aucun |
| 2026-10-08 | Choc de taux : moyenne exacte sur l'année (décision du mainteneur) ; hypothèse `dette_part_refinancement_debut_annee` | test_dette_choc_taux : -15,1 % → -16,6 % (échec inchangé) ; tests unitaires du choc réécrits pour la nouvelle formule (3 tests) |
| 2026-10-09 | Validation de la cinquième année du choc (« environ 19 Md€ », PAP 2027 page 40), encours de fin 2026 tenu constant | 1 test de validation créé, réussi : 17,51 Md€, écart -7,8 % |
