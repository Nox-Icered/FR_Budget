# Hypothèses à plage nulle : secondes sources proposées

Lot C de la revue de code (28 octobre 2026). Sept hypothèses du registre ont une plage nulle (valeur basse = valeur centrale = valeur haute). Leur incertitude n'entre donc pas dans les fourchettes publiées. Décision du mainteneur : chercher une seconde source publique pour chacune et **proposer** une plage, sans l'appliquer avant relecture. Quand rien n'est trouvé, le site le signale.

**Rien n'est appliqué dans ce lot.** `registres/hypotheses.yaml` et le moteur sont inchangés, et aucun test ne bouge. Le site signale désormais toute hypothèse à plage nulle (page Hypothèses). Chaque proposition ci-dessous est à relire. Les plages retenues seront saisies dans un lot de calcul séparé, avec les tests qui bougent.

Documents téléchargés le 28 octobre 2026 et lus pour ce lot. Ils ne sont pas encore versés au dépôt : ils le seront avec le lot qui applique les plages.

| Document | URL | Empreinte SHA-256 |
|---|---|---|
| G. Mourre, A. Poissonnier, « What Drives the Responsiveness of the Budget Balance to the Business Cycle in EU Countries? », *Intereconomics*, vol. 54, 2019, n° 4 | https://www.intereconomics.eu/contents/year/2019/number/4/article/what-drives-the-responsiveness-of-the-budget-balance-to-the-business-cycle-in-eu-countries.html | page HTML, non conservée |
| Insee Première n° 2114, « Les revenus d'activité des non-salariés en 2024 » (juin 2026) | https://www.insee.fr/fr/statistiques/fichier/version-html/9013403/IP2114.pdf | `02fefb0fd008b606e00644c8ae6fb5f26e084288a8f6a3e4312c8bca5a0444a1` |
| Insee, Note de conjoncture de mars 2026, fiche « Salaires » | https://www.insee.fr/fr/statistiques/fichier/8907437/ndc-mars-2026-salaires.pdf | `cc69f155bf796d68567f5055f35ca5f087399929c0f6c43aa8ebda0ac5f095d2` |

Documents déjà au dépôt :
- COR, rapport annuel de juin 2026 (`cor_rapport_annuel_2026`), avec ses données (`cor_ra2026_donnees_partie2.xlsx`) ;
- RESF du PLF 2027 (`plf2027_resf`) ;
- tome I de Voies et Moyens du PLF 2026 (`plf2026_voies_et_moyens_tome1`).

## Synthèse

| Hypothèse | Valeur actuelle | Seconde source | Plage proposée |
|---|---|---|---|
| `croissance_effet_ecart_production_solde` | 0,5 | Commission européenne (Mourre et Poissonnier, 2019) : 0,60 et 0,63 ; RESF 2027 : 0,57 | 0,5 à 0,63 |
| `croissance_persistance_ecart_production` | 0,7 | **aucune trouvée** | plage nulle, signalée sur le site |
| `retraites_duree_montee_en_charge` | 4 ans | COR 2026, figure 2.5 (âge conjoncturel de départ observé après la réforme de 2010) | 4 à 4,9 ans |
| `menages_ecart_evolution_salaire_smic` | 0 | Insee, note de conjoncture de mars 2026 (SMB, SMPT 2025) | −0,2 % à 0 % |
| `menages_ecart_evolution_pension_moyenne` | 0 | COR 2026, tableau 2.1 (pension moyenne réelle) | 0 % à +1,0 % |
| `menages_ecart_evolution_revenu_independant` | 0 | Insee Première n° 2114 (revenus 2024) | −0,6 % à 0 % |
| `scenario_rendement_constant_pib` | 0 | RESF 2027 et Voies et Moyens 2026 (élasticités des recettes) | plage nulle gardée, RESF cité (option (a), décidée) |

Les valeurs centrales actuelles sont gardées dans toutes les propositions. Le choix d'une autre valeur centrale (par exemple 0,57 au lieu de 0,5) est laissé au mainteneur.

## 1. Effet d'un point d'écart de production sur le solde (`croissance_effet_ecart_production_solde`)

Valeur actuelle : 0,5 (OFCE, *Policy Brief* n° 146, encadré 3, « valeur usuelle »).

Secondes sources :
- **Commission européenne.** Mourre et Poissonnier (2019), tableau 1, « Robustness analysis of budget balance semi-elasticities ». Pour la France, la semi-élasticité du solde est de **0,60** (estimation de 2014) et de **0,63** (estimation de 2018), contre 0,5 en moyenne dans l'UE (texte et figure 1). Les auteurs sont économistes de la DG ECFIN : c'est la méthode commune de l'UE. La publication de la Commission elle-même (*Discussion Paper* 098, economy-finance.ec.europa.eu) est **inaccessible depuis l'environnement** ; les valeurs sont lues dans l'article d'*Intereconomics*.
- **RESF du PLF 2027** (DG Trésor), page 104 du PDF, note du tableau du solde structurel. La composante conjoncturelle est « le produit de l'écart de production et de la semi-élasticité du solde à l'écart de production (soit **0,57**) ».

