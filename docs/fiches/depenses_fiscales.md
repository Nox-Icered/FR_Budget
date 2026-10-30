---
levier: depenses_fiscales
statut: beta
mise_a_jour: 2026-10-09
---

# Fiche : dépenses fiscales (niches fiscales)

Lot 2.4 du plan (phase 2). Décisions du mainteneur du 9 octobre 2026 : réduction d'une dépense du catalogue **et** de toutes les dépenses d'un impôt (option 1 (c)) ; dépenses de TVA et d'accise sur les énergies exclues (option 2 (a)) ; rendement égal au coût officiel, sans effet de comportement (option 3 (a)).

## 1. Question posée

Combien rapporterait la réduction de x % d'une dépense fiscale (par exemple « suppression de la réduction d'impôt au titre des dons, 110201 »), ou de toutes les dépenses fiscales d'un impôt (par exemple « réduction de 10 % des dépenses fiscales de l'impôt sur le revenu ») ?

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Réduction d'une dépense fiscale du catalogue (251 dépenses chiffrées, hors TVA et accises sur les énergies) | 0 % | de 0 à 100 %, par pas de 5 | `plf2026_voies_et_moyens_tome2` |
| Réduction de toutes les dépenses fiscales d'un impôt (7 parties du tome II) | 0 % | de 0 à 100 %, par pas de 5 | `plf2026_voies_et_moyens_tome2` |

