---
levier: retraites
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : retraites, première étape (âge effectif moyen de départ)

Lot 3.1 du plan (phase 3). Ce lot a été fait en autonomie (instruction du mainteneur du 12 octobre 2026). Les choix du § 5 et les 7 valeurs saisies sont **à relire**.

## 1. Question posée

Que changent pour le solde et la dette des départs à la retraite plus tardifs (ou plus précoces) de x années en moyenne, par rapport à la projection du COR à législation inchangée ?

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur de référence | Plage proposée sur le site | Source |
|-----------|---------------------|----------------------------|--------|
| Âge effectif moyen de départ, en écart à la projection du COR | 63,1 ans en 2025, 64,6 ans en 2070 (projection à législation inchangée) | de −1 à +3 ans, par pas de 0,25 | COR, rapport annuel de juin 2026, figure 2.24 |

La borne haute (+3 ans) est le relèvement qui équilibrerait le système de retraite en 2070 selon le COR (67,6 ans au lieu de 64,6 ans).

## 3. Méthode de calcul

Moteur : `moteur/src/fr_budget/retraites.py`. Données : `pipelines/retraites/extraire_cor.py`, qui produit `data/processed/retraites/cor_2026_reference.csv`.

- **Effet d'un an, année par année.** La figure 2.24 du COR donne, pour chaque année jusqu'en 2070, trois façons de rétablir seul l'équilibre du système : un âge de départ plus élevé (Δa), une pension moyenne relative plus basse (Δp) ou un taux de prélèvement plus haut (Δτ). Ces trois ajustements ont le même effet sur le solde. L'effet d'un an d'âge s'en déduit de deux façons :
  - voie « pension » : dépenses × Δp / p, divisé par Δa ;
  - voie « prélèvement » : ressources × Δτ / τ, divisé par Δa. Elle égale exactement le déficit publié par le COR.

  Les dépenses et les ressources viennent des figures 2.2 et 2.8, en part du PIB. La valeur centrale est la moyenne des deux voies, et les bornes sont les deux voies.

  Résultat : environ 0,82 point de PIB pour un an en 2030, 0,84 en 2036 et 0,78 en 2046. Avant 2032, l'écart d'âge qui équilibre le système est petit (moins de 0,4 an) et les deux voies s'écartent : jusqu'à 0,90 et 1,55 point en 2026.
- **Montée en charge.** L'écart choisi est atteint de façon linéaire en 4 ans, ce qui correspond au rythme de la réforme de 2023 pour un an : trois mois par génération (COR, page 206).
- **Effet dans le scénario.** L'écart de solde primaire s'ajoute chaque année à la baseline, comme pour les autres leviers. La baseline (RESF puis projection du projet) n'est pas celle du COR : le module ne reprend du COR que l'effet d'un an d'âge.

## 4. Données

| Jeu de données | Ce qu'il apporte |
|----------------|------------------|
| `cor_ra2026_donnees_partie2_xlsx` | figures 2.2, 2.8 et 2.24 (scénario de référence, de 2025 à 2070) |
| `cor_ra2026_pdf` | tableau 2.10 (validation), rythme de la réforme de 2023 (page 206) |

Les 6 valeurs du tableau 2.10 saisies dans `registres/references/chiffrages.yaml` et l'hypothèse `retraites_duree_montee_en_charge` sont à relire.

## 5. Choix faits en autonomie, et leurs limites

1. **Première étape, pas de modèle de cohortes.** La spécification prévoit un modèle de cohortes avec la démographie de l'INSEE. Il n'est pas construit : cette étape reprend le calcul « mécanique » du COR (son abaque).
   - Limite : seul l'âge moyen de départ est réglable. L'âge légal, la durée de cotisation, le taux de remplacement et les régimes ne le sont pas.
   - L'indexation des pensions passe déjà par le curseur de revalorisation (lot 2.8), et les prélèvements par ceux de la CSG et des cotisations. La pension relative et le taux de prélèvement du COR ne sont donc pas proposés, pour éviter les doubles comptes.
2. **Âge effectif, pas âge légal.** Le levier porte sur l'âge moyen auquel les gens partent. Un an de plus sur l'âge légal relève moins l'âge effectif (départs anticipés, invalidité, chômage), d'un montant qu'aucune source saisie ne donne.
3. **Calcul mécanique.** Comme le COR le précise (page 124), ce calcul ne compte pas les interactions entre leviers (pensions plus élevées après des carrières plus longues), les effets sur l'emploi et l'activité, ni les dépenses d'autres risques (chômage, invalidité, minima sociaux).
4. **Montée en charge en 4 ans quelle que soit l'ampleur.** Pour que le calcul reste linéaire (site statique), la durée ne dépend pas de l'écart choisi. Un relèvement de 3 ans monte donc à 9 mois par an, trois fois plus vite que la réforme de 2023.
5. **Pas de multiplicateur de demande.** L'interrupteur de croissance (lot 3.2) ne s'applique pas à ce levier : le relèvement de l'âge agit sur l'offre de travail, et le modèle de l'OFCE ne le représente pas. Les simulations citées par le COR lui prêtent un effet positif sur le PIB (de +0,1 à +0,8 %).
6. **Bornes.** La borne de +3 ans est l'écart d'équilibre de 2070 selon le COR. La borne de −1 an est un choix, sans source.

## 6. Validation

Test : `moteur/tests/validation/test_levier_retraites.py`. Tolérance : ±10 %.

La référence est le tableau 2.10 du COR (page 123) : l'effet d'un an de plus sur l'âge d'ouverture des droits sur le solde primaire des APU, selon les simulations de la DG Trésor, d'I-MIP et de l'OFCE. Le modèle est comparé à chaque borne de la fourchette publiée.

| Référence | Référence | Modèle | Écart | Dans la tolérance |
|-----------|----------:|-------:|------:|-------------------|
| À 10 ans, borne basse | 0,30 | 0,84 | +179,7 % | non |
| À 10 ans, borne haute | 0,60 | 0,84 | +39,9 % | non |
| À 20 ans, borne basse | 0,30 | 0,78 | +161,3 % | non |
| À 20 ans, borne haute | 0,65 | 0,78 | +20,6 % | non |

Lecture : le modèle donne un effet plus fort que les trois modèles cités par le COR, même à leur borne haute. Les raisons probables sont celles du § 5 :
- l'âge effectif monte moins que l'âge légal ;
- les pensions augmentent avec des carrières plus longues ;
- d'autres dépenses sociales augmentent.

Les simulations du COR comptent en revanche des recettes supplémentaires dues à l'emploi, qui jouent dans l'autre sens. L'écart est publié tel quel, et le module reste en bêta. Aucune source indépendante (Cour des comptes) n'est encore confrontée.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-12 | Création du module (première étape) | 4 nouvelles références de validation, toutes hors tolérance ; tableau : 49 sur 70 |
