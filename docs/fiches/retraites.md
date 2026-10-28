---
levier: retraites
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : retraites (âge effectif moyen de départ ; âge légal, modèle par cohortes)

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
- **Montée en charge.** L'écart choisi est atteint de façon linéaire en 4 ans, ce qui correspond au rythme de la réforme de 2023 pour un an : trois mois par génération (COR, page 206). Plage de 4 à 4,9 ans depuis le 28 octobre 2026 : après la réforme de 2010, l'âge conjoncturel de départ observé a gagné 1,63 an de 2010 à 2017 et 1,82 an de 2010 à 2019 (COR, figure 2.5), soit 4,3 à 4,9 ans par an d'âge effectif (`docs/validation/plages_nulles.md`, § 3). Les bornes de l'effet croisent celles de l'effet d'un an et celles de cette durée.
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

Test : `moteur/tests/validation/test_levier_retraites.py`.

La référence est le tableau 2.10 du COR (page 123) : l'effet d'un an de plus sur l'âge d'ouverture des droits sur le solde primaire des APU, selon les simulations de la DG Trésor, d'I-MIP et de l'OFCE (court terme à 2 ans, moyen terme à 10 ans, long terme à 20 ans). C'est une fourchette de trois modèles, pas un chiffrage unique.

**Règle** (décision du mainteneur du 28 octobre 2026) : le modèle passe s'il est dans [0,9 × borne basse ; 1,1 × borne haute]. L'écart affiché est nul dans la fourchette, et mesuré à la borne la plus proche en dehors (`fr_budget.validation.comparer_fourchette`). Elle remplace la comparaison à chaque borne à ±10 %, qu'aucun modèle ne pouvait satisfaire aux deux bornes à la fois (les bornes basse et haute sont éloignées de bien plus de 20 %). Limite : la règle est moins exigeante qu'un chiffrage unique ; une fourchette large (0,05 à 0,4 à 2 ans) laisse passer des modèles très différents.

| Horizon | Fourchette du COR | Modèle | Écart à la fourchette | Dans la tolérance |
|---------|------------------:|-------:|----------------------:|-------------------|
| 2 ans | 0,05 à 0,40 | 0,48 | +20,0 % | non |
| 10 ans | 0,30 à 0,60 | 0,84 | +39,9 % | non |
| 20 ans | 0,30 à 0,65 | 0,78 | +20,6 % | non |

Lecture : le modèle donne un effet plus fort que les trois modèles cités par le COR, même à leur borne haute. Les raisons probables sont celles du § 5 :
- l'âge effectif monte moins que l'âge légal ;
- les pensions augmentent avec des carrières plus longues ;
- d'autres dépenses sociales augmentent.

Les simulations du COR comptent en revanche des recettes supplémentaires dues à l'emploi, qui jouent dans l'autre sens. L'écart est publié tel quel, et le module reste en bêta. Aucune source indépendante (Cour des comptes) n'est encore confrontée.

## 8. Deuxième étape : âge légal d'ouverture des droits, modèle par cohortes

Lot du 14 octobre 2026, fait en autonomie (« finir la V1 ») ; choix et 3 hypothèses **à relire**. Levier `retraites_age_legal` (de −1 à +3 ans), à côté du levier sur l'âge effectif : les deux ne se cumulent pas (double compte refusé par le moteur et bloqué sur le site). Code : `moteur/src/fr_budget/retraites_cohortes.py` ; pipeline : `pipelines/retraites/extraire_cohortes.py`.

### Méthode

Pour chaque année t et chaque âge a, la génération g = t − a part plus tard de s(g) : le relèvement choisi, atteint au rythme de la réforme de 2023 quelle que soit son ampleur (trois mois par génération, hypothèse `retraites_duree_montee_en_charge`), à partir de la première génération qui atteint l'âge légal l'année d'entrée en vigueur (DREES, fiche 14). Un relèvement de trois ans prend donc douze générations.

- **Retraités en moins** : population de l'âge (Insee, projections 2021, scénario central) × écart entre le taux de retraités de 2023 à cet âge (DREES, fiche 15) et ce taux décalé de s(g), sans dépasser le taux de référence, et sans décalage à partir de l'âge d'annulation de la décote (67 ans, inchangé) ; × (1 − part des départs non décalés : ex-invalidité, handicap, inaptitude ; hypothèse `retraites_part_departs_non_decales`, DREES fiche 17).
- **Moindres pensions** : retraités en moins ÷ retraités de l'année × dépenses de retraite du COR (part du PIB, scénario de référence de juin 2026) × (1 + écart de pension des nouveaux retraités ; hypothèse `retraites_ecart_pension_liquidants`, DREES fiche 7) × (1 − prélèvements que la pension aurait rapportés : CSG, CRDS, CASA et impôt sur le revenu, taux moyen calculé avec OpenFisca sur la distribution des pensions de l'EIR 2020, `fr_budget.agrege.indexation.prelevements_moyens_pension` ; 11,5 % pour une personne seule, 14,0 % pour un couple, valeur centrale à mi-chemin).
- **Recettes** : retraités en moins × part en emploi l'année précédant la liquidation (hypothèse `retraites_part_emploi_avant_liquidation`, DREES fiche 20) × prélèvements sur un salaire médian (coût employeur moins revenu après impôt, OpenFisca, 2025) ÷ PIB ; ces prélèvements suivent le PIB par personne de 20 à 64 ans.
- **Fourchette** : combinaison des bornes des trois hypothèses et des deux foyers (prélèvements sur la pension) qui donne l'effet le plus faible et le plus fort.
- **Site** : l'effet n'étant pas proportionnel au relèvement, le site lit la réponse exacte de chaque cran du curseur (16 crans de trois mois, `scenario.grille_levier`, environ 2,2 Mo de données en plus avant compression) ; une valeur hors de ces crans est refusée.