Une même dépense ne peut pas être réglée deux fois : le moteur refuse une dépense choisie avec le curseur de son impôt, ou la même dépense deux fois (`verifier_double_compte`) ; le site bloque ces combinaisons.

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/depenses_fiscales.py`, leviers dans `moteur/src/fr_budget/scenario.py`).
- **Extraction** : `pipelines/niches_fiscales/extraire_tome2.py` lit chaque fiche des tomes II des PLF 2024, 2025 et 2026 (numéro, libellé, impôt, coût réalisé N-2 et prévu N-1 et N, fiabilité) et écrit `data/processed/niches_fiscales/depenses_fiscales.csv`. Les mentions « nc », « ε » et « - » sont gardées en texte.
- **Convention du tome II** (sous-partie V, méthodologie) : une dépense non chiffrée reprend le dernier montant chiffré du même tome ; « ε » et « - » valent zéro (`cout`). Avec cette convention, l'extraction redonne exactement le total publié de chaque tome, pour chaque année et chaque impôt.
- **Rendement** d'une réduction de x % : x % du coût prévu pour 2026 par le PLF 2026, ramené en euros de 2025 par la croissance nominale 2026 du RESF 2027 (`plf2027_resf`), puis rapporté au PIB 2025 et tenu constant en points de PIB (`scenario_rendement_constant_pib`). Cela revient à rapporter le coût 2026 au PIB 2026. Exemple : un pour cent des dépenses de l'impôt sur le revenu rapporte 0,405 Md€ de 2025 ; la suppression de 110201 rapporte 2,16 Md€ (fourchette 1,38 à 3,40).
- **Site** : une dépense choisie devient une mesure sur le levier générique `depense_fiscale` (1 Md€ de 2025, plage d'une dépense), de valeur x fois le rendement d'un pour cent publié dans `depenses-fiscales.json` (`web/lib/depenses-fiscales.ts`). Le modèle étant linéaire, le résultat égale celui du moteur (test `api/tests/test_api_depenses_fiscales.py`).

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `plf2026_voies_et_moyens_tome2_pdf` | coût réalisé 2024, prévu 2025 et 2026 (465 fiches) ; coût du levier | PLF 2026 |
| `plf2025_voies_et_moyens_tome2_pdf` | coût réalisé 2023, prévu 2024 et 2025 (474 fiches) ; validation | PLF 2025 |
| `plf2024_voies_et_moyens_tome2_pdf` | coût réalisé 2022, prévu 2023 et 2024 (467 fiches) ; validation et plages | PLF 2024 |

Le PLF 2027 (déposé en octobre 2026) n'a pas encore son tome II en ligne : à intégrer dès sa publication.

## 5. Hypothèses

| Hypothèse (`registres/hypotheses.yaml`) | Valeur centrale | Plage | Effet sur le résultat |
|-----------------------------------------|-----------------|-------|-----------------------|
| `depenses_fiscales_ecart_depense` | 0 | -0,362 à +0,575 | rendement d'une dépense choisie |
| `depenses_fiscales_ecart_impot_revenu` | 0 | 0 à +0,062 | rendement du curseur de l'impôt |
| `depenses_fiscales_ecart_impot_revenu_et_societes` | 0 | -0,02 à +0,012 | idem |
| `depenses_fiscales_ecart_impot_societes` | 0 | -0,17 à +0,087 | idem |
| `depenses_fiscales_ecart_autres_impots_directs` | 0 | -0,035 à +0,024 | idem |
| `depenses_fiscales_ecart_enregistrement_timbre` | 0 | 0 à +4,948 | idem (réévaluation du « pacte Dutreil », +4,2 Md€, PLF 2026) |
| `depenses_fiscales_ecart_autres_droits` | 0 | 0 à +2,8 | idem |
| `depenses_fiscales_ecart_impots_locaux` | 0 | 0 à +0,2 | idem |

Valeurs basse et haute du rendement : coût × (1 + plage basse) et coût × (1 + plage haute). Pour une dépense, la plage reprend les 10e et 90e centiles des écarts entre coût prévu à un an (PLF 2024, année 2024) et coût réalisé (PLF 2026), sur 274 dépenses. Pour un impôt, elle va de zéro à l'écart extrême du total sur trois comparaisons. Les tests unitaires recalculent ces plages à partir des données.

## 6. Validation

Par construction, le rendement est le coût officiel prévu : le comparer au même chiffrage n'apprendrait rien. La validation compare donc ce que le modèle aurait affiché avec un millésime antérieur (coût prévu pour l'année en cours) au coût réalisé publié deux ans plus tard.

- Références : tableau « Dépenses fiscales par impôt » des tomes II des PLF 2025 et 2026 (`registres/references/chiffrages.yaml`, à relire).
- Tolérance : ±10 % (règle de publication, `CLAUDE.md`).
- Test : `moteur/tests/validation/test_levier_depenses_fiscales.py`.

| Référence | Millésime | Valeur de référence | Valeur du modèle | Écart | Dans la tolérance |
|-----------|-----------|---------------------|------------------|-------|-------------------|
| Impôt sur le revenu | réalisation 2023 (PLF 2025) ; prévision du PLF 2024 | 38 735 M€ | 38 337 M€ | -1,0 % | oui |
| Impôt sur le revenu et impôt sur les sociétés | idem | 13 977 M€ | 14 257 M€ | +2,0 % | oui |
| Impôt sur les sociétés | idem | 9 179 M€ | 9 108 M€ | -0,8 % | oui |
| Impôt sur le revenu | réalisation 2024 (PLF 2026) ; prévision du PLF 2025 | 42 079 M€ | 41 762 M€ | -0,8 % | oui |
| Impôt sur le revenu et impôt sur les sociétés | idem | 14 111 M€ | 14 106 M€ | -0,0 % | oui |
| Impôt sur les sociétés | idem | 3 913 M€ | 3 558 M€ | -9,1 % | oui |

À la prévision à un an (celle que le levier utilise), les écarts sont plus grands : impôt sur les sociétés -17 %, droits d'enregistrement +495 % (voir les plages).

**Source indépendante : Cour des comptes**, note d'analyse de l'exécution budgétaire 2024 sur les dépenses fiscales (avril 2025, `ccomptes_neb_2024_depenses_fiscales`, déposée par le mainteneur). La Cour retraite les données de l'administration fiscale : elle contrôle le chiffrage, elle ne le refait pas. Coût total de toutes les dépenses fiscales (nouvelle convention TVA), tableau page 18 :

| Référence (Cour des comptes) | Valeur de référence | Valeur du modèle (prévision du PLF 2024) | Écart | Dans la tolérance |
|------------------------------|---------------------|------------------------------------------|-------|-------------------|
| Coût révisé 2024 (PLF 2025) | 83,29 Md€ | 78,74 Md€ | -5,5 % | oui |
| Coût définitif 2023 (PLF 2025) | 82,92 Md€ | 81,34 Md€ | -1,9 % | oui |

Ce que la Cour ajoute :
- les montants des tomes II qu'elle cite (78,741, 81,344, 82,923, 83,292 et 85,616 Md€) sont ceux que l'extraction redonne ;
- le coût prévu est **systématiquement sous-estimé** : le coût définitif dépasse la prévision initiale chaque année depuis 2019, de 3,4 % en moyenne sur 2018-2023 (`depenses_fiscales_ccomptes_ecart_moyen_n_n2`, page 17) et de 6,75 % pour 2023 (prévision initiale du PLF 2023 : 77,676 Md€, page 18) ;
- la révision de 2024 (+4,55 Md€) vient de mesures nouvelles (0,85 Md€), de changements de méthode (1,95 Md€) et de l'évolution spontanée (1,76 Md€) (page 19) ;
- la méthode de chiffrage « suppose le comportement des agents économiques stable » (page 42), comme le modèle.

La valeur centrale du levier ne corrige pas ce biais (décision du mainteneur du 9 octobre 2026, option (a)) : il reste visible dans les fourchettes, orientées vers le haut, et sur cette fiche. Statut maintenu en bêta par le mainteneur.

## 7. Limites connues

- Le coût d'une dépense fiscale n'est pas le gain de sa suppression : le tome II (sous-partie V, méthodologie, page 37 du PLF 2026) précise que ses coûts sont « la conséquence immédiate et directe de la mesure concernée, sans effet comportemental », et que les interactions entre dépenses ne sont pas quantifiées.
- Le même passage ajoute que « la somme des coûts des dépenses fiscales est donc dépourvue de réelle signification ». Le curseur par impôt additionne pourtant ces coûts : son résultat est à lire comme un ordre de grandeur, et plusieurs dépenses choisies une à une s'additionnent de même.
- Les dépenses non chiffrables (« nc » sans montant antérieur dans le tome) ne sont pas proposées.
- Les dépenses d'impôt sur les sociétés interagissent avec le levier du taux normal de l'IS (une hausse du taux augmente le coût des dépenses) : non compté, les effets s'additionnent.
- Les dépenses fiscales sur les impôts locaux sont comptées dans le solde de l'ensemble des administrations publiques, sans distinguer qui en porte le coût.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-30 | Fiche descriptive de chaque dépense (finalité, bénéficiaires, création, dernière modification, mission et programme, texte de loi), extraite du tome II du PLF 2026 et affichée dans le simulateur ; recherche aussi sur la finalité | Aucun calcul ne change ; `depenses_fiscales.csv` inchangé ; 465 fiches lues, 434 avec finalité (les 31 autres n'en indiquent pas) ; 1 test du moteur et 1 du site ajoutés |
| 2026-10-09 | Création du levier (catalogue et impôts), extraction des trois tomes II | 6 nouvelles références de validation, toutes dans la tolérance ; tableau : 21 sur 29 |
| 2026-10-09 | Confrontation à la Cour des comptes (NEB 2024) : 2 références ajoutées, dans la tolérance ; tableau : 23 sur 31 | aucun calcul modifié |
| 2026-10-09 | Accises : remboursements des transporteurs, du transport collectif et des taxis repris du PLF 2026 (1 178, 183 et 59 M€ au lieu de 1 272, 183 et 50 M€) | aucun test de validation ; rendement d'un centime de gazole 0,225 → 0,232 Md€ |
