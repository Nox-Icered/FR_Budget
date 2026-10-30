---
# En-tête lu par la vérification des registres : l'identifiant doit exister dans
# registres/leviers.yaml (levier) ou désigner un module documenté (module).
levier: assurance_chomage
statut: beta
mise_a_jour: 2026-10-30
---

# Fiche : assurance chômage (première étape, leviers agrégés)

Premier lot de la V2 (exception à la porte 3 décidée le 30 octobre 2026, `docs/plan.md`, § 6 bis). Plan soumis et validé tel quel par le mainteneur le 30 octobre 2026. Le modèle de flux d'allocataires prévu par la spécification viendra dans une seconde étape.

## 1. Question posée

Que deviennent le solde et la dette des administrations publiques si l'on change :

- le taux de la contribution patronale d'assurance chômage (« hausse de 0,1 point du taux ») ;
- la revalorisation des allocations au 1er juillet (« revalorisation supérieure de 1 point à celle décidée ») ;
- le coefficient appliqué à la durée d'indemnisation (« coefficient porté de 0,75 à 0,80 ») ?

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Taux de la contribution patronale | `chomage_taux_contribution_2026` (4,00 %) | -1 à +1 point, pas de 0,05 | `unedic_parametres_utiles_juillet_2026`, page 3 |
| Revalorisation au 1er juillet, en écart à celle décidée | aucune revalorisation au 1er juillet 2026 | -2 à +2 points, pas de 0,1 | `unedic_previsions_octobre_2026` |
| Coefficient appliqué à la durée d'indemnisation | `chomage_coefficient_duree_2026` (0,75) | -0,25 à +0,25, pas de 0,05 | `unedic_parametres_utiles_juillet_2026`, page 5 |

Bornes choisies au lot (à relire) : la contribution exceptionnelle de 0,05 point de 2017 à 2025 et la modulation des taux par entreprise (2,95 % à 5,00 %) ; les deux revalorisations de 1,9 % de 2023 ; la réforme de 2023 (coefficient de 1 à 0,75).

## 3. Méthode de calcul

Moteur agrégé, `moteur/src/fr_budget/agrege/assurance_chomage.py`, branché dans `fr_budget.scenario` (`effet_chomage`).

- **Contribution** : rendement d'un point = contributions principales de 2026 avant prélèvements de l'État (`chomage_contributions_principales_2026`, 30,3 Md€) / taux de 2026, ramené en euros de 2025 par la croissance nominale du RESF 2027, puis tenu constant en points de PIB. Entrée en vigueur au 1er janvier.
- **Revalorisation** (au 1er juillet, une fois) : coût d'un point en part des allocations brutes, calé sur la revalorisation de 1,9 % du 1er juillet 2023 (mode d'emploi de l'Unédic, tableau 2) : 222 M€ en 2023 (six mois), 293 M€ en 2024, rapportés aux allocations brutes et aides de 2023 (35,0 Md€). Au-delà de la deuxième année, seuls les paramètres fixes (partie fixe, ARE minimale, plancher de l'AREF : 104 M€ en 2024) restent, puisque les nouveaux entrants en bénéficient ; la revalorisation des salaires de référence « s'atténue au gré des sorties d'indemnisation » (même document, page 4) et n'est plus comptée. Appliqué aux allocations de 2026 (38,1 Md€).
- **Durée** : effet proportionnel à l'écart de coefficient, calé sur la réforme de 2023 (de 1 à 0,75 : 4,2 Md€ de moindres allocations en régime de croisière, euros de 2027), avec sa montée en charge : rien la première année, 0,7/4,5 la deuxième, 3,0/4,5 la troisième, plein effet la quatrième (hypothèse `chomage_duree_rang_croisiere`). Entrée en vigueur au 1er janvier.
- **Retours aux administrations publiques** (choix 1 du plan) : les versements de l'Unédic à France Travail (11 % des contributions, deux ans plus tard) et aux caisses de retraite complémentaire (environ 7 % des allocations) sont des transferts entre administrations publiques et ne changent pas leur solde : ils ne sont pas comptés. Les chiffrages de l'Unédic, faits pour l'Unédic seule, les incluent : la validation compare le modèle aux montants avant ces transferts. Pour la revalorisation et la durée, la CSG et la CRDS sur les allocations (6,58 % de l'allocation brute, OpenFisca 2026) reviennent en partie aux administrations publiques (hypothèse `chomage_retour_prelevements`).

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `unedic_previsions_octobre_2026_pdf` | Contributions principales et allocations de 2026 ; avenant de 2026 sur les ruptures conventionnelles | octobre 2026 |
| `unedic_parametres_utiles_juillet_2026_pdf` | Taux de contribution, coefficient de durée | juillet 2026 |
| `unedic_etude_impact_convention_2024_pdf` | Suppression de la contribution de 0,05 point (2026) ; taux de 4,05 % | 2025 |
| `unedic_etude_impact_convention_2017_pdf` | Création de la contribution de 0,05 point (2019) | 2017 |
| `unedic_previsions_mars_2019_pdf` | Contributions principales de 2019, allocations de 2018 | mars 2019 |
| `unedic_revalorisation_mode_emploi_2023_pdf` | Profil de coût de la revalorisation du 1er juillet 2023 | juin 2023 |
| `unedic_previsions_juin_2024_pdf` | Allocations de 2023 | juin 2024 |
| `unedic_communique_revalorisation_avril_2023_html`, `unedic_communique_revalorisation_juillet_2018_html` | Références de validation de la revalorisation | 2023, 2018 |
| `unedic_effets_adaptation_conjoncture_2023_pdf` | Économies de la réforme de 2023 par année | 2023 |
| `unedic_etude_impact_avenant_rci_2026_pdf` | Contexte de l'avenant de 2026 | octobre 2026 |

