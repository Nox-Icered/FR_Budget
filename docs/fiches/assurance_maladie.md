---
levier: assurance_maladie
statut: beta
mise_a_jour: 2026-11-06
---

# Fiche : assurance maladie, première étape (leviers agrégés)

Lot V2 « assurance maladie ». Plan validé par le responsable du projet le 6 novembre 2026 :
- les trois leviers ci-dessous ;
- pour les franchises, l'option (i) : les montants et les plafonds bougent ensemble ;
- pour l'ONDAM, des bornes tirées de l'exécution passée.

Statut : **bêta, non validé**. Les chiffrages et l'hypothèse du § 5 sont **à relire**.

## 1. Question posée

Quel effet sur le solde public auraient :
- une progression de l'objectif national de dépenses d'assurance maladie (ONDAM) plus ou moins forte ;
- une variation des franchises médicales et des participations forfaitaires ;
- un relèvement du plafond du salaire pris en compte pour les indemnités journalières maladie ?

## 2. Sources

| Source | Usage |
|---|---|
| Annexes 5 des PLFSS pour 2024, 2025 et 2026 (« ONDAM et dépenses de santé ») | montants de l'ONDAM (objectif initial, constat), économies prévues, chiffrages des indemnités journalières |
| Commission des comptes de la sécurité sociale, mai 2024, fiche 3.3 | rendement 2022 et effet du doublement de 2024 (880 M€), tous régimes |
| Cour des comptes, rapport sur l'application des LFSS, mai 2026 | rendement constaté des franchises (2023-2025), projet de doublement de 2025 (2,3 Md€), indemnités journalières (0,4 Md€) |

Fichiers bruts dans `data/raw/assurance_maladie/`. Les montants sont saisis dans `registres/references/chiffrages.yaml`, avec leur page.

## 3. Leviers

Code : `moteur/src/fr_budget/agrege/assurance_maladie.py`.

**Progression de l'ONDAM** (`ondam_progression`, en points ; un point de plus augmente les dépenses)
- Un point vaut 1 % de l'ONDAM 2025 voté (265,9 Md€).
- Bornes de l'effet : part des économies prévues effectivement réalisées (hypothèse `ondam_realisation_economies`, § 5).
- Curseur : ±2,6 points, soit les mesures d'économies de la construction de 2026 (7,1 Md€) rapportées à l'ONDAM 2026.
- La loi fixe un objectif ; le levier ne dit pas comment l'atteindre.

**Franchises et participations forfaitaires** (`franchises_participations`, en % des montants unitaires et des plafonds journaliers et annuels, ensemble ; option (i))
- Un pour cent vaut 1 % du rendement 2025 de l'ensemble des régimes de base, soit 2,5 Md€ selon la Cour des comptes.
- Borne basse : le chiffrage du doublement des montants et des plafonds présenté en 2025 (2,3 Md€).
- Borne haute : le rendement en année pleine après la réforme de 2024 estimé par la CCSS (1 640 + 880 M€).
- Curseur : de −100 % (suppression) à +100 % (doublement).
- **Variante non retenue (ii)**, montants seuls avec plafonds annuels inchangés (forme de la réforme de 2024) : non linéaire. Doubler les montants n'a rapporté que +54 % (CCSS : +880 M€ sur 1 640 M€).

**Plafond des indemnités journalières** (`ij_plafond_smic`, en points de Smic au-dessus de 140 % du Smic, de 0 à 40)
- Relever le plafond à 1,8 Smic coûte l'économie de la baisse de 2025 en année pleine : économie de la première année plus montée en charge de 2026 (0,5 Md€).
- L'économie de la première année est chiffrée à 0,6 Md€ par le PLFSS pour 2025 et à 0,4 Md€ dans la LFSS pour 2025 selon la Cour. Valeur centrale : la moyenne ; bornes : les deux.
- L'effet est supposé proportionnel à l'écart de plafond, faute de répartition des salaires des personnes en arrêt entre 1,4 et 1,8 Smic.
- Première année : part de l'économie de 2025 dans l'économie en année pleine (environ la moitié), car seuls les arrêts commencés après l'entrée en vigueur sont concernés.
- Pas de baisse sous 1,4 Smic : aucun chiffrage.

**Double compte** : les franchises et les indemnités journalières font partie de l'ONDAM. Leur combinaison avec le levier ONDAM est refusée par le moteur et par le site.

**Ménages types** : sans effet calculé (raison affichée : la cascade ne décrit ni les dépenses de santé ni les arrêts de travail). **Dixièmes de niveau de vie** : non répartis.

## 4. Validation

Test : `moteur/tests/validation/test_levier_assurance_maladie.py`, tolérance ±10 %.

| Référence | Modèle | Référence | Écart |
|---|---|---|---|
| Doublement des montants et des plafonds des franchises (projet 2025, Cour des comptes) | 2,50 Md€ | 2,3 Md€ | +8,7 % (dans la tolérance) |
| Baisse du plafond des indemnités journalières, première année (PLFSS pour 2025) | 0,49 Md€ | 0,6 Md€ | −17,5 % (hors tolérance) |
| Même mesure, montant inclus dans la LFSS pour 2025 (Cour des comptes) | 0,49 Md€ | 0,4 Md€ | +23,7 % (hors tolérance) |

Les deux références des indemnités journalières diffèrent entre elles de 50 %, et le modèle se place entre les deux. L'ONDAM n'a pas de chiffrage de mesure à reproduire : un point vaut, par définition, 1 % de l'objectif voté.

Confrontation indépendante : la Cour des comptes constate +820 M€ en année pleine pour le doublement des montants de 2024, au régime général. La CCSS l'estimait à +880 M€, tous régimes. Le levier (option i) ne représente pas cette réforme, qui laissait les plafonds annuels inchangés ; l'écart n'est donc pas une validation du levier. Le levier reste en bêta.

## 5. Choix à relire

- **Hypothèse `ondam_realisation_economies`** : centrale 1 (objectif tenu) ; plage de 0,57 à 1,12.
  - Plage : un moins l'écart d'exécution rapporté aux économies prévues, en 2024 (dépassement de 1,5 Md€ pour 3,5 Md€ d'économies) et en 2025 (sous-exécution de 0,5 Md€ pour 4,3 Md€).
  - Les années 2020 à 2023 (crise sanitaire, inflation exceptionnelle) sont écartées.
  - **Écart au plan** : le plan prévoyait de rapporter les dépassements à l'ONDAM. Ils dépassent un point de progression (3,8 Md€ hors crise en 2023), d'où le rapport aux économies prévues.
- L'effet d'activité (multiplicateur, désactivé par défaut) prend la catégorie « prestations » pour les trois leviers.
- Les bornes des curseurs.
- L'effet proportionnel du plafond des indemnités journalières.