Proposition : plage de **0,5 à 0,63**, valeur centrale 0,5 inchangée.

Limites :
- La semi-élasticité mesure l'effet immédiat de l'écart de production sur le solde, rapporté au PIB potentiel. Le paramètre alpha de l'OFCE a le même sens, mais son modèle est plus simple.
- La plage est asymétrique : la valeur centrale actuelle est sa borne basse.

## 2. Persistance de l'écart de production (`croissance_persistance_ecart_production`)

Valeur actuelle : 0,7 (OFCE, *Policy Brief* n° 146, encadré 3 : « une valeur usuelle dans les études empiriques »).

Recherches menées :
- avis du HCFP n° 2025-5 ;
- RESF du PLF 2027 ;
- recherche web (DG Trésor, Cour des comptes, HCFP).

Aucune autre valeur publiée du coefficient de résorption annuelle de l'écart de production n'a été trouvée. Les publications de la Commission européenne sont inaccessibles depuis l'environnement.

Proposition : **pas de plage**. La plage nulle est signalée sur la page Hypothèses du site. Une source qui donnerait ce coefficient (par exemple un document de travail de la DG Trésor ou de la Banque de France) peut être déposée.

## 3. Durée de montée en charge d'un an d'âge effectif (`retraites_duree_montee_en_charge`)