## 5. Hypothèses

| Hypothèse (`registres/hypotheses.yaml`) | Valeur centrale | Plage | Effet sur le résultat |
|-----------------------------------------|-----------------|-------|-----------------------|
| `chomage_retour_prelevements` | 0,5 du taux plein | 0 à 1 | Revalorisation et durée : coût net de 0 à 6,58 % plus faible que le coût brut |
| `chomage_duree_rapport_hypotheses_unedic` | 1 | 0,896 à 1,104 | Durée : ±10,4 %, écart des deux hypothèses de l'Unédic sur le prolongement des droits des seniors (avenant de 2026) |
| `chomage_duree_rang_croisiere` | 4e année | 4e à 5e année | Durée : la quatrième année, plein effet ou effet de la troisième |

Contribution : bornes = valeur centrale multipliée par le rapport entre le chiffrage de l'Unédic et le modèle pour chacune des deux mesures de 0,05 point (2019 : 0,975 ; 2026 : 1,016). Les bornes de chaque année sont les extrêmes sur les combinaisons des plages.

## 6. Validation

Tolérance : ±10 % (règle de publication). Test : `moteur/tests/validation/test_levier_assurance_chomage.py`.

| Référence | Millésime | Valeur de référence | Valeur du modèle | Écart | Dans la tolérance |
|-----------|-----------|---------------------|------------------|-------|-------------------|
| `chomage_contribution_hausse_0_05_2019` (création de la contribution de 0,05 point) | 2019 | 288 M€ | 295 M€ | +2,5 % | oui |
| `chomage_contribution_baisse_0_05_2026` (suppression de la contribution de 0,05 point) | 2026 | 385 M€ | 379 M€ | -1,6 % | oui |
| `chomage_revalorisation_avril_2023_cumul` (1,9 % au 1er avril 2023, cumul 2023-2024) | 2023 | 590 M€ | 626 M€ | +6,1 % | oui |
| `chomage_revalorisation_juillet_2018_cout` (0,70 % au 1er juillet 2018, fin 2018 et 2019) | 2018 | 200 M€ | 182 M€ | -9,2 % | oui |

Limites de cette validation :

- toutes les références viennent de l'Unédic : aucune confrontation indépendante (Cour des comptes, DARES, OFCE) n'est encore faite. Reste à faire ;
- la revalorisation est calée sur la revalorisation du 1er juillet 2023 ; les deux références sont d'autres revalorisations, mais chiffrées par le même organisme. La référence de 2018 est « de l'ordre de 200 millions » ;
- la durée est calée sur le seul chiffrage publié pour l'ensemble des allocataires (réforme de 2023) : la comparer à ce même chiffrage serait circulaire, elle n'a donc **pas de référence de validation**. L'avenant de 2026 sur les ruptures conventionnelles (730 à 900 M€ en régime de croisière) ne vise qu'une partie des allocataires : il ne sert qu'à la plage.

Les trois leviers restent « bêta, non validé ».

## 7. Limites connues

- Aucun effet de comportement : une durée plus courte ou une allocation plus faible peut accélérer les reprises d'emploi (l'Unédic signale que les économies seraient alors plus élevées), un taux de contribution plus élevé peut peser sur l'emploi.
- Effet de la durée linéaire dans l'écart de coefficient, et symétrique (une hausse coûte ce qu'une baisse rapporte), alors que la réforme de 2023 a gardé une durée minimale de six mois et un complément de fin de droits en conjoncture défavorable.
- Les prélèvements sur les allocations ne comptent que la CSG et la CRDS ; l'impôt sur le revenu sur les allocations n'est pas compté.
- Contribution : les contributions principales comprennent des contributions particulières (intermittents, expatriés, employeurs publics adhérents) ; leur taux n'est pas forcément celui du levier.
- La revalorisation compte les paramètres fixes indéfiniment et les salaires de référence deux ans seulement ; l'Unédic ne publie pas d'effet au-delà de la deuxième année.
- Les effets sur les ménages types (allocation d'un chômeur type) et sur la charge des entreprises (contribution patronale) ne sont pas encore calculés.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-30 | Première étape : trois leviers agrégés calés sur l'Unédic (plan validé par le mainteneur) | Ajout : 4 tests de validation, `tests/unitaires/test_assurance_chomage.py` ; `test_validation_resume` étendu aux 4 nouvelles références |
