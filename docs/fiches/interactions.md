---
module: interactions
statut: beta
mise_a_jour: 2026-11-06
---

# Fiche : combinaison de mesures sans double compte

Statut : bêta, non validé (pas de chiffrage officiel d'une combinaison à reproduire). Plan validé par le responsable du projet le 6 novembre 2026 : option A (termes croisés mécaniques chiffrés), avertissement seul pour les interactions non chiffrées.

## 1. Ce qui est refusé (double compte au sens strict)

Le moteur (`scenario.verifier_double_compte`) et le site refusent :
- deux mesures sur un même levier ;
- une dépense fiscale avec tout son impôt ;
- les rémunérations ou l'indexation avec la mission qui les finance ;
- le barème de l'impôt sur le revenu avec la revalorisation de ses seuils ;
- l'âge effectif avec l'âge légal de départ.

## 2. Termes croisés chiffrés

Quand une mesure change l'assiette d'un prélèvement que modifie une autre mesure, le prélèvement supplémentaire sur l'assiette supplémentaire s'ajoute au total. Le terme est proportionnel au produit des deux réglages et nul si l'un d'eux est nul. Aucune élasticité ni valeur nouvelle : seulement des assiettes et des taux déjà utilisés par les deux leviers (`moteur/src/fr_budget/agrege/interactions.py`).

| Paire | Terme pour une unité de chaque levier | Données |
|---|---|---|
| Point d'indice (1 %) × CSG sur les revenus d'activité (1 point) | 1 % du coût brut de chaque versant × assiette de CSG ajoutée par euro de coût × 1 point | coût brut du levier (Insee, DGAFP, OpenFisca) ; CSG du fonctionnaire moyen (OpenFisca) ; taux de CSG de 2025 (CCSS) |
| Effectifs (1 %) × CSG sur les revenus d'activité (1 point) | même calcul, sur l'agent entier | mêmes données |
| Revalorisation des pensions et prestations (1 point) × taux plein de CSG sur les pensions (1 point) | 1 % des pensions du levier d'indexation × part de la masse des pensions au taux plein × 1 point | DREES (comptes de la protection sociale 2025, EIR 2020) ; OpenFisca |

Fourchette :
- rémunérations : catégories A, B et C, comme le coût net du levier ;
- pensions : législations de 2020 et de 2025, personne seule ou couple, comme le rendement du levier CSG sur les retraites.

Calendrier : comme les deux leviers, à partir de la plus tardive des deux années d'entrée. Pour les pensions, la première année compte les mois qui suivent la revalorisation des pensions.

Effet d'activité (multiplicateur, interrupteur désactivé par défaut) : celui de la CSG.

Ordre de grandeur, aux bornes des curseurs :
- 5 % de point d'indice × 2 points de CSG : environ 0,19 Md€ ;
- 5 % d'effectifs × 2 points de CSG : environ 0,25 Md€ ;
- 2 points de revalorisation × 2 points de CSG retraites : environ 0,1 Md€.

## 3. Interactions non chiffrées (avertissement)

Le site les signale quand les deux mesures sont réglées. La combinaison n'est pas refusée et les deux effets s'additionnent.

| Mécanisme | Leviers | Ce qui manque pour chiffrer |
|---|---|---|
| L'accise entre dans le prix soumis à la TVA | accises × TVA | part des volumes de carburant achetée sans TVA déductible |
| La CSG déductible réduit le revenu imposable | CSG × leviers de l'impôt sur le revenu | revenu imposable par tranche du barème |
| Les cotisations des employeurs sont déductibles du bénéfice | cotisations, allègements, contribution chômage × impôt sur les sociétés | part des cotisations qui réduit le bénéfice imposable (incidence) |
| Le plafonnement du quotient familial dépend du barème | seuils ou barème × plafond du quotient familial | foyers plafonnés par tranche |
| L'âge de départ change pensions, cotisants et chômage | âge de départ × indexation, CSG retraites, chômage | effet du COR séparé entre pensions et cotisations |

Paires sans interaction par construction : taux de cotisation × allègements généraux. Le levier taux est hors du champ des allègements, selon la convention de la CCSS.

## 4. Limites

- Les effets propres de chaque levier ne changent pas. En particulier, le rendement de la CSG reste brut de son effet sur l'impôt sur le revenu, comme dans les chiffrages de la CCSS.
- Les ménages types additionnent l'effet de chaque mesure, calculé séparément ; les interactions au niveau d'un ménage ne sont pas comptées.
- Les interactions entre plus de deux mesures ne sont pas comptées : elles sont d'un ordre de grandeur encore inférieur.
