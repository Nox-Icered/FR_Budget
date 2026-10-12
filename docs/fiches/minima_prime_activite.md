---
levier: minima_prime_activite
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : prime d'activité (part des revenus d'activité prise en compte)

Lot 2.12 du plan (phase 2). Décision du mainteneur du 12 octobre 2026 : « levier calé pour la prime d'activité ». Les autres choix du § 5 sont **à relire**.

## 1. Question posée

Que change pour le solde et la dette une variation de x points de la part des revenus d'activité prise en compte dans le calcul de la prime d'activité (la « pente ») ? Exemple : « baisse d'un point de la pente », comme la baisse de 1,15 point du 1er avril 2025.

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source |
|-----------|-----------------|----------------------------|--------|
| Part des revenus professionnels prise en compte | 59,85 % depuis le 1er avril 2025 | de -5 à +5 points, par pas de 0,1 | OpenFisca (`ppa.pa_m.majoration_ressources_revenus_activite`) ; décret n° 2025-292 |

Le levier ne peut pas être combiné avec les crédits de la mission « Solidarité, insertion et égalité des chances », qui finance la prime d'activité (même règle que pour l'indexation).

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/prime_activite.py`, levier dans `scenario.py`).
- **Calage.** Selon l'administration, la baisse de 1,15 point de 2025 rapporte « jusqu'à 500 millions d'euros en année pleine » (note de présentation du Sénat, page 15). Un point vaut donc **0,43 Md€** par an.
- **Borne basse.** Elle applique le rapport entre les crédits de prime d'activité prévus pour 2026 (9,3 Md€) et la dépense de 2024 (10,5 Md€), pour une prime plus réduite après les mesures de 2025 et 2026 : **0,39 Md€**.
- **Effet dans le scénario** : moins le coût en année pleine, en Md€, rapporté au PIB 2025 et tenu constant en points de PIB.

## 4. Données

| Jeu de données | Ce qu'il apporte |
|----------------|------------------|
| `senat_note_presentation_siec_plf2026_pdf` | baisse de 1,15 point et son rendement en année pleine (500 M€) ; dépense de 2024 (10,5 Md€) ; crédits de 2026 (9,3 Md€) |
| `senat_rapport_special_siec_plf2026_pdf` | moindre dépense constatée en 2025 (290 M€, page 55) |

Les valeurs, saisies dans `registres/references/chiffrages.yaml`, sont à relire.

## 5. Choix et limites

1. **Levier calé** (décision du mainteneur). Il n'existe pas de données publiques sur les revenus des allocataires : les micro-données d'enquête ne sont pas publiables et je n'ai pas trouvé d'agrégats de la CNAF. Le rendement reprend donc le seul chiffrage de l'administration.
2. **Linéarité** : chaque point vaut le même montant, à la hausse comme à la baisse. Une forte baisse ferait sortir des foyers de la prime ; l'effet réel n'est pas linéaire.
3. **Bornes de ±5 points** : choix sans source, à partir du repère de 2025.
4. **RSA et montants forfaitaires** : non proposés ici. Leur revalorisation est couverte par le curseur d'indexation (lot 2.8) ; un curseur sur le montant du RSA demanderait les mêmes données manquantes.
5. **Aucun effet de comportement** sur l'emploi.

## 6. Validation

Test : `moteur/tests/validation/test_levier_prime_activite.py`. Tolérance : ±10 %.

| Référence | Millésime | Référence | Modèle | Écart | Dans la tolérance |
|-----------|-----------|----------:|-------:|------:|-------------------|
| Moindre dépense en 2025 de la baisse de 1,15 point (avril à décembre) | 2025 (rapport spécial du Sénat) | 290 M€ | 375 M€ | **+29,3 %** | non |

Lecture :
- Le chiffrage en année pleine de l'administration (500 M€), appliqué aux neuf mois d'avril à décembre, surestime de 29 % la moindre dépense constatée en 2025.
- Explications possibles, non chiffrées :
  - montée en charge (les droits se recalculent chaque trimestre) ;
  - décalage d'un mois entre droit et versement ;
  - chiffrage « jusqu'à » 500 M€, donc maximal.
- Ce n'est pas une validation indépendante : même mesure, autre mesure de son effet.
- Aucune source indépendante. Le levier reste en bêta.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-12 | Création du levier calé | 1 nouvelle référence, hors tolérance (+29,3 %) ; tableau : 49 sur 66 (avec la référence AAH du lot 2.8) |