Valeur actuelle : 4 ans (rythme légal de la réforme de 2023, trois mois par génération ; le lien entre âge légal et âge effectif n'est pas sourcé).

Seconde source : **COR, rapport annuel de juin 2026, figure 2.5** (page 78 du PDF ; données dans `cor_ra2026_donnees_partie2.xlsx`, onglet « Fig 2.5 »). L'âge conjoncturel de départ observé passe de :
- 60,49 ans en 2010 à 62,12 ans en 2017, soit +1,63 an en 7 ans : **4,3 ans par an d'âge effectif** ;
- 60,49 ans en 2010 à 62,31 ans en 2019, soit +1,82 an en 9 ans : **4,9 ans par an**.

Le COR attribue le début de cette hausse à la réforme de 2010 : page 78, « report de l'âge minimal de 60 à 62 ans et report de l'âge d'annulation de la décote de 65 à 67 ans » ; page 217, cette réforme « décale progressivement l'âge d'ouverture des droits de 60 à 62 ans ».

Proposition : plage de **4 à 4,9 ans**, valeur centrale 4 inchangée. **Appliquée** (branche `plages/retraites`) au levier sur l'âge effectif : les bornes de l'effet croisent celles de l'effet d'un an et celles de la durée (`docs/fiches/retraites.md`, journal).

Limites :
- La hausse observée mêle d'autres causes : durée d'assurance requise, départs anticipés, entrée plus tardive dans la vie active (COR, pages 78 et 217).
- Le choix de la fenêtre (2017 ou 2019) est le mien.
- Le modèle par cohortes (`retraites_cohortes`) lit la même hypothèse, mais seulement sa valeur centrale : c'est le rythme légal de trois mois par génération, sans incertitude. Il n'est donc pas concerné par la plage (correction : la première version de ce document disait qu'il n'utilisait pas l'hypothèse).

## 4. Salaires médian et du 95e centile face au SMIC net (`menages_ecart_evolution_salaire_smic`)

Valeur actuelle : 0 (salaires de l'Insee de 2024 portés en 2025 comme le SMIC net).

Seconde source : **Insee, note de conjoncture de mars 2026, fiche « Salaires », figure 1** (page 1). En moyenne annuelle 2025 :
- salaire mensuel de base (SMB) : **+2,0 %** ;
- salaire moyen par tête (SMPT) des branches marchandes non agricoles : **+1,8 %**.

Comparaison : le modèle fait évoluer le SMIC net (OpenFisca, juin 2024 → juin 2025, mois repère des ménages types) de +1,97 %. L'écart vaut +0,03 % avec le SMB et −0,17 % avec le SMPT.

Proposition : plage de **−0,2 % à 0 %**, valeur centrale 0 inchangée. La borne haute de +0,03 % est arrondie à 0. **Appliquée** (branche `plages/menages`) : voir « Fourchette selon le revenu » dans `docs/fiches/menages_types.md`.

Limites :
- Ce sont des moyennes, et non la médiane ou le 95e centile.
- Le champ est le secteur marchand non agricole.

## 5. Pension moyenne face à la revalorisation (`menages_ecart_evolution_pension_moyenne`)

Valeur actuelle : 0 (pension moyenne de la DREES de fin 2023, revalorisée comme les pensions de base jusqu'en 2025).

La meilleure seconde source serait l'édition 2026 de « Les retraités et les retraites » de la DREES (fiche 5, pensions de fin 2024). **Le site de la DREES est inaccessible depuis l'environnement** (drees.solidarites-sante.gouv.fr, 28 octobre 2026). Pour l'utiliser, il faut déposer le PDF de la fiche 5 de l'édition 2026.

En attendant : **COR, rapport annuel de juin 2026, tableau 2.1** (page 73 du PDF). La pension moyenne réelle progresse de **0,4 %** par an en moyenne de 2002 à 2025, et de **0,5 %** par an de 2025 à 2030 (scénario de référence). Les pensions étant indexées sur les prix, cette hausse réelle mesure surtout l'effet du renouvellement des générations (« effet noria », défini par le COR page 76, note 66).

Proposition : plage de **0 % à +1,0 %** sur les deux années (fin 2023 → 2025, deux fois 0,5 %), valeur centrale 0 inchangée. **Appliquée** (branche `plages/menages`).

Limites :
- Ce sont des moyennes sur longue période et des projections, pas l'observé de 2024 et 2025.
- En 2024, la revalorisation (5,3 %) a dépassé l'inflation : la pension moyenne réelle de cette année-là mêle effet noria et revalorisation.

## 6. Revenu des non-salariés face au SMIC horaire (`menages_ecart_evolution_revenu_independant`)

Valeur actuelle : 0 (revenu médian des non-salariés classiques de 2023, Insee Première n° 2060, porté en 2025 comme le SMIC horaire brut).

Seconde source : **Insee Première n° 2114** (juin 2026) :
- figure 1 (page 2) : le revenu d'activité moyen des non-salariés hors micro-entrepreneurs augmente de **+0,7 %** en euros constants en 2024 ;
- texte (page 3) : l'inflation est passée de 4,9 % en 2023 à **2,0 %** en 2024.

En euros courants, cela donne environ +2,7 % (1,007 × 1,020). Le SMIC horaire brut au 1er janvier (OpenFisca, comme le modèle) passe de 11,27 € en 2023 à 11,65 € en 2024, soit +3,4 %. L'écart en 2024 vaut donc **−0,6 %**.

Proposition : plage de **−0,6 % à 0 %**, valeur centrale 0 inchangée. **Appliquée** (branche `plages/menages`).

Limites :
- C'est une moyenne, et non la médiane utilisée par le modèle.
- Rien n'est encore publié sur 2025.

## 7. Rendement constant en points de PIB (`scenario_rendement_constant_pib`)

Valeur actuelle : 0. Le rendement d'une mesure croît comme le PIB, soit une élasticité unitaire. La valeur n'est pas lue par le calcul : elle documente la convention.

Sources trouvées :
- **RESF du PLF 2027**, page 169 du PDF : l'élasticité de 1 est la « valeur de référence à moyen terme, qui correspond à la moyenne de l'élasticité sur longue période ». Pages 93 et 113 : l'élasticité des prélèvements obligatoires vaut 0,7 en 2025, 0,7 en 2026 et 0,8 en 2027.
- **Voies et Moyens, tome I, PLF 2026**, page 7 du PDF : l'élasticité des recettes fiscales nettes de l'État vaut 1,2 en 2025 et 0,5 en 2026.

Ces sources confirment la convention à long terme. Elles montrent aussi des écarts annuels importants, de 0,5 à 1,2. Elles portent sur l'ensemble des prélèvements, pas sur la TVA, les accises ou l'IS une à une.

**Décision du mainteneur (28 octobre 2026) : option (a), appliquée.** Le RESF est ajouté aux sources de l'hypothèse et la justification est mise à jour. La plage reste nulle et le site la signale.

Options présentées :
- **(a)** Garder la plage nulle, signalée sur le site, en citant le RESF comme seconde source de la convention.
- **(b)** Ajouter une plage d'élasticité (par exemple 0,7 à 1,2) sur les premières années. C'est un changement de calcul : le moteur devrait appliquer l'élasticité année par année. Il serait fait dans un lot séparé, avec les tests qui bougent.

## Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-28 | § 4 à 6 appliqués : ménages types au revenu bas, central et haut (sources `insee_premiere_2114` et `insee_note_conjoncture_2026_03_salaires` versées au dépôt) | Valeurs centrales inchangées ; fourchettes du net après impôt publiées (détail : `docs/fiches/menages_types.md`) |
| 2026-10-28 | § 3 appliqué : durée de montée en charge de 4 à 4,9 ans (levier sur l'âge effectif) | Validation inchangée (valeur centrale) ; bornes basses de l'écart de solde plus basses pendant la montée en charge (détail : `docs/fiches/retraites.md`) ; 1 test unitaire ajouté |
| 2026-10-28 | Option (a) retenue pour `scenario_rendement_constant_pib` : RESF ajouté aux sources, plage nulle gardée | Aucun (valeur non lue par le calcul) |
| 2026-10-28 | Propositions de plages pour 5 hypothèses sur 7. Signalement des plages nulles sur la page Hypothèses du site. | Aucun (registre et moteur inchangés). Tests web : un test ajouté. |
