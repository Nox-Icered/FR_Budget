---
levier: impot_revenu_structure
statut: beta
mise_a_jour: 2026-11-09
---

# Fiche : effet du quotient familial et du quotient conjugal

Troisième étape du lot impôt sur le revenu (structure). Plan validé le 9 novembre 2026 : deux leviers agrégés, en bêta. Code : `moteur/src/fr_budget/agrege/quotients_ir.py`.

## 1. Question posée

Combien rapporterait la suppression de tout ou partie de la baisse d'impôt due :
- **au quotient familial** : les parts des enfants et des autres personnes à charge, ainsi que les autres dispositifs liés aux personnes à charge ;
- **au quotient conjugal** : l'imposition commune des couples mariés ou pacsés. Le supprimer revient à imposer chaque membre du couple seul.

## 2. Sources

| Source | Contenu | Année de législation |
|---|---|---|
| Insee, *Économie et Statistique* n° 526-527 (2021), André et Sireyjol, tableau 2, page 29 | impôt individuel 93,7 Md€, conjugal 82,6 Md€, réel 66,0 Md€ (Ines, France métropolitaine, ménages ordinaires) | 2017 |
| Insee Analyses n° 53 (juin 2020), figure 1 | familialisation 19,0 Md€, conjugalisation 10,8 Md€ | 2018 |
| Même numéro d'*Économie et Statistique*, Allègre, Périvier et Pucci (OFCE, Université Paris 1), tableau 2, page 13 | individualisation avec répartition au mieux des parts des enfants : +7,2 Md€ | 2016 |

Fichiers : `data/raw/impot_revenu/insee_economie_statistique_526_527_2021.pdf`, `data/raw/impot_revenu/insee_analyses_53_2020.html`.

## 3. Leviers

Les deux curseurs vont de 0 à 100 % de l'effet supprimé. Effet positif sur le solde (recettes en plus).

| Levier | 1 % de l'effet | Effet total (100 %) | Fourchette d'un point |
|---|---|---|---|
| `ir_quotient_familial_effet` | 0,217 Md€ | 21,7 Md€ | de 0,217 à 0,241 Md€ (Insee 2017, Insee 2018) |
| `ir_quotient_conjugal_effet` | 0,145 Md€ | 14,5 Md€ | de 0,096 à 0,145 Md€ (Insee 2017, Insee 2018, OFCE 2016) |

- **Valeur centrale** : écart de l'Insee pour 2017 (16,6 et 11,1 Md€), porté en euros de 2025 par le PIB nominal, comme le plafond du quotient familial.
- **Effet proportionnel au curseur.** Une suppression partielle n'a pas de chiffrage officiel : la vraie réponse n'est pas linéaire.
- **Ordre des effets.** L'Insee mesure le quotient conjugal sans les dispositifs familiaux, puis le quotient familial après le quotient conjugal. Les deux leviers à 100 % redonnent donc l'écart total (27,7 Md€ en 2017). En revanche, le quotient conjugal supprimé seul, dispositifs familiaux maintenus, n'est pas chiffré par la source.
- **Double compte.** Le levier sur l'effet du quotient familial est refusé avec le levier sur son plafond.
- **Interactions non chiffrées.** Les deux leviers sont ajoutés aux interactions signalées avec le barème et avec la CSG.
- **Ménages types** (calcul OpenFisca, `docs/fiches/menages_types.md`, choix 53).
  - Quotient familial : l'impôt après plafonnement (`ir_plaf_qf`) est rapproché, de x % de l'écart, de l'impôt calculé sur les seules parts des adultes (`ir_ss_qf`).
  - Quotient conjugal : pour un couple, l'impôt commun est rapproché, de x % de l'écart, de la somme des impôts des deux membres déclarant seuls. Les enfants sont rattachés à celui qui a le revenu le plus élevé.
  - L'effet sur l'impôt d'un ménage n'est pas proportionnel au curseur (décote, tranches), contrairement au levier national.
- **Dixièmes.** Pas de répartition.
- **Comportements.** Aucun : pas de changement de déclaration ni de statut marital.

## 4. Validation

Tests : `moteur/tests/validation/test_levier_quotients_ir.py` et `test_confrontations_independantes.py`, tolérance ±10 %.

| Référence | Modèle | Référence | Écart |
|---|---|---|---|
| Composante familiale 2018 (Insee Analyses n° 53) | 17,1 Md€ | 19,0 Md€ | −10,2 % (hors tolérance) |
| Composante conjugale 2018 (Insee Analyses n° 53) | 11,4 Md€ | 10,8 Md€ | +5,6 % (dans la tolérance) |
| Individualisation avec répartition des enfants, 2016 (OFCE, source indépendante) | 10,8 Md€ | 7,2 Md€ | +50,1 % (hors tolérance) |

Lecture :
- **Une seule équipe.** Les deux millésimes de l'Insee viennent de la même équipe et du même modèle (Ines). Ils ne sont pas indépendants entre eux.
- **Écart avec l'OFCE.** L'OFCE simule une autre réforme : les parents se partagent au mieux les parts des enfants, ce qui réduit le gain. Il donne aussi « environ 10 milliards » sans cette répartition (annexe en ligne C7, non téléchargée), proche du modèle.
- **Chiffres de la Cour des comptes (2023) et de l'IGF-IGAS (2026).** Ils reprennent l'estimation de l'Insee pour 2017 : ce ne sont pas des recoupements.

Les deux leviers restent en bêta.

## 5. Recoupement par le moteur du barème (non concluant)

`recoupement_bareme_qf` recalcule l'impôt de 2024 en ne gardant que les parts des adultes, avec l'avantage plafonné par demi-part :
- avec la part des couples par quantile de la DGFiP : 7,2 Md€ ;
- avec une part des couples uniforme (32 %) : 14,4 Md€ ;
- le levier donne 21,3 Md€ la même année.

Pourquoi le moteur ne permet pas de conclure :
- **Parts des enfants mal estimées.** Le moteur ne connaît que les parts moyennes par dixième de revenu par part. Dans les dixièmes du haut, le nombre de parts au-delà des adultes devient négatif avec la part des couples par quantile, et il est ramené à zéro.
- **Dispositifs non recalculés.** Le moteur ne recalcule ni les autres dispositifs familiaux, ni la demi-part des parents isolés (plafond plus élevé).

Cet écart est publié. Il ne sert pas de référence.

## 6. Choix à relire

- **Valeur centrale** prise sur 2017 (article détaillé, à comité de lecture) plutôt que sur 2018 (note courte).
- **Conversion en euros de 2025** par le PIB nominal (+28 % de 2017 à 2025), comme le plafond du quotient familial. L'impôt sur le revenu n'a pas suivi exactement le PIB.
- **Champ de l'Insee** : France métropolitaine, ménages ordinaires. L'impôt simulé (66 Md€) est plus faible que l'impôt total : l'effet est sans doute un peu sous-estimé.
- **Borne basse du quotient conjugal** : la réforme de l'OFCE (avec répartition des enfants).
- **Proportionnalité au curseur.**