### Résultats et validation

Un an de plus sur l'âge légal, entrée en 2027 : environ 418 000 retraités de moins la deuxième année, 627 000 la dixième. Effet sur le solde primaire, en points de PIB (central, fourchette) : 0,47 (0,42 à 0,56) à 2 ans, 0,66 (0,59 à 0,79) à 10 ans, 0,62 (0,56 à 0,75) à 20 ans. Une fois la montée en charge achevée : 18,9 Md€ de 2025 (17,2 à 22,8).

Comparé au tableau 2.10 du COR (mêmes références que la première étape, test `moteur/tests/validation/test_levier_retraites_cohortes.py`), même règle (fourchette, § 6) : +16,4 % au-dessus de la borne haute à 2 ans (première étape : +20,0 %), +9,4 % à 10 ans (+39,9 %), dans la fourchette à 20 ans (0,62 pour 0,30 à 0,65 ; première étape : +20,6 %). Deux comparaisons sur trois sont dans la tolérance (10 et 20 ans). Les deux modèles sont publiés sur la page Validation.

### Choix et limites

1. **Profil de départs de 2023.** Le taux de retraités par âge de 2023 sert pour toutes les années ; seul son décalage compte. Les générations suivantes partent plus tard (réforme de 2023), ce que le profil ne suit pas.
2. **Législation de l'édition 2025 de la DREES.** Les âges légaux par génération ne tiennent pas compte de la suspension de la réforme de 2023 votée en LFSS 2026 (aucune source déposée ne la détaille par génération).
3. **Population** : projections de l'Insee de 2021 ; une édition 2026 est publiée (Insee Première n° 2108), sans tableaux détaillés par âge trouvés.
4. **Non comptés** : prestations des personnes décalées sans emploi (chômage, invalidité, minima ; un tiers d'entre elles selon la fiche 20), pensions plus élevées après des carrières plus longues, effets sur l'emploi et l'activité. Les deux premiers réduiraient l'effet ; c'est la raison probable de l'écart au COR.
5. **Salaire médian.** Les prélèvements sont ceux d'un célibataire au salaire médian ; les seniors en emploi ont des salaires différents.
6. **Revue de la PR (Codex).** Deux corrections : rythme de trois mois par génération quelle que soit l'ampleur (au lieu d'une montée en quatre ans pour toute valeur), et économie sur les pensions nette des prélèvements qu'elles auraient rapportés (le taux moyen, et non marginal, sert ici : c'est toute la pension qui n'est pas versée).

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-28 | Plage de la durée de montée en charge (levier sur l'âge effectif) : 4 à 4,9 ans, à la demande du mainteneur ; le modèle par cohortes garde la valeur centrale (rythme légal) | Validation inchangée (valeur centrale). Un an d'âge effectif en 2027, borne basse de l'écart de solde : 2027 0,230 → 0,187 ; 2028 0,460 → 0,375 ; 2030 0,737 → 0,602 ; 2046 inchangée (0,768). Borne haute de l'écart de dette : 2030 −1,949 → −1,591 ; 2046 −14,891 → −14,508. Centrales et autres bornes inchangées. 1 test unitaire ajouté |
| 2026-10-28 | Règle de validation : modèle dans [0,9 × borne basse ; 1,1 × borne haute] du tableau 2.10 du COR, au lieu de ±10 % à chaque borne (décision du mainteneur, lot C de la revue de code) | Les 12 comparaisons (6 par modèle) deviennent 6 (3 par modèle). Âge effectif : 0 sur 6 → 0 sur 3 (écarts inchangés : +20,0 %, +39,9 %, +20,6 %). Cohortes : 2 sur 6 → 2 sur 3 (2 ans +16,4 %, hors ; 10 ans +9,4 % ; 20 ans −4,9 % → 0,0 %). Tableau : 59 sur 91 → 59 sur 85 |
| 2026-10-14 | Revue de la PR : rythme de trois mois par génération, pensions nettes des prélèvements, réponses exactes par cran sur le site | Variante « cohortes » : 2 sur 6 dans la tolérance (10 ans : +18,5 % → +9,4 % ; 20 ans : +2,8 % → −4,9 % ; 2 ans : +26,6 % → +16,4 %) |
| 2026-10-14 | Deuxième étape : levier sur l'âge légal, modèle par cohortes (§ 8) | 6 comparaisons de la variante « cohortes » au tableau 2.10 du COR, 1 dans la tolérance ; références et première étape inchangées |
| 2026-10-12 | Revue de la PR : références à 2 ans ajoutées à la validation | 2 nouvelles références, hors tolérance ; tableau : 49 sur 72 |
| 2026-10-12 | Création du module (première étape) | 4 nouvelles références de validation, toutes hors tolérance ; tableau : 49 sur 70 |
