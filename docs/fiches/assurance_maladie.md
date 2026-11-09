---
levier: assurance_maladie
statut: beta
mise_a_jour: 2026-11-09
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

## 6. Deuxième étape : ticket modérateur (plan validé le 9 novembre 2026, option a)

Le ticket modérateur est la part du tarif que l'assurance maladie ne rembourse pas. Deux leviers bêta, en points, de −10 à +10 (positif : hausse de la part non remboursée, donc économie). Le domaine est celui des deux hausses de 10 points chiffrées.

| Levier | Un point | Base du chiffrage | Fourchette d'un point |
|---|---|---|---|
| `ticket_moderateur_consultations` (médecins et sages-femmes, 30 % aujourd'hui) | 0,110 Md€ | Hausse de 30 % à 40 % prévue pour 2025 : 1,0 Md€ en ville et 0,1 Md€ dans les établissements (annexe 5 du PLFSS pour 2025, pages 8 et 9). Les taux viennent du Sénat (commission des affaires sociales, 13 novembre 2024) | de 0,063 à 0,123 Md€ : part des économies prévues réalisées (`ondam_realisation_economies`) |
| `ticket_moderateur_dentaire` (40 % depuis le 15 octobre 2023) | 0,043 Md€ | Hausse de 30 % à 40 % du 15 octobre 2023 : 525 M€ économisés jusqu'à fin 2024 (Cour des comptes, mai 2026, page 216), ramenés à un an (14,6 mois) | de 0,031 à 0,043 Md€ : la borne basse vient de la hausse de 2 points de la part des complémentaires, sur 15,7 Md€ de soins dentaires en 2024 (7,4 Md€ payés par les complémentaires, 47 %), même page |

- **Effet linéaire.** Même rendement par point dans les deux sens, sans changement de comportement.
- **Qui paie.** L'économie pour l'assurance maladie est surtout payée par les complémentaires santé, donc par leurs cotisations, et par les patients sans complémentaire. Cet effet n'est pas calculé.
- **Euros.** Montants en euros de l'année du chiffrage (2025 pour les consultations, 2023-2024 pour le dentaire), sans conversion, comme pour les franchises.
- **Double compte.** La combinaison avec le levier ONDAM est refusée.
- **Ménages types et dixièmes.** Comme pour les autres leviers d'assurance maladie : pas d'effet calculé, pas de répartition.

### Validation

| Référence | Modèle | Référence | Écart |
|---|---|---|---|
| Hausse de 10 points sur les consultations (avis n° 130 du Sénat sur le PLFSS 2025, page 38) | 1,10 Md€ | 1,1 Md€ | 0 % (calage) |
| Hausse de 10 points sur les soins dentaires, d'octobre 2023 à fin 2024 (Cour des comptes) | 525 M€ | 525 M€ | 0 % (calage) |

Les deux leviers restent en bêta :
- **Consultations.** Le chiffre du Sénat reprend celui du gouvernement : ce n'est pas une source indépendante. La mesure n'a pas été appliquée, donc il n'existe pas de constat. Il n'y a qu'un seul millésime.
- **Soins dentaires.** Le constat de la Cour des comptes est une source indépendante. En revanche, le chiffrage officiel avant la mesure est introuvable : l'annexe 5 du PLFSS pour 2023 n'en parle pas, et celle de 2024 l'inclut dans un total. La seconde lecture tirée de la Cour (part des complémentaires) donne 27 % de moins que le constat.

### Choix à relire

- **Fourchette des consultations.** Elle applique au chiffrage la part des économies réalisées sur l'ensemble de l'ONDAM (2024 et 2025). C'est une hypothèse : rien ne dit que cette mesure aurait été réalisée comme la moyenne.
- **Fourchette du dentaire.**
  - Pas de borne haute sourcée au-delà du constat.
  - Le passage de 2 points de part à une économie suppose que le reste de la part n'ait pas bougé à cause de la mesure. Le chiffre est arrondi par la Cour.
- **Durée du constat.** Du 15 octobre 2023 au 31 décembre 2024 : 444 jours, soit 14,6 mois.
- **Bornes de ±10 points.** C'est le seul domaine chiffré.
- **Hausse retirée.** La hausse sur les consultations a été réduite puis retirée pendant le débat de 2025. Ce retrait n'est documenté que par la presse, qui n'est pas utilisée ici.
