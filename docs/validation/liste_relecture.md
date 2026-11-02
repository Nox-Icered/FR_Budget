# Liste de relecture

Générée le 2026-11-02 par `outils/liste_relecture.py` à partir des registres ; ne pas modifier à la main, relancer le script.

Pour chaque ligne : ouvrir le document à la page indiquée, vérifier la valeur, l'unité et ce qu'elle mesure. Cocher la case quand la valeur est conforme, ou noter l'écart. Les lignes cochées passent ensuite à `relecture: relu` dans `registres/references/chiffrages.yaml`. Le classement entre entrées du calcul et références de validation est repéré automatiquement dans le code : il est indicatif.

**336 chiffrages à relire** sur 336, dont 186 entrées du calcul (à relire en premier : elles changent les résultats affichés), 107 références de validation et 43 non repérés automatiquement. Puis **45 hypothèses** (valeur centrale et plage).

## Sommaire

| Levier ou module | À relire | Entrées du calcul |
|---|---|---|
| [tva](#tva) | 28 | 2 |
| [impot_revenu](#impot-revenu) | 37 | 37 |
| [impot_societes](#impot-societes) | 6 | 1 |
| [csg](#csg) | 34 | 26 |
| [cotisations_patronales](#cotisations-patronales) | 14 | 12 |
| [accises_energie](#accises-energie) | 14 | 9 |
| [depenses_fiscales](#depenses-fiscales) | 19 | 0 |
| [credits_missions](#credits-missions) | 3 | 0 |
| [remunerations_publiques](#remunerations-publiques) | 37 | 24 |
| [indexation_pensions_prestations](#indexation-pensions-prestations) | 12 | 1 |
| [minima_prime_activite](#minima-prime-activite) | 5 | 4 |
| [dotations_collectivites](#dotations-collectivites) | 5 | 1 |
| [retraites](#retraites) | 6 | 0 |
| [assurance_chomage](#assurance-chomage) | 27 | 20 |
| [croissance](#croissance) | 11 | 0 |
| [dynamique_dette](#dynamique-dette) | 12 | 7 |
| [menages_types](#menages-types) | 66 | 42 |

## tva

### Entrée du calcul (2)

- [ ] `tva_nette_totale_2022_dgtresor` : **202,7 Md€** (2022)
  - Mesure : TVA nette en comptabilité budgétaire, toutes administrations publiques, 2022 (sert au vieillissement 2022 → 2025)
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Page 2, section 1
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_nette_totale_prevision_2025` : **210 Md€** (PLF 2026)
  - Mesure : TVA nette totale en comptabilité budgétaire, prévision 2025 (sert au vieillissement 2022 → 2025)
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome I (recettes), Tableau « TVA brute totale… », page 33 (section « Taxe sur la valeur ajoutée nette »)
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087930/file/PLF%202026%20-%20V%26M%20TI%20-%20Evaluations%20des%20recettes.pdf ; fichier : `data/raw/tva/plf2026_voies_et_moyens_tome1.pdf`

### Référence de validation (18)

- [ ] `tva_point_net_2025_ensemble` : **11,4 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement net (après TVA payée par les APU) d'une hausse d'un point de tous les taux, statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 2, page 5
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_brut_2025_ensemble` : **13,7 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement brut d'une hausse d'un point de tous les taux, statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 1, page 4
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_net_2025_taux_2_1` : **0,4 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement net (après TVA payée par les APU) d'une hausse d'un point de le taux super-réduit (2,1 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 2, page 5
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_brut_2025_taux_2_1` : **0,4 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement brut d'une hausse d'un point de le taux super-réduit (2,1 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 1, page 4
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_net_2025_taux_5_5` : **2 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement net (après TVA payée par les APU) d'une hausse d'un point de le taux réduit (5,5 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 2, page 5
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_brut_2025_taux_5_5` : **2,4 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement brut d'une hausse d'un point de le taux réduit (5,5 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 1, page 4
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_net_2025_taux_10` : **1,6 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement net (après TVA payée par les APU) d'une hausse d'un point de le taux intermédiaire (10 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 2, page 5
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_brut_2025_taux_10` : **1,9 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement brut d'une hausse d'un point de le taux intermédiaire (10 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 1, page 4
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_net_2025_taux_20` : **7,5 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement net (après TVA payée par les APU) d'une hausse d'un point de le taux normal (20 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 2, page 5
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_point_brut_2025_taux_20` : **8,9 Md€** (2025 (modèle 2022 vieilli))
  - Mesure : Rendement brut d'une hausse d'un point de le taux normal (20 %), statique
  - Où : Trésor-Éco n° 371, « Analyse de la composition des recettes de TVA » (M. Gesta), Tableau 1, page 4
  - Document : https://www.tresor.economie.gouv.fr/Articles/2025/09/25/analyse-de-la-composition-des-recettes-de-tva ; fichier : `data/raw/tva/dgtresor_tresor_eco_371_2025-09.pdf`
- [ ] `tva_nette_totale_execution_2024` : **210,7 Md€** (PLF 2026)
  - Mesure : TVA nette totale en comptabilité budgétaire, exécution 2024
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome I (recettes), Tableau « TVA brute totale… », page 33 (section « Taxe sur la valeur ajoutée nette »)
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087930/file/PLF%202026%20-%20V%26M%20TI%20-%20Evaluations%20des%20recettes.pdf ; fichier : `data/raw/tva/plf2026_voies_et_moyens_tome1.pdf`
- [ ] `tva_point_brut_2015_ensemble` : **9,75 Md€** (2015 (estimation du PLF pour 2016))
  - Mesure : Rendement d'une hausse d'un point de tous les taux, statique, hors hausse des dépenses publiques induite (arrondi au quart de milliard dans la source)
  - Où : Les Cahiers de la DG Trésor n° 2016-02, « Le modèle d'estimation de la TVA théorique » (J.-A. Andrivon, C. Geay, É. Janbon), Tableau 8, page 24 (page 26 du PDF)
  - Document : https://www.tresor.economie.gouv.fr/Articles/8a0808ef-32d9-487c-87f3-8b86a5e65785/files/8c114556-bf7a-4ee1-a827-3cdda0107371 ; fichier : `data/raw/tva/dgtresor_cahier_2016-02_tva_theorique.pdf`
- [ ] `tva_point_brut_2015_taux_2_1` : **0,5 Md€** (2015 (estimation du PLF pour 2016))
  - Mesure : Rendement d'une hausse d'un point de le taux super-réduit (2,1 %), statique, hors hausse des dépenses publiques induite (arrondi au quart de milliard dans la source)
  - Où : Les Cahiers de la DG Trésor n° 2016-02, « Le modèle d'estimation de la TVA théorique » (J.-A. Andrivon, C. Geay, É. Janbon), Tableau 8, page 24 (page 26 du PDF)
  - Document : https://www.tresor.economie.gouv.fr/Articles/8a0808ef-32d9-487c-87f3-8b86a5e65785/files/8c114556-bf7a-4ee1-a827-3cdda0107371 ; fichier : `data/raw/tva/dgtresor_cahier_2016-02_tva_theorique.pdf`
- [ ] `tva_point_brut_2015_taux_5_5` : **1,75 Md€** (2015 (estimation du PLF pour 2016))
  - Mesure : Rendement d'une hausse d'un point de le taux réduit (5,5 %), statique, hors hausse des dépenses publiques induite (arrondi au quart de milliard dans la source)
  - Où : Les Cahiers de la DG Trésor n° 2016-02, « Le modèle d'estimation de la TVA théorique » (J.-A. Andrivon, C. Geay, É. Janbon), Tableau 8, page 24 (page 26 du PDF)
  - Document : https://www.tresor.economie.gouv.fr/Articles/8a0808ef-32d9-487c-87f3-8b86a5e65785/files/8c114556-bf7a-4ee1-a827-3cdda0107371 ; fichier : `data/raw/tva/dgtresor_cahier_2016-02_tva_theorique.pdf`
- [ ] `tva_point_brut_2015_taux_10` : **1,25 Md€** (2015 (estimation du PLF pour 2016))
  - Mesure : Rendement d'une hausse d'un point de le taux intermédiaire (10 %), statique, hors hausse des dépenses publiques induite (arrondi au quart de milliard dans la source)
  - Où : Les Cahiers de la DG Trésor n° 2016-02, « Le modèle d'estimation de la TVA théorique » (J.-A. Andrivon, C. Geay, É. Janbon), Tableau 8, page 24 (page 26 du PDF)
  - Document : https://www.tresor.economie.gouv.fr/Articles/8a0808ef-32d9-487c-87f3-8b86a5e65785/files/8c114556-bf7a-4ee1-a827-3cdda0107371 ; fichier : `data/raw/tva/dgtresor_cahier_2016-02_tva_theorique.pdf`
- [ ] `tva_point_brut_2015_taux_20` : **6,5 Md€** (2015 (estimation du PLF pour 2016))
  - Mesure : Rendement d'une hausse d'un point de le taux normal (20 %), statique, hors hausse des dépenses publiques induite (arrondi au quart de milliard dans la source)
  - Où : Les Cahiers de la DG Trésor n° 2016-02, « Le modèle d'estimation de la TVA théorique » (J.-A. Andrivon, C. Geay, É. Janbon), Tableau 8, page 24 (page 26 du PDF)
  - Document : https://www.tresor.economie.gouv.fr/Articles/8a0808ef-32d9-487c-87f3-8b86a5e65785/files/8c114556-bf7a-4ee1-a827-3cdda0107371 ; fichier : `data/raw/tva/dgtresor_cahier_2016-02_tva_theorique.pdf`
- [ ] `tva_point_brut_ipp_2025_quatre_taux` : **13 Md€** (Perspectives budgétaires, juin 2025)
  - Mesure : Hausse des recettes de TVA pour une hausse d'un point des quatre taux de TVA (IPP)
  - Où : IPP, Perspectives budgétaires, juin 2025, chapitre 2 « Effets budgétaires et redistributifs des mesures socio-fiscales » (H. Darricau, S. Duchesne, B. Garbinti, L. Josseran, F. Reutzel), Tableau 2.1 « Effets budgétaires d'une hausse d'un point de la TVA », ligne « Recettes de TVA », page 38 (fichier lu : sha256 aa28c3ae6056457d6991ffa1ed385e337d9fd20f411bd704cc4e6dfee2ba64a2)
  - Document : https://www.ipp.eu/wp-content/uploads/2025/06/chapitre_2_fiscalite_web.pdf ; fichier : aucun
- [ ] `tva_point_net_ipp_2025_quatre_taux` : **11 Md€** (Perspectives budgétaires, juin 2025)
  - Mesure : Effet d'une hausse d'un point des quatre taux de TVA sur le solde public, net de la TVA payée par les administrations publiques sur leurs achats (IPP)
  - Où : IPP, Perspectives budgétaires, juin 2025, chapitre 2 « Effets budgétaires et redistributifs des mesures socio-fiscales » (H. Darricau, S. Duchesne, B. Garbinti, L. Josseran, F. Reutzel), Page 38 : « 2 Mde étant payé par les administrations publiques sur leurs achats, les dépenses publiques augmentent d'autant, et l'effet sur le solde public se trouve limité à 11 Mde » (sha256 aa28c3ae6056457d6991ffa1ed385e337d9fd20f411bd704cc4e6dfee2ba64a2)
  - Document : https://www.ipp.eu/wp-content/uploads/2025/06/chapitre_2_fiscalite_web.pdf ; fichier : aucun

### Non repéré (8)

- [ ] `tva_nette_totale_execution_2023` : **208,4 Md€** (PLF 2025)
  - Mesure : TVA nette totale en comptabilité budgétaire, exécution 2023
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome I (recettes), Tableau « TVA brute totale… », page 30 (section « Taxe sur la valeur ajoutée nette »)
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_1_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome1.pdf`
- [ ] `tva_depense_fiscale_730213_2023` : **2 150 M€** (2023 (réalisation, PLF 2025))
  - Mesure : Taux de 10 % pour les travaux d'amélioration, de transformation, d'aménagement et d'entretien des logements achevés depuis plus de deux ans (hors rénovation énergétique) ; coût par rapport au taux normal de 20 %
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Tome II, page 165, dépense fiscale n° 730213, colonne « Réalisation 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `tva_depense_fiscale_730223_2023` : **970 M€** (2023 (réalisation, PLF 2025))
  - Mesure : Taux de 5,5 % pour les travaux d'amélioration de la qualité énergétique des logements achevés depuis plus de deux ans ; coût par rapport au taux normal de 20 %
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Tome II, page 167, dépense fiscale n° 730223, colonne « Réalisation 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `tva_depense_fiscale_710103_2023` : **1 940 M€** (2023 (réalisation, PLF 2025))
  - Mesure : Niveau des taux en Guadeloupe, en Martinique et à La Réunion (8,5 % et 2,1 %) ; coût par rapport aux taux de la France métropolitaine
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Tome II, page 159, dépense fiscale n° 710103, colonne « Réalisation 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `tva_depense_fiscale_710105_2023` : **160 M€** (2023 (réalisation, PLF 2025))
  - Mesure : Non-application provisoire de la TVA en Guyane et à Mayotte ; coût par rapport à l'application de la TVA
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Tome II, page 159, dépense fiscale n° 710105, colonne « Réalisation 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `tva_depense_fiscale_730306_2023` : **197 M€** (2023 (réalisation, PLF 2025))
  - Mesure : Taux particuliers applicables en Corse ; coût par rapport aux taux de la France continentale
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Tome II, page 172, dépense fiscale n° 730306, colonne « Réalisation 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `tva_depense_fiscale_730221_2023` : **2 000 M€** (2023 (réalisation, PLF 2025))
  - Mesure : Taux de 10 % pour la restauration commerciale ; coût par rapport au taux normal de 20 % (contrôle, non utilisé par le modèle)
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Tome II, page 166, dépense fiscale n° 730221, colonne « Réalisation 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `tva_depense_fiscale_730207_2023` : **171 M€** (2023 (réalisation, PLF 2025))
  - Mesure : Taux de 10 % pour les repas des cantines d'entreprises ou d'administrations ; coût par rapport au taux normal de 20 % (contrôle, non utilisé par le modèle)
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Tome II, page 164, dépense fiscale n° 730207, colonne « Réalisation 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`

## impot_revenu

### Entrée du calcul (37)

- [ ] `ir_non_indexation_2025` : **3,7 Md€** (PLF 2025 (revenus 2024))
  - Mesure : Rendement supplémentaire de l'impôt sur le revenu en 2025 en l'absence d'indexation du barème et des seuils associés (avis d'imposition des revenus 2024 et prélèvement à la source)
  - Où : Projet de loi de finances pour 2025, évaluations préalables des articles, Article 2 (indexation du barème), § 4.2.1, page 18
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/PLF-2025_Evaluations%20prealables.pdf ; fichier : `data/raw/impot_societes/plf/plf2025_evaluations_prealables.pdf`
- [ ] `ir_indexation_plf2025` : **2 %** (PLF 2025)
  - Mesure : Taux d'indexation du barème proposé (prévision d'évolution de l'IPC hors tabac de 2024 par rapport à 2023)
  - Où : Projet de loi de finances pour 2025, évaluations préalables des articles, Article 2, § 1.4, page 15
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/PLF-2025_Evaluations%20prealables.pdf ; fichier : `data/raw/impot_societes/plf/plf2025_evaluations_prealables.pdf`
- [ ] `ir_gel_bareme_2026` : **1,9 Md€** (PLF 2026 (revenus 2025))
  - Mesure : Augmentation attendue du produit de l'impôt sur le revenu en 2026 liée à l'absence d'indexation du barème (chiffrage des mesures nouvelles, Voies et moyens tome I)
  - Où : Rapport général n° 139 (2025-2026), tome I, sur le projet de loi de finances pour 2026, par Jean-François Husson, commission des finances du Sénat, Première partie, I, A, 1, pages 149 et 150
  - Document : https://www.senat.fr/rap/l25-139-1/l25-139-11.pdf ; fichier : `data/raw/impot_revenu/senat_rapport_general_plf2026_tome1.pdf`
- [ ] `ir_rfr_part_moyen_2_2024` : **5 093,2673 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 2e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 2e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_3_2024` : **9 548,2081 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 3e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 3e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_4_2024` : **12 704,8242 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 4e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 4e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_5_2024` : **15 523,3134 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 5e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 5e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_6_2024` : **18 224,0643 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 6e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 6e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_7_2024` : **21 127,6341 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 7e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 7e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_8_2024` : **24 861,9856 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 8e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 8e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_9_2024` : **31 043,1944 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, 9e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 9e dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_10_2024` : **65 532,4266 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, dernier dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « dernier dixième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_c1_2024` : **213 672,0604 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, dernier centième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « dernier centième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_part_moyen_m1_2024` : **916 590,4786 €** (revenus 2024)
  - Mesure : RFR par part fiscale moyen, dernier millième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « dernier millième », colonne « RFR par part fiscale, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_1_2024` : **14,0676 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 1er dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 1er dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_2_2024` : **14,3818 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 2e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 2e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_3_2024` : **6,4355 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 3e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 3e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_4_2024` : **5,2554 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 4e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 4e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_5_2024` : **95,5393 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 5e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 5e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_6_2024` : **485,6725 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 6e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 6e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_7_2024` : **1 103,3304 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 7e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 7e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_8_2024` : **2 008,2831 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 8e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 8e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_9_2024` : **3 895,528 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, 9e dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « 9e dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_10_2024` : **16 136,9224 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, dernier dixième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « dernier dixième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_c1_2024` : **57 712,9726 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, dernier centième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « dernier centième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_bareme_moyen_m1_2024` : **163 412,9721 €** (revenus 2024)
  - Mesure : Impôt au barème moyen par foyer, dernier millième de RFR par part
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », ligne « dernier millième », colonne « Impôt au barème, moyenne »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_total_10_2024` : **272,6582 Md€** (revenus 2024)
  - Mesure : Montant total de RFR, dernier dixième
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « dernier dixième », colonne « RFR »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_total_c1_2024` : **88,9015 Md€** (revenus 2024)
  - Mesure : Montant total de RFR, dont dernier centième
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « dont dernier centième », colonne « RFR »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_total_m1_2024` : **38,1366 Md€** (revenus 2024)
  - Mesure : Montant total de RFR, dont dernier millième
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « dont dernier millième », colonne « RFR »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_total_10_2024` : **67,1403 Md€** (revenus 2024)
  - Mesure : Montant total de impôt au barème, dernier dixième
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « dernier dixième », colonne « impôt au barème »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_total_c1_2024` : **24,0124 Md€** (revenus 2024)
  - Mesure : Montant total de impôt au barème, dont dernier centième
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « dont dernier centième », colonne « impôt au barème »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_total_m1_2024` : **6,7991 Md€** (revenus 2024)
  - Mesure : Montant total de impôt au barème, dont dernier millième
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « dont dernier millième », colonne « impôt au barème »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_rfr_total_total_2024` : **846,9111 Md€** (revenus 2024)
  - Mesure : Montant total de RFR, Total
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « Total », colonne « RFR »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_impot_total_total_2024` : **98,8435 Md€** (revenus 2024)
  - Mesure : Montant total de impôt au barème, Total
  - Où : DGFiP Statistiques n° 41, « L'impôt sur le revenu 2024 a été plus dynamique que les revenus » (novembre 2025), et ses tableaux, Tableau 2 « Impôt au barème et impôt hors barème par décile de RFR par part, revenus 2024 », bloc des montants, ligne « Total », colonne « impôt au barème »
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-revenu-2024-ete-plus-dynamique-que-les-revenus ; fichier : `data/raw/impot_revenu/dgfip_statistiques_41.xlsx`, `data/raw/impot_revenu/dgfip_statistiques_41.pdf`
- [ ] `ir_gel_ipp_inflation_1_0_2026` : **1,1 Md€** (octobre 2025 (inflation de 1 %))
  - Mesure : Recettes de l'impôt sur le revenu d'un gel du barème en 2026, inflation de 1 % (IPP)
  - Où : IPP, « Actualisation de l'estimation de rendement de l'année blanche », Tableau, colonne « Inflation à 1 % (septembre 2025) », ligne « dont recettes de l'IR » (page lue : sha256 765f48922ade283e987d0345f7e651d36d0a299631cfff494fc4672fb4435dcf)
  - Document : https://www.ipp.eu/actualisation-de-lestimation-de-rendement-de-lannee-blanche/ ; fichier : aucun
- [ ] `ir_gel_ipp_inflation_1_3_2026` : **1,4 Md€** (juin 2025 (inflation de 1,3 %))
  - Mesure : Recettes de l'impôt sur le revenu d'un gel du barème en 2026, inflation de 1,3 % (IPP)
  - Où : IPP, « Actualisation de l'estimation de rendement de l'année blanche », Tableau, colonne « Inflation à 1,3 % (juin 2025) », ligne « dont recettes de l'IR » (sha256 765f48922ade283e987d0345f7e651d36d0a299631cfff494fc4672fb4435dcf)
  - Document : https://www.ipp.eu/actualisation-de-lestimation-de-rendement-de-lannee-blanche/ ; fichier : aucun
- [ ] `ir_gel_ofce_2026` : **1,2 Md€** (juin 2025 (revalorisation usuelle prévue de 1,1 %))
  - Mesure : Rendement en 2026 d'un gel total du barème de l'impôt sur le revenu, revalorisation évitée de 1,1 % (OFCE)
  - Où : OFCE, P. Madec, « Impôts et prestations : quels effets attendre d'une "année blanche" ? », blog de l'OFCE, Page 5 : « Le gel total du barème de l'impôt sur le revenu rapporterait quant à lui, selon nos estimations, environ 1,2 milliard d'euros en 2026 » ; note 5 : revalorisation de 1,1 % (sha256 fa4078cd41f39f11560b5050726e2789a112a24ecad9861a782e366658855396)
  - Document : https://ofce.sciences-po.fr/blog2024/fr/2025/20250630_PIM/Post_AnneeBlanche.fr.pdf ; fichier : aucun

## impot_societes

### Entrée du calcul (1)

- [ ] `is_taux_contribution_exceptionnelle_haute` : **41,2 %** (PLF 2025)
  - Mesure : Taux de la contribution exceptionnelle pour les sociétés au chiffre d'affaires d'au moins 3 Md€, premier exercice (en % de l'IS dû)
  - Où : Projet de loi de finances pour 2025, évaluations préalables des articles, Article 11, texte proposé, IV. B., page 120
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/PLF-2025_Evaluations%20prealables.pdf ; fichier : `data/raw/impot_societes/plf/plf2025_evaluations_prealables.pdf`

### Référence de validation (2)

- [ ] `is_brut_2024_dgfip` : **69,05 Md€** (2024 (bénéfices 2024))
  - Mesure : IS brut des entreprises imposées à l'IS, avant réductions et crédits d'impôt
  - Où : DGFiP Statistiques n° 39, « L'impôt sur le bénéfice 2024 des entreprises », Fichier de tableaux, onglet « Tableau 2 », ligne « IS brut », colonne « Ensemble » (69 047 590 312 €)
  - Document : https://www.impots.gouv.fr/dgfip-statistiques-limpot-sur-le-benefice-2024-des-entreprises ; fichier : `data/raw/impot_societes/dgfip/dgfip_stat_39_is-2024.xlsx`, `data/raw/impot_societes/dgfip/dgfip_stat_39_is-2024.pdf`
- [ ] `is_brut_2025_dgfip` : **70,47 Md€** (2025 (bénéfices 2025))
  - Mesure : IS brut des entreprises imposées à l'IS, avant réductions et crédits d'impôt
  - Où : DGFiP Statistiques n° 51, « L'impôt sur le bénéfice 2025 des entreprises », Fichier de tableaux, onglet « Tableau 2 », ligne « TOTAL », colonne « IS brut » (70,47417 Md€)
  - Document : https://www.impots.gouv.fr/node/28492 ; fichier : `data/raw/impot_societes/dgfip/dgfip_stat_51_is-2025.xlsx`, `data/raw/impot_societes/dgfip/dgfip_stat_51_is-2025.pdf`

### Non repéré (3)

- [ ] `is_contribution_exceptionnelle_2025_plf` : **8 Md€** (PLF 2025 (résultats 2023))
  - Mesure : Rendement de la contribution exceptionnelle sur les bénéfices des grandes entreprises (20,6 % ou 41,2 % de l'IS des sociétés au chiffre d'affaires d'au moins 1 Md€), première année
  - Où : Projet de loi de finances pour 2025, évaluations préalables des articles, Article 11, section 4.2.1 « Incidences budgétaires », page 123
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/PLF-2025_Evaluations%20prealables.pdf ; fichier : `data/raw/impot_societes/plf/plf2025_evaluations_prealables.pdf`
- [ ] `is_contribution_exceptionnelle_2025_fipeco` : **7,5 Md€** (2025 (réalisé))
  - Mesure : Rendement de la contribution exceptionnelle sur les bénéfices des grandes entreprises (source indépendante)
  - Où : FIPECO, fiche « L'impôt sur les sociétés », Section sur les taux, paragraphe sur la loi de finances pour 2025
  - Document : https://www.fipeco.fr/fiche/Limp%C3%B4t-sur-les-soci%C3%A9t%C3%A9s ; fichier : aucun
- [ ] `is_taux_contribution_exceptionnelle_basse` : **20,6 %** (PLF 2025)
  - Mesure : Taux de la contribution exceptionnelle pour les sociétés au chiffre d'affaires de 1 à 3 Md€, premier exercice (en % de l'IS dû)
  - Où : Projet de loi de finances pour 2025, évaluations préalables des articles, Article 11, texte proposé, IV. A., page 120
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/PLF-2025_Evaluations%20prealables.pdf ; fichier : `data/raw/impot_societes/plf/plf2025_evaluations_prealables.pdf`

## csg

### Entrée du calcul (26)

- [ ] `csg_rendement_activite_2024` : **108 175 M€** (2024)
  - Mesure : Rendement de la CSG sur les revenus d'activité, tous affectataires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette, tous affectataires », page 55, ligne « CSG sur les revenus d'activité », colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_activite_2025` : **110 670 M€** (2025)
  - Mesure : Rendement de la CSG sur les revenus d'activité, tous affectataires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette, tous affectataires », page 55, ligne « CSG sur les revenus d'activité », colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_activite_2027` : **111 880 M€** (2027 (prévision))
  - Mesure : Rendement de la CSG sur les revenus d'activité, tous affectataires (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette, tous affectataires », page 55, ligne « CSG sur les revenus d'activité », colonne 2027
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_capital_2024` : **17 627 M€** (2024)
  - Mesure : Rendement de la CSG sur les revenus ou produits du capital, tous affectataires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette, tous affectataires », page 55, ligne « CSG sur les revenus ou produits du capital », colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_capital_2025` : **17 590 M€** (2025)
  - Mesure : Rendement de la CSG sur les revenus ou produits du capital, tous affectataires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette, tous affectataires », page 55, ligne « CSG sur les revenus ou produits du capital », colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_capital_2027` : **19 171 M€** (2027 (prévision))
  - Mesure : Rendement de la CSG sur les revenus ou produits du capital, tous affectataires (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette, tous affectataires », page 55, ligne « CSG sur les revenus ou produits du capital », colonne 2027
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_retraites_2024` : **24 812 M€** (2024)
  - Mesure : Rendement de la CSG sur les pensions de retraite (tous taux), tous affectataires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 3 « Décomposition de l'évolution de la CSG sur revenus de remplacement par assiette », ligne « Retraites », page 55, colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_retraites_2025` : **25 439 M€** (2025)
  - Mesure : Rendement de la CSG sur les pensions de retraite (tous taux), tous affectataires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 3 « Décomposition de l'évolution de la CSG sur revenus de remplacement par assiette », ligne « Retraites », page 55, colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_retraites_2027` : **27 558 M€** (2027 (prévision))
  - Mesure : Rendement de la CSG sur les pensions de retraite (tous taux), tous affectataires (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 3 « Décomposition de l'évolution de la CSG sur revenus de remplacement par assiette », ligne « Retraites », page 55, colonne 2027
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_activite_2025` : **9,2 %** (2025)
  - Mesure : Taux de CSG sur les revenus d'activité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus d'activité »
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_retraites_2025` : **8,3 %** (2025)
  - Mesure : Taux plein de CSG sur les revenus de retraite et d'invalidité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus de retraites et d'invalidité (taux plein) »
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_capital_2025` : **9,2 %** (2025)
  - Mesure : Taux de CSG sur les revenus du capital (taux plein et taux réduit)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, lignes « Sur revenus du capital »
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_capital_2027` : **10,6 %** (2027 (prévision))
  - Mesure : Taux plein de CSG sur les revenus du capital après la LFSS 2026 (le taux réduit reste à 9,2 %)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus du capital (taux plein) », colonne 2027 (p)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_rendement_activite_2017` : **68 811 M€** (2017)
  - Mesure : Rendement de la CSG activité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette », page 45, ligne « CSG activité », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_rendement_patrimoine_2017` : **5 044 M€** (2017)
  - Mesure : Rendement de la CSG patrimoine
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette », page 45, ligne « CSG patrimoine », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_rendement_placement_2017` : **5 816 M€** (2017)
  - Mesure : Rendement de la CSG placement
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 1 « Rendement de la CSG par assiette », page 45, ligne « CSG placement », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_rendement_retraites_2017` : **17 232 M€** (2017)
  - Mesure : Rendement de la CSG sur les retraites (tous taux)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 3 « Décomposition de l'évolution de la CSG sur revenu de remplacement par assiette », page 45, ligne « Retraites », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_rendement_retraites_taux_plein_2017` : **15 780 M€** (2017)
  - Mesure : Rendement de la CSG sur les retraites au taux plein
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 3 « Décomposition de l'évolution de la CSG sur revenu de remplacement par assiette », page 45, ligne « Taux plein », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_taux_activite_2017` : **7,5 %** (2017)
  - Mesure : Taux de CSG sur les revenus d'activité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 47, ligne « Sur revenus d'activité », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_taux_retraites_2017` : **6,6 %** (2017)
  - Mesure : Taux plein de CSG sur les revenus de retraite et d'invalidité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 47, ligne « Sur revenus de retraites et d'invalidité (taux plein) », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_taux_capital_2017` : **8,2 %** (2017)
  - Mesure : Taux de CSG sur les revenus du capital
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 47, ligne « Sur revenus du capital », colonne 2017
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_taux_activite_2024` : **9,2 %** (2024)
  - Mesure : Taux de CSG sur les revenus d'activité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus d'activité », colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_activite_2027` : **9,2 %** (2027 (prévision))
  - Mesure : Taux de CSG sur les revenus d'activité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus d'activité », colonne 2027 (p)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_retraites_2024` : **8,3 %** (2024)
  - Mesure : Taux plein de CSG sur les revenus de retraite et d'invalidité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus de retraites et d'invalidité (taux plein) », colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_retraites_2027` : **8,3 %** (2027 (prévision))
  - Mesure : Taux plein de CSG sur les revenus de retraite et d'invalidité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus de retraites et d'invalidité (taux plein) », colonne 2027 (p)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_taux_capital_2024` : **9,2 %** (2024)
  - Mesure : Taux de CSG sur les revenus du capital (taux plein et taux réduit)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 4 « Taux de CSG par risque et par assiette », bloc « Total », page 57, ligne « Sur revenus du capital », colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`

### Référence de validation (8)

- [ ] `csg_hausse_1_7_2018_activite` : **16 052 M€** (2018 (prévision))
  - Mesure : Supplément de rendement en 2018 de la hausse de 1,7 point du taux de CSG sur les revenus d'activité (LFSS 2018, article 7)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 2 « Décomposition de l’évolution de la CSG sur revenus d’activité par assiette », page 45, ligne « Hausse de 1,7 point du taux », colonne 2018 (p)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_hausse_1_7_2018_retraites` : **4 181 M€** (2018 (prévision))
  - Mesure : Supplément de rendement en 2018 de la hausse de 1,7 point du taux plein de CSG sur les retraites (LFSS 2018, article 7)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, tableau 3 « Décomposition de l'évolution de la CSG sur revenu de remplacement par assiette », page 45, ligne « Retraites », sous-ligne « Taux plein », « Hausse de 1,7 point du taux », colonne 2018 (p)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_hausse_1_7_2018_capital` : **2,1 Md€** (2018 (prévision))
  - Mesure : Supplément de rendement en 2018 de la hausse de 1,7 point du taux de CSG sur les revenus du capital (LFSS 2018, article 7)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.3, texte, page 46 (« 2,1 Md€ sur les revenus de capital »)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `csg_hausse_capital_1_4_2026` : **2,8 Md€** (PLFSS 2026 (2026))
  - Mesure : Rendement en 2026 du passage de 9,2 % à 10,6 % du taux de la CSG sur les revenus du patrimoine et des placements (article 6 bis adopté par l'Assemblée nationale en première lecture), toutes administrations publiques
  - Où : Rapport n° 131 (2025-2026), tome I, sur le projet de loi de financement de la sécurité sociale pour 2026, par Élisabeth Doineau et les rapporteurs de la commission des affaires sociales du Sénat, Tableau « Chiffrage pour 2026 des mesures adoptées par l'Assemblée nationale », ligne « Article 6 bis », colonne « Toutes APU », page 112
  - Document : https://www.senat.fr/rap/l25-131-1/l25-131-11.pdf ; fichier : `data/raw/indexation/senat_rapport_plfss2026_tome1.pdf`
- [ ] `csg_valeur_point_activite_2025` : **12 030 M€** (2025)
  - Mesure : Valeur d'un point de CSG sur les revenus d'activité
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 6 « Valeur de point de la CSG par assiette », page 57, ligne « Activité », colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_valeur_point_activite_2027` : **12 160 M€** (2027 (prévision))
  - Mesure : Valeur d'un point de CSG sur les revenus d'activité (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 6 « Valeur de point de la CSG par assiette », page 57, ligne « Activité », colonne 2027 (p)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_valeur_point_capital_2025` : **1 910 M€** (2025)
  - Mesure : Valeur d'un point de CSG sur les revenus du capital
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 6 « Valeur de point de la CSG par assiette », page 57, ligne « Capital », colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `csg_valeur_point_capital_2027` : **1 960 M€** (2027 (prévision))
  - Mesure : Valeur d'un point de CSG sur les revenus du capital (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.3, tableau 6 « Valeur de point de la CSG par assiette », page 57, ligne « Capital », colonne 2027 (p)
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`

## cotisations_patronales

### Entrée du calcul (12)

- [ ] `cotisations_point_prive_2026` : **7 590 M€** (2026 (prévision))
  - Mesure : Valeur d'un point de cotisation déplafonnée des employeurs du secteur privé (régimes de base), rendement théorique d'une hausse d'un point supposant compensée la hausse des exonérations induite
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.2, encadré 2 « Valeurs de point de cotisation déplafonné des actifs des régimes de base », ligne « Secteur privé », colonne 2026, page 51
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `cotisations_point_prive_2025` : **7 380 M€** (2025 (prévision))
  - Mesure : Valeur d'un point de cotisation déplafonnée des employeurs du secteur privé (régimes de base), rendement théorique d'une hausse d'un point supposant compensée la hausse des exonérations induite
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2025 (résultats 2024, prévisions 2025 et 2026), Fiche 1.2, encadré 2 « Valeurs de point de cotisation », ligne « Secteur privé », colonne 2025, page 47
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2025/CCSS_octobre%202025_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2025.pdf`
- [ ] `cotisations_point_prive_2017` : **5 570 M€** (2017)
  - Mesure : Valeur d'un point de cotisation déplafonnée des employeurs du secteur privé (régimes de base), rendement théorique d'une hausse d'un point supposant compensée la hausse des exonérations induite
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, septembre 2018 (résultats 2017, prévisions 2018 et 2019), Fiche 1.2, encadré 1 « Valeur de point de cotisation », ligne « Secteur privé », colonne 2017, page 39
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2018/CCSS_RAPPORT-SEPTEMBRE%202018.pdf ; fichier : `data/raw/csg/ccss_septembre_2018.pdf`
- [ ] `allegements_generaux_total_2024` : **79 562 M€** (2024)
  - Mesure : Allègements généraux et mesures de modulation des taux, tous attributaires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne « Allègements généraux et mesures de modulation des taux », colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_tns_famille_2024` : **832 M€** (2024)
  - Mesure : Réduction du taux de cotisations d'allocations familiales des travailleurs non-salariés
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne correspondante, colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_tns_maladie_2024` : **1 145 M€** (2024)
  - Mesure : Réduction du taux de cotisations d'assurance maladie des travailleurs non salariés
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne correspondante, colonne 2024
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_generaux_total_2025` : **77 554 M€** (2025)
  - Mesure : Allègements généraux et mesures de modulation des taux, tous attributaires
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne « Allègements généraux et mesures de modulation des taux », colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_tns_famille_2025` : **811 M€** (2025)
  - Mesure : Réduction du taux de cotisations d'allocations familiales des travailleurs non-salariés
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne correspondante, colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_tns_maladie_2025` : **1 100 M€** (2025)
  - Mesure : Réduction du taux de cotisations d'assurance maladie des travailleurs non salariés
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne correspondante, colonne 2025
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_generaux_total_2027` : **72 762 M€** (2027 (prévision))
  - Mesure : Allègements généraux et mesures de modulation des taux, tous attributaires (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne « Allègements généraux et mesures de modulation des taux », colonne 2027
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_tns_famille_2027` : **799 M€** (2027 (prévision))
  - Mesure : Réduction du taux de cotisations d'allocations familiales des travailleurs non-salariés (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne correspondante, colonne 2027
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`
- [ ] `allegements_tns_maladie_2027` : **1 010 M€** (2027 (prévision))
  - Mesure : Réduction du taux de cotisations d'assurance maladie des travailleurs non salariés (prévision)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2026 (résultats 2025, prévisions 2026 et 2027), Fiche 1.6, tableau 2 « Les dispositifs d'allégements généraux de sécurité sociale et hors sécurité sociale », page 67, ligne correspondante, colonne 2027
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2026/CCSS-octobre-2026_assemble_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2026.pdf`

### Référence de validation (2)

- [ ] `allegements_generaux_prevision_2025` : **74,5 Md€** (2025 (prévision))
  - Mesure : Coût prévu des allègements généraux en 2025, tous attributaires (« les AG s'élèveraient à 74,5 Md€ »)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2025 (résultats 2024, prévisions 2025 et 2026), Fiche 1.6, texte, page 62
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2025/CCSS_octobre%202025_VDEF.pdf ; fichier : `data/raw/csg/ccss_octobre_2025.pdf`
- [ ] `allegements_generaux_prevision_2024` : **78,7 Md€** (2024 (prévision))
  - Mesure : Coût prévu des allègements généraux en 2024 (« Les allègements généraux s'élèveraient à 78,7 Md€ en 2024 »)
  - Où : Les comptes de la sécurité sociale, rapport à la Commission des comptes de la sécurité sociale, octobre 2024 (résultats 2023, prévisions 2024 et 2025), Fiche 1.6, texte, page 52
  - Document : https://www.securite-sociale.fr/files/live/sites/SSFR/files/medias/CCSS/2024/CCSS-octobre%202024.pdf ; fichier : `data/raw/csg/ccss_octobre_2024.pdf`

## accises_energie

### Entrée du calcul (9)

- [ ] `accises_tarif_trm_2025` : **45,19 €/hl** (2025)
  - Mesure : Tarif réduit de l'accise sur les gazoles du transport routier de marchandises (L. 312-53 du CIBS)
  - Où : Guide 2026 sur la fiscalité des énergies, Page 24, tableau des tarifs réduits, ligne « Transport routier de marchandises »
  - Document : https://www.ecologie.gouv.fr/sites/default/files/documents/Guide%202026%20sur%20fiscalit%C3%A9%20des%20%C3%A9nergies.pdf ; fichier : `data/raw/accises/ministere/guide_2026_fiscalite_energies.pdf`
- [ ] `accises_tarif_transport_collectif_2025` : **39,19 €/hl** (2025)
  - Mesure : Tarif réduit de l'accise sur les gazoles du transport collectif routier de personnes (L. 312-51 du CIBS)
  - Où : Guide 2026 sur la fiscalité des énergies, Page 24, tableau des tarifs réduits, ligne « Transport collectif routier de personnes »
  - Document : https://www.ecologie.gouv.fr/sites/default/files/documents/Guide%202026%20sur%20fiscalit%C3%A9%20des%20%C3%A9nergies.pdf ; fichier : `data/raw/accises/ministere/guide_2026_fiscalite_energies.pdf`
- [ ] `accises_tarif_taxis_gazole_2025` : **30,2 €/hl** (2025)
  - Mesure : Tarif réduit de l'accise sur les gazoles des taxis (L. 312-52 du CIBS)
  - Où : Guide 2026 sur la fiscalité des énergies, Page 24, tableau des tarifs réduits, ligne « Transport de personnes par taxi », gazoles
  - Document : https://www.ecologie.gouv.fr/sites/default/files/documents/Guide%202026%20sur%20fiscalit%C3%A9%20des%20%C3%A9nergies.pdf ; fichier : `data/raw/accises/ministere/guide_2026_fiscalite_energies.pdf`
- [ ] `accises_remboursement_trm_2025` : **1 178 M€** (2025 (prévision du PLF 2026))
  - Mesure : Dépense fiscale 800221, remboursement partiel de l'accise sur les gazoles des véhicules de transport de marchandises d'au moins 7,5 tonnes
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Fiche 800221, impact budgétaire, colonne « Prévision 2025 »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `accises_remboursement_transport_collectif_2025` : **183 M€** (2025 (prévision du PLF 2026))
  - Mesure : Dépense fiscale 800222, remboursement partiel de l'accise sur les gazoles des véhicules de transport public collectif de voyageurs
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Fiche 800222, impact budgétaire, colonne « Prévision 2025 »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `accises_remboursement_taxis_2025` : **59 M€** (2025 (prévision du PLF 2026))
  - Mesure : Dépense fiscale 800220, remboursement partiel de l'accise sur les carburants des taxis
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Fiche 800220, impact budgétaire, colonne « Prévision 2025 »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `ademe_masse_volumique_gazole` : **832 kg/m³** (Base Carbone (page consultée le 9 octobre 2026))
  - Mesure : Masse volumique du gazole (« Gasoil »)
  - Où : Base Carbone, documentation « PCI et masse volumique », Tableau des masses volumiques, ligne « Gasoil » (fichier data/raw/accises/ademe/base_carbone_pci_et_masse_volumique.htm)
  - Document : https://prod-basecarbonesolo.ademe-dri.fr/documentation/UPLOAD_DOC_FR/pci_et_masse_volumique.htm ; fichier : `data/raw/accises/ademe/base_carbone_pci_et_masse_volumique.htm`
- [ ] `ademe_masse_volumique_essence` : **747 kg/m³** (Base Carbone (page consultée le 9 octobre 2026))
  - Mesure : Masse volumique de l'essence
  - Où : Base Carbone, documentation « PCI et masse volumique », Tableau des masses volumiques, ligne « Essence » (fichier data/raw/accises/ademe/base_carbone_pci_et_masse_volumique.htm)
  - Document : https://prod-basecarbonesolo.ademe-dri.fr/documentation/UPLOAD_DOC_FR/pci_et_masse_volumique.htm ; fichier : `data/raw/accises/ademe/base_carbone_pci_et_masse_volumique.htm`
- [ ] `ademe_masse_volumique_fioul_domestique` : **845 kg/m³** (Base Carbone (page consultée le 9 octobre 2026))
  - Mesure : Masse volumique du fioul domestique
  - Où : Base Carbone, documentation « PCI et masse volumique », Tableau des masses volumiques, ligne « Fioul domestique » (fichier data/raw/accises/ademe/base_carbone_pci_et_masse_volumique.htm)
  - Document : https://prod-basecarbonesolo.ademe-dri.fr/documentation/UPLOAD_DOC_FR/pci_et_masse_volumique.htm ; fichier : `data/raw/accises/ademe/base_carbone_pci_et_masse_volumique.htm`

### Référence de validation (2)

- [ ] `accises_ticpe_brute_totale_2023` : **31,7 Md€** (2023 (exécution))
  - Mesure : Recette brute totale de l'accise sur les produits énergétiques (ex-TICPE), avant transferts et remboursements
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome I (recettes), Page 28, tableau de la ligne 1501, ligne « TICPE brute totale », colonne 2023
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_1_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome1.pdf`
- [ ] `accises_ticpe_brute_totale_2024` : **31,6 Md€** (2024 (exécution))
  - Mesure : Recette brute totale de l'accise sur les produits énergétiques (ex-TICPE), avant transferts et remboursements
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome I (recettes), Page 28, tableau de la ligne 1501, ligne « Accise sur les produits énergétiques (ex-TICPE) brute totale », colonne 2024
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087930/file/PLF%202026%20-%20V%26M%20TI%20-%20Evaluations%20des%20recettes.pdf ; fichier : `data/raw/tva/plf2026_voies_et_moyens_tome1.pdf`

### Non repéré (3)

- [ ] `accises_tarif_gnr_non_agricole_2024` : **24,81 €/hl** (2024)
  - Mesure : Tarif de l'accise sur le gazole non routier à usage non agricole (€/MWh, égal au tarif en €/hl pour les gazoles)
  - Où : Guide 2026 sur la fiscalité des énergies, Page 23, tableau « Tarif de l'accise sur le gazole non routier à usage non agricole », colonne 2024
  - Document : https://www.ecologie.gouv.fr/sites/default/files/documents/Guide%202026%20sur%20fiscalit%C3%A9%20des%20%C3%A9nergies.pdf ; fichier : `data/raw/accises/ministere/guide_2026_fiscalite_energies.pdf`
- [ ] `accises_ticpe_comptabilite_nationale_2024_fipeco` : **30,2 Md€** (2024 (comptabilité nationale, INSEE))
  - Mesure : Produit de la TICPE en comptabilité nationale (source indépendante, non utilisée pour la validation)
  - Où : FIPECO, fiche « Les taxes sur les carburants », Section « B) Le rendement budgétaire », première phrase
  - Document : https://www.fipeco.fr/fiche/Les-taxes-sur-les-carburants ; fichier : aucun
- [ ] `accises_ticpe_comptabilite_nationale_2025_fipeco` : **30,5 Md€** (2025 (comptabilité nationale, INSEE))
  - Mesure : Produit de la TICPE en comptabilité nationale (source indépendante, non utilisée pour la validation)
  - Où : FIPECO, fiche « Les taxes sur les carburants », Section « B) Le rendement budgétaire », première phrase
  - Document : https://www.fipeco.fr/fiche/Les-taxes-sur-les-carburants ; fichier : aucun

## depenses_fiscales

### Référence de validation (8)

- [ ] `depenses_fiscales_impot_revenu_realisation_2023` : **38 735 M€** (2023 (réalisation du PLF 2025))
  - Mesure : Coût réalisé des dépenses fiscales de la partie « Impôt sur le revenu » du tome II
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Impôt sur le revenu », colonne « Coût 2023 », pages 13 et 14 du fichier PDF
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_impot_revenu_et_societes_realisation_2023` : **13 977 M€** (2023 (réalisation du PLF 2025))
  - Mesure : Coût réalisé des dépenses fiscales de la partie « Impôt sur le revenu et impôt sur les sociétés » du tome II
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Impôt sur le revenu et impôt sur les sociétés », colonne « Coût 2023 », pages 13 et 14 du fichier PDF
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_impot_societes_realisation_2023` : **9 179 M€** (2023 (réalisation du PLF 2025))
  - Mesure : Coût réalisé des dépenses fiscales de la partie « Impôt sur les sociétés » du tome II
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Impôt sur les sociétés », colonne « Coût 2023 », pages 13 et 14 du fichier PDF
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_impot_revenu_realisation_2024` : **42 079 M€** (2024 (réalisation du PLF 2026))
  - Mesure : Coût réalisé des dépenses fiscales de la partie « Impôt sur le revenu » du tome II
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Impôt sur le revenu », colonne « Coût 2024 », pages 14 et 15 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_impot_revenu_et_societes_realisation_2024` : **14 111 M€** (2024 (réalisation du PLF 2026))
  - Mesure : Coût réalisé des dépenses fiscales de la partie « Impôt sur le revenu et impôt sur les sociétés » du tome II
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Impôt sur le revenu et impôt sur les sociétés », colonne « Coût 2024 », pages 14 et 15 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_impot_societes_realisation_2024` : **3 913 M€** (2024 (réalisation du PLF 2026))
  - Mesure : Coût réalisé des dépenses fiscales de la partie « Impôt sur les sociétés » du tome II
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Impôt sur les sociétés », colonne « Coût 2024 », pages 14 et 15 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_ccomptes_total_2023_definitif` : **82,923 Md€** (2023 (montant définitif du PLF 2025))
  - Mesure : Coût total définitif des dépenses fiscales de 2023, nouvelle convention TVA
  - Où : Cour des comptes, « Le budget de l'État en 2024 (résultats et gestion) - Dépenses fiscales », note d'analyse de l'exécution budgétaire, tableau « écarts de chiffrage des dépenses fiscales par année de référence sur le fondement de la nouvelle convention TVA (2022 - 2025) », page 18, ligne « Montant définitif en PLF N+2 », colonne 2023
  - Document : https://www.ccomptes.fr/sites/default/files/2025-04/NEB-2024-Depenses-fiscales.pdf ; fichier : `data/raw/niches_fiscales/ccomptes_neb_2024_depenses_fiscales.pdf`
- [ ] `depenses_fiscales_ccomptes_total_2024_revise` : **83,292 Md€** (2024 (montant révisé du PLF 2025))
  - Mesure : Coût total révisé des dépenses fiscales de 2024, nouvelle convention TVA
  - Où : Cour des comptes, « Le budget de l'État en 2024 (résultats et gestion) - Dépenses fiscales », note d'analyse de l'exécution budgétaire, tableau « écarts de chiffrage des dépenses fiscales par année de référence sur le fondement de la nouvelle convention TVA (2022 - 2025) », page 18, ligne « Montant révisé en PLF N+1 », colonne 2024
  - Document : https://www.ccomptes.fr/sites/default/files/2025-04/NEB-2024-Depenses-fiscales.pdf ; fichier : `data/raw/niches_fiscales/ccomptes_neb_2024_depenses_fiscales.pdf`

### Non repéré (11)

- [ ] `depenses_fiscales_total_plf2024_2022` : **85 616 M€** (2022 (réalisation du PLF 2024))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2024, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2022 », page 14 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/content/download/705208/file/Evaluation%20des%20voies%20et%20moyens%20-%20Tome%20II.pdf ; fichier : `data/raw/niches_fiscales/plf2024_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2024_2023` : **81 344 M€** (2023 (prévision du PLF 2024))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2024, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2023 », page 14 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/content/download/705208/file/Evaluation%20des%20voies%20et%20moyens%20-%20Tome%20II.pdf ; fichier : `data/raw/niches_fiscales/plf2024_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2024_2024` : **78 741 M€** (2024 (prévision du PLF 2024))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2024, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2024 », page 14 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/content/download/705208/file/Evaluation%20des%20voies%20et%20moyens%20-%20Tome%20II.pdf ; fichier : `data/raw/niches_fiscales/plf2024_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2025_2023` : **82 923 M€** (2023 (réalisation du PLF 2025))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2023 », pages 13 et 14 du fichier PDF
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2025_2024` : **83 292 M€** (2024 (prévision du PLF 2025))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2024 », pages 13 et 14 du fichier PDF
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2025_2025` : **85 098 M€** (2025 (prévision du PLF 2025))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2025 », pages 13 et 14 du fichier PDF
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_2_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2026_2024` : **89 406 M€** (2024 (réalisation du PLF 2026))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2024 », pages 14 et 15 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2026_2025` : **91 834 M€** (2025 (prévision du PLF 2026))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2025 », pages 14 et 15 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_total_plf2026_2026` : **88 269 M€** (2026 (prévision du PLF 2026))
  - Mesure : Coût total des dépenses fiscales, convention du tome II (une dépense non chiffrée reprend le dernier montant chiffré)
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome II (dépenses fiscales), Présentation générale, tableau « Dépenses fiscales par impôt », ligne « Total », colonne « Coût 2026 », pages 14 et 15 du fichier PDF
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087933/file/Voies_et_moyens_Tome_2_2026.pdf ; fichier : `data/raw/niches_fiscales/plf2026_voies_et_moyens_tome2.pdf`
- [ ] `depenses_fiscales_ccomptes_total_2023_initial` : **77,676 Md€** (2023 (prévision initiale du PLF 2023, recalculée en nouvelle convention TVA))
  - Mesure : Coût total des dépenses fiscales prévu pour 2023 (source indépendante, non utilisée par le modèle)
  - Où : Cour des comptes, « Le budget de l'État en 2024 (résultats et gestion) - Dépenses fiscales », note d'analyse de l'exécution budgétaire, tableau « écarts de chiffrage des dépenses fiscales par année de référence sur le fondement de la nouvelle convention TVA (2022 - 2025) », page 18, ligne « Montant prévisionnel du PLF N », colonne 2023
  - Document : https://www.ccomptes.fr/sites/default/files/2025-04/NEB-2024-Depenses-fiscales.pdf ; fichier : `data/raw/niches_fiscales/ccomptes_neb_2024_depenses_fiscales.pdf`
- [ ] `depenses_fiscales_ccomptes_ecart_moyen_n_n2` : **3,4 %** (2018 à 2023 (ancienne convention TVA))
  - Mesure : Écart moyen entre le coût total prévu en N et le coût définitif publié en N+2 (source indépendante, non utilisée par le modèle)
  - Où : Cour des comptes, « Le budget de l'État en 2024 (résultats et gestion) - Dépenses fiscales », note d'analyse de l'exécution budgétaire, Page 17, encadré sur les écarts de prévision 2018-2025, « Le différentiel est en moyenne de 3,4 % sur la période considérée entre les prévisions en N et N+2 »
  - Document : https://www.ccomptes.fr/sites/default/files/2025-04/NEB-2024-Depenses-fiscales.pdf ; fichier : `data/raw/niches_fiscales/ccomptes_neb_2024_depenses_fiscales.pdf`

## credits_missions

### Référence de validation (3)

- [ ] `credits_missions_depenses_constatees_2023` : **377,712 Md€** (exercice 2023)
  - Mesure : Dépenses constatées (crédits de paiement) des programmes des missions du levier, somme calculée par le moteur sur l'annexe 1 (budget général, hors remboursements et dégrèvements, relations avec les collectivités territoriales, crédits non répartis, régimes sociaux et de retraite et programmes absents du PLF 2026)
  - Où : Projet de loi relatif aux résultats de la gestion et portant approbation des comptes de l'année 2023 (PLRG 2023), données en CSV, Fichier annexe1_etat_cp_2023, colonne « Depenses_constatees », somme des lignes du périmètre (fr_budget.agrege.credits_missions.total_execution(2023))
  - Document : https://data.economie.gouv.fr/explore/dataset/projet-de-loi-relatif-aux-resultats-de-la-gestion-et-portant-approbation-des-comptes-de-lannee-plrg-2023/ ; fichier : `data/raw/credits_missions/plrg2023_annexe1_etat_cp.csv`
- [ ] `credits_missions_depenses_constatees_2024` : **371,94 Md€** (exercice 2024)
  - Mesure : Dépenses constatées (crédits de paiement) des programmes des missions du levier, somme calculée par le moteur sur l'annexe 1 (budget général, hors remboursements et dégrèvements, relations avec les collectivités territoriales, crédits non répartis, régimes sociaux et de retraite et programmes absents du PLF 2026)
  - Où : Projet de loi relatif aux résultats de la gestion et portant approbation des comptes de l'année 2024 (PLRG 2024), données en CSV, Fichier annexe1_etat_cp_2024, colonne « Depenses_constatees », somme des lignes du périmètre (fr_budget.agrege.credits_missions.total_execution(2024))
  - Document : https://data.economie.gouv.fr/explore/dataset/plrg-2024/ ; fichier : `data/raw/credits_missions/plrg2024_annexe1_etat_cp.csv`
- [ ] `credits_missions_depenses_constatees_2025` : **375,091 Md€** (exercice 2025)
  - Mesure : Dépenses constatées (crédits de paiement) des programmes des missions du levier, somme calculée par le moteur sur l'annexe 1 (budget général, hors remboursements et dégrèvements, relations avec les collectivités territoriales, crédits non répartis, régimes sociaux et de retraite et programmes absents du PLF 2026)
  - Où : Projet de loi relatif aux résultats de la gestion et portant approbation des comptes de l'année 2025 (PLRG 2025), données en CSV, Fichier annexe1_etat_cp_2025, colonne « Depenses_constatees », somme des lignes du périmètre (fr_budget.agrege.credits_missions.total_execution(2025))
  - Document : https://data.economie.gouv.fr/explore/dataset/projet-de-loi-relatif-aux-resultats-de-la-gestion-et-portant-approbation-des-comptes-de-lannee-plrg-2025/ ; fichier : `data/raw/credits_missions/plrg2025_annexe1_etat_cp.csv`

## remunerations_publiques

### Entrée du calcul (24)

- [ ] `remunerations_tib_fpe_ensemble` : **2 894 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, ensemble des fonctionnaires (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « Ensemble », ligne « Traitement brut », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpe_ensemble` : **951 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, ensemble des fonctionnaires (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « Ensemble », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fpe_a` : **3 244 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie A (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « A », ligne « Traitement brut », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpe_a` : **915 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie A (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « A », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fpe_b` : **2 212 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie B (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « B », ligne « Traitement brut », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpe_b` : **1 163 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie B (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « B », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fpe_c` : **1 981 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie C (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « C », ligne « Traitement brut », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpe_c` : **832 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie C (FPE)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « C », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPE
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fpt_ensemble` : **2 127 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, ensemble des fonctionnaires (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « Ensemble », ligne « Traitement brut », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpt_ensemble` : **719 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, ensemble des fonctionnaires (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « Ensemble », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fpt_a` : **3 033 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie A (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « A », ligne « Traitement brut », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpt_a` : **1 291 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie A (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « A », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fpt_b` : **2 235 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie B (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « B », ligne « Traitement brut », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpt_b` : **825 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie B (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « B », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fpt_c` : **1 944 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie C (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « C », ligne « Traitement brut », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fpt_c` : **595 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie C (FPT)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « C », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPT
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fph_ensemble` : **2 491 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, ensemble des fonctionnaires (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « Ensemble », ligne « Traitement brut », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fph_ensemble` : **765 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, ensemble des fonctionnaires (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « Ensemble », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fph_a` : **2 803 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie A (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « A », ligne « Traitement brut », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fph_a` : **931 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie A (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « A », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fph_b` : **2 388 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie B (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « B », ligne « Traitement brut », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fph_b` : **726 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie B (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « B », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_tib_fph_c` : **2 103 €** (2023)
  - Mesure : Traitement brut mensuel moyen en EQTP, fonctionnaires de catégorie C (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « C », ligne « Traitement brut », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`
- [ ] `remunerations_primes_fph_c` : **533 €** (2023)
  - Mesure : Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement, mensuels moyens en EQTP, fonctionnaires de catégorie C (FPH)
  - Où : Rapport annuel sur l'état de la fonction publique, édition 2025 (Faits et chiffres, données 2023), Figure 9, page 113, bloc « C », ligne « Primes et rémunérations annexes, indemnité de résidence et supplément familial de traitement », colonne FPH
  - Document : https://www.fonction-publique.gouv.fr/files/files/publications/rapport-annuel/ra_2025.pdf ; fichier : `data/raw/remunerations/dgafp_rapport_annuel_2025.pdf`

### Référence de validation (13)

- [ ] `remunerations_point_3_5_fpe_2023` : **3,6 Md€** (2023 (année pleine))
  - Mesure : Coût de la revalorisation de 3,5 % du point d'indice pour la FPE en 2023, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 3,5 % », colonnes 2023, FPE
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_3_5_fpt_2023` : **2,4 Md€** (2023 (année pleine))
  - Mesure : Coût de la revalorisation de 3,5 % du point d'indice pour la FPT en 2023, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 3,5 % », colonnes 2023, FPT
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_3_5_fph_2023` : **1,6 Md€** (2023 (année pleine))
  - Mesure : Coût de la revalorisation de 3,5 % du point d'indice pour la FPH en 2023, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 3,5 % », colonnes 2023, FPH
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_3_5_total_2023` : **7,6 Md€** (2023 (année pleine))
  - Mesure : Coût de la revalorisation de 3,5 % du point d'indice en 2023, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 3,5 % », colonnes 2023, Total
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_1_5_fpe_2024` : **1,5 Md€** (2024 (année pleine))
  - Mesure : Coût de la revalorisation de 1,5 % du point d'indice pour la FPE en 2024, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 1,5 % », colonnes 2024, FPE
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_1_5_fpt_2024` : **0,9 Md€** (2024 (année pleine))
  - Mesure : Coût de la revalorisation de 1,5 % du point d'indice pour la FPT en 2024, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 1,5 % », colonnes 2024, FPT
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_1_5_fph_2024` : **0,71 Md€** (2024 (année pleine))
  - Mesure : Coût de la revalorisation de 1,5 % du point d'indice pour la FPH en 2024, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 1,5 % », colonnes 2024, FPH
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_1_5_total_2024` : **3,2 Md€** (2024 (année pleine))
  - Mesure : Coût de la revalorisation de 1,5 % du point d'indice en 2024, première année pleine (réponses du Gouvernement au questionnaire budgétaire)
  - Où : Avis n° 134 (2023-2024) sur le projet de loi de finances pour 2024, tome V, « Fonction publique », par Catherine Di Folco, commission des lois du Sénat, Tableau « Coûts des dernières revalorisations du point d'indice », page 8, ligne « + 1,5 % », colonnes 2024, Total
  - Document : https://www.senat.fr/rap/a23-134-5/a23-134-51.pdf ; fichier : `data/raw/remunerations/senat_avis_plf2024_fonction_publique.pdf`
- [ ] `remunerations_point_1_ccomptes_2017_total` : **2,07 Md€** (juin 2017)
  - Mesure : Surcoût d'une hausse de 1 % de la valeur du point pour l'ensemble de la fonction publique (Cour des comptes)
  - Où : Cour des comptes, « La situation et les perspectives des finances publiques », juin 2017 (copie de la DILA sur vie-publique.fr), Chapitre IV, I, A, 1, a, page 141 : « une augmentation de 1 % de la valeur du point se traduit par un surcoût de 2 070 M€ pour l'ensemble de la fonction publique » (sha256 760ebe3d05b1decc3943367894b1a05b5ac30da69f835d6a7dc9b45df9385ef7)
  - Document : https://www.vie-publique.fr/files/rapport/pdf/174000536.pdf ; fichier : aucun
- [ ] `remunerations_point_1_ccomptes_2017_fpe` : **0,88 Md€** (juin 2017)
  - Mesure : Même surcoût pour l'État, y compris les opérateurs (Cour des comptes)
  - Où : Cour des comptes, « La situation et les perspectives des finances publiques », juin 2017 (copie de la DILA sur vie-publique.fr), Page 141 : « dont 880 M€ pour l'État (y compris les opérateurs) »
  - Document : https://www.vie-publique.fr/files/rapport/pdf/174000536.pdf ; fichier : aucun
- [ ] `remunerations_point_1_ccomptes_2017_fpt` : **0,64 Md€** (juin 2017)
  - Mesure : Même surcoût pour les collectivités territoriales (Cour des comptes)
  - Où : Cour des comptes, « La situation et les perspectives des finances publiques », juin 2017 (copie de la DILA sur vie-publique.fr), Page 141 : « 640 M€ pour les collectivités territoriales »
  - Document : https://www.vie-publique.fr/files/rapport/pdf/174000536.pdf ; fichier : aucun
- [ ] `remunerations_point_1_ccomptes_2017_fph` : **0,55 Md€** (juin 2017)
  - Mesure : Même surcoût pour les hôpitaux (Cour des comptes)
  - Où : Cour des comptes, « La situation et les perspectives des finances publiques », juin 2017 (copie de la DILA sur vie-publique.fr), Page 141 : « 550 M€ pour les hôpitaux »
  - Document : https://www.vie-publique.fr/files/rapport/pdf/174000536.pdf ; fichier : aucun
- [ ] `remunerations_point_1_fipeco_2026_total` : **2,5 Md€** (juillet 2026)
  - Mesure : Coût d'une hausse de 1 % du point de la fonction publique, hors cotisations des employeurs (Fipeco ; source de second rang)
  - Où : FIPECO, fiche « Le niveau et l'évolution de la masse salariale publique », Partie B-2 : « Chaque augmentation de 1,0 % du point de la fonction publique a un coût (hors cotisations des employeurs) de 1 000 M€ pour l'Etat, 200 M€ pour ses opérateurs, 700 M€ pour les administrations locales et 700 M€ pour les administrations sociales […] soit un total de 2,5 Md€ » (sha256 ad5ed76725d964a02f0e705ff02d1cdd6dd283c86838f65ddf3e147085f001f7)
  - Document : https://www.fipeco.fr/fiche/Le-niveau-et-l%C3%A9volution-de-la-masse-salariale-publique ; fichier : aucun

## indexation_pensions_prestations

### Entrée du calcul (1)

- [ ] `indexation_mois_revalorisation_pensions` : **1 mois** (PLFSS 2027)
  - Mesure : Mois de la revalorisation légale des pensions de retraite (« la loi garantit aujourd'hui la revalorisation automatique des pensions au 1er janvier »)
  - Où : Projet de loi de financement de la sécurité sociale pour 2027, n° 3211 (exposé des motifs et annexe sur les prévisions de recettes et objectifs de dépenses), Exposé des motifs de l'article 35, page 106
  - Document : https://www.assemblee-nationale.fr/dyn/17/textes/l17b3211_projet-loi.pdf ; fichier : `data/raw/indexation/plfss2027_projet_loi.pdf`

### Référence de validation (10)

- [ ] `indexation_gel_2026_apu` : **3,6 Md€** (PLFSS 2026 (2026))
  - Mesure : Économie en 2026 du maintien des prestations sociales, y compris les pensions de retraite, à leur niveau de 2025 (article 44), pour l'ensemble des administrations publiques (2,5 Md€ pour la sécurité sociale, 1,1 Md€ pour l'État), nette de l'effet sur la CSG
  - Où : Projet de loi de financement de la sécurité sociale pour 2026, n° 1907 (exposé des motifs et annexe sur les prévisions de recettes et objectifs de dépenses), Exposé des motifs de l'article 44, page 138 ; le rapport du Sénat n° 131 (tome I, page 134, note 2) précise que les 2,5 Md€ de la sécurité sociale sont nets de 0,2 Md€ de CSG
  - Document : https://www.assemblee-nationale.fr/dyn/17/textes/l17b1907_projet-loi.pdf ; fichier : `data/raw/indexation/plfss2026_projet_loi.pdf`
- [ ] `indexation_gel_2026_familiales` : **0,3 Md€** (PLFSS 2026 (2026))
  - Mesure : Économie en 2026 du gel des prestations familiales (prestation d'accueil du jeune enfant, allocations familiales, complément familial, allocation de soutien familial, allocation de rentrée scolaire, allocation forfaitaire en cas de décès d'un enfant), selon l'étude d'impact du PLFSS 2026 citée par la rapporteure de la branche vieillesse
  - Où : Rapport n° 131 (2025-2026), tome I, sur le projet de loi de financement de la sécurité sociale pour 2026, par Élisabeth Doineau et les rapporteurs de la commission des affaires sociales du Sénat, Audition de la CNAF, question de Mme Pascale Gruny, page 164
  - Document : https://www.senat.fr/rap/l25-131-1/l25-131-11.pdf ; fichier : `data/raw/indexation/senat_rapport_plfss2026_tome1.pdf`
- [ ] `indexation_sous_indexation_0_5_2027` : **1,5 Md€** (PLFSS 2026, lettre rectificative (2027))
  - Mesure : Rendement en 2027 d'une sous-indexation supplémentaire de 0,5 point des pensions de retraite de base (lettre rectificative du 23 octobre 2025)
  - Où : Rapport n° 131 (2025-2026), tome I, sur le projet de loi de financement de la sécurité sociale pour 2026, par Élisabeth Doineau et les rapporteurs de la commission des affaires sociales du Sénat, Page 101 (« a majoré la sous-indexation en 2027 de 0,5 point, soit 1,5 milliard d'euros ») ; aussi page 34
  - Document : https://www.senat.fr/rap/l25-131-1/l25-131-11.pdf ; fichier : `data/raw/indexation/senat_rapport_plfss2026_tome1.pdf`
- [ ] `indexation_gel_familiales_2027` : **0,5 Md€** (PLFSS 2027 (2027))
  - Mesure : Rendement attendu en 2027 du maintien des prestations familiales à leur niveau de 2026 (pas de revalorisation au 1er avril 2027)
  - Où : Projet de loi de financement de la sécurité sociale pour 2027, n° 3211 (exposé des motifs et annexe sur les prévisions de recettes et objectifs de dépenses), Annexe, solde de la branche famille, page 134
  - Document : https://www.assemblee-nationale.fr/dyn/17/textes/l17b3211_projet-loi.pdf ; fichier : `data/raw/indexation/plfss2027_projet_loi.pdf`
- [ ] `indexation_inflation_hors_tabac_2025_plfss2026` : **1 %** (PLFSS 2026 (prévision pour 2025))
  - Mesure : Inflation hors tabac prévue pour 2025, qui détermine la revalorisation légale de 2026
  - Où : Projet de loi de financement de la sécurité sociale pour 2026, n° 1907 (exposé des motifs et annexe sur les prévisions de recettes et objectifs de dépenses), Annexe, tableau des hypothèses d'évolution, ligne « Inflation hors tabac », colonne 2025 (p), page 152
  - Document : https://www.assemblee-nationale.fr/dyn/17/textes/l17b1907_projet-loi.pdf ; fichier : `data/raw/indexation/plfss2026_projet_loi.pdf`
- [ ] `indexation_inflation_hors_tabac_2026_plfss2027` : **2,1 %** (PLFSS 2027 (prévision pour 2026))
  - Mesure : Inflation hors tabac prévue pour 2026, qui détermine la revalorisation légale de 2027
  - Où : Projet de loi de financement de la sécurité sociale pour 2027, n° 3211 (exposé des motifs et annexe sur les prévisions de recettes et objectifs de dépenses), Annexe, tableau des hypothèses, ligne « Inflation hors tabac », colonne 2026 (p), page 127
  - Document : https://www.assemblee-nationale.fr/dyn/17/textes/l17b3211_projet-loi.pdf ; fichier : `data/raw/indexation/plfss2027_projet_loi.pdf`
- [ ] `indexation_gel_aah_2026` : **122,4 M€** (PLFSS 2026 (2026))
  - Mesure : Économie attendue en 2026 sur l'AAH de l'« année blanche » (absence de revalorisation légale prévue au V de l'article 44 du PLFSS 2026)
  - Où : Rapport général n° 139 (2025-2026), tome III, annexe 29, « Solidarité, insertion et égalité des chances », commission des finances du Sénat, Partie consacrée à l'AAH, page 27
  - Document : https://www.senat.fr/rap/l25-139-329/l25-139-3291.pdf ; fichier : `data/raw/prime_activite/senat_rapport_special_siec_plf2026.pdf`
- [ ] `indexation_pensions_ipp_inflation_1_0_2026` : **2,4 Md€** (octobre 2025 (inflation de 1 %))
  - Mesure : Rendement en 2026 d'un gel des pensions de retraite de base (complémentaires non gelées), inflation de 1 % (IPP)
  - Où : IPP, « Actualisation de l'estimation de rendement de l'année blanche », Tableau, colonne « Inflation à 1 % (septembre 2025) », ligne « dont pensions de retraite » ; NB2 : retraites complémentaires non gelées (sha256 765f48922ade283e987d0345f7e651d36d0a299631cfff494fc4672fb4435dcf)
  - Document : https://www.ipp.eu/actualisation-de-lestimation-de-rendement-de-lannee-blanche/ ; fichier : aucun
- [ ] `indexation_pensions_ipp_inflation_1_3_2026` : **3 Md€** (juin 2025 (inflation de 1,3 %))
  - Mesure : Rendement en 2026 d'un gel des pensions de retraite de base, inflation de 1,3 % (IPP)
  - Où : IPP, « Actualisation de l'estimation de rendement de l'année blanche », Tableau, colonne « Inflation à 1,3 % (juin 2025) », ligne « dont pensions de retraite » (sha256 765f48922ade283e987d0345f7e651d36d0a299631cfff494fc4672fb4435dcf)
  - Document : https://www.ipp.eu/actualisation-de-lestimation-de-rendement-de-lannee-blanche/ ; fichier : aucun
- [ ] `indexation_pensions_gel_2026_hcfp` : **2,9 Md€** (PLF et PLFSS 2026 (octobre 2025, inflation hors tabac de 1,0 %))
  - Mesure : Économie brute en 2026 de l'absence d'indexation des retraites sur l'inflation, CAS pensions compris (scénario du Gouvernement cité par le HCFP)
  - Où : Haut Conseil des finances publiques, avis n° HCFP-2025-5 relatif aux projets de lois de finances et de financement de la sécurité sociale pour l'année 2026, 9 octobre 2025, Page 21, note 10 : « Ces 3,6 Md€ […] se décomposeraient en 2,9 Md€ de l'absence d'indexation des retraites sur l'inflation (dont 0,8 Md€ sur le CAS pensions), 1,1 Md€ sur l'absence d'indexation des autres prestations sociales, −0,4 Md€ de moindres recettes d'IR et CSG découlant de ces mesures » (sha256 130ae291dcad2c898327892305f1c8af79efaa836fd7e371d8fbfe3cd67b04ae)
  - Document : https://www.hcfp.fr/sites/default/files/2025-10/Avis%20HCFP%202025%20%E2%80%93%205%20PLF-PLFSS%202026_0.pdf ; fichier : aucun

### Non repéré (1)

- [ ] `indexation_gel_2026_retour_csg` : **0,2 Md€** (PLFSS 2026 (2026))
  - Mesure : Effet retour du gel des prestations de 2026 sur la CSG sur les revenus de remplacement (moindres recettes de la sécurité sociale)
  - Où : Rapport n° 131 (2025-2026), tome I, sur le projet de loi de financement de la sécurité sociale pour 2026, par Élisabeth Doineau et les rapporteurs de la commission des affaires sociales du Sénat, Tableau des mesures du PLFSS, page 134, note 2 (« Avant cet effet retour, ce gain est de 2,7 milliards d'euros »)
  - Document : https://www.senat.fr/rap/l25-131-1/l25-131-11.pdf ; fichier : `data/raw/indexation/senat_rapport_plfss2026_tome1.pdf`

## minima_prime_activite

### Entrée du calcul (4)

- [ ] `pa_pente_baisse_2025_points` : **1,15 point** (2025)
  - Mesure : Baisse de la fraction des revenus professionnels prise en compte dans le calcul de la prime d'activité (décret n° 2025-292 du 29 mars 2025), de 61 % à 59,85 %
  - Où : Note de présentation de la mission « Solidarité, insertion et égalité des chances », projet de loi de finances pour 2026, commission des finances du Sénat, Encadré « La modification de la pente de la prime d'activité en 2025 », pages 15 et 16
  - Document : https://www.senat.fr/fileadmin/cru-1762483659/Commissions/Finances/2025-2026/PLF_2026/NP/SIEC_NP_PLF_2026.pdf ; fichier : `data/raw/prime_activite/senat_note_presentation_siec_plf2026.pdf`
- [ ] `pa_pente_rendement_annee_pleine` : **500 M€** (2025 (année pleine))
  - Mesure : Rendement en année pleine de la baisse de 1,15 point de la pente de la prime d'activité, selon l'administration (« jusqu'à 500 millions d'euros en année pleine »)
  - Où : Note de présentation de la mission « Solidarité, insertion et égalité des chances », projet de loi de finances pour 2026, commission des finances du Sénat, Partie I, B, 2, page 15
  - Document : https://www.senat.fr/fileadmin/cru-1762483659/Commissions/Finances/2025-2026/PLF_2026/NP/SIEC_NP_PLF_2026.pdf ; fichier : `data/raw/prime_activite/senat_note_presentation_siec_plf2026.pdf`
- [ ] `pa_depense_2024` : **10,5 Md€** (2024)
  - Mesure : Masses financières versées au titre de la prime d'activité en 2024 (« plus de 10,5 milliards d'euros »)
  - Où : Note de présentation de la mission « Solidarité, insertion et égalité des chances », projet de loi de finances pour 2026, commission des finances du Sénat, Partie I, B, 2, page 14
  - Document : https://www.senat.fr/fileadmin/cru-1762483659/Commissions/Finances/2025-2026/PLF_2026/NP/SIEC_NP_PLF_2026.pdf ; fichier : `data/raw/prime_activite/senat_note_presentation_siec_plf2026.pdf`
- [ ] `pa_credits_plf2026` : **9,3 Md€** (PLF 2026)
  - Mesure : Crédits prévus au titre de la prime d'activité en PLF 2026 (AE et CP)
  - Où : Note de présentation de la mission « Solidarité, insertion et égalité des chances », projet de loi de finances pour 2026, commission des finances du Sénat, Partie I, B, 2, page 15
  - Document : https://www.senat.fr/fileadmin/cru-1762483659/Commissions/Finances/2025-2026/PLF_2026/NP/SIEC_NP_PLF_2026.pdf ; fichier : `data/raw/prime_activite/senat_note_presentation_siec_plf2026.pdf`

### Référence de validation (1)

- [ ] `pa_pente_moindre_depense_2025` : **290 M€** (2025)
  - Mesure : Moindres dépenses de prime d'activité en 2025 dues au décret du 29 mars 2025 (diminution de la pente de 1,15 point)
  - Où : Rapport général n° 139 (2025-2026), tome III, annexe 29, « Solidarité, insertion et égalité des chances », commission des finances du Sénat, Commentaire de l'article 79, page 55
  - Document : https://www.senat.fr/rap/l25-139-329/l25-139-3291.pdf ; fichier : `data/raw/prime_activite/senat_rapport_special_siec_plf2026.pdf`

## dotations_collectivites

### Entrée du calcul (1)

- [ ] `dotations_dgf_regions_reintegree_2026` : **5 172 M€** (2026 (PLF 2026))
  - Mesure : Montant des fractions de TVA attribuées aux régions depuis 2018 réintégré dans la DGF en 2026 (mesure de périmètre)
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome I (recettes), Commentaire de la ligne 3101 (prélèvement au titre de la DGF), pages 77 et 78
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087930/file/PLF%202026%20-%20V%26M%20TI%20-%20Evaluations%20des%20recettes.pdf ; fichier : `data/raw/tva/plf2026_voies_et_moyens_tome1.pdf`

### Référence de validation (4)

- [ ] `dotations_dgf_execution_2023` : **26 929,622 M€** (exercice 2023 (exécution))
  - Mesure : Prélèvement sur recettes au titre de la dotation globale de fonctionnement (ligne 3101), exécution
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome I (recettes), Tableau « Prélèvements sur les recettes de l'État au profit des collectivités territoriales », ligne 3101, colonne « Exécution 2023 »
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_1_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome1.pdf`
- [ ] `dotations_dgf_execution_2024` : **27 238,524 M€** (exercice 2024 (exécution))
  - Mesure : Prélèvement sur recettes au titre de la dotation globale de fonctionnement (ligne 3101), exécution
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome I (recettes), Tableau « Prélèvements sur les recettes de l'État au profit des collectivités territoriales », ligne 3101, colonne « Exécution 2024 », page 76
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087930/file/PLF%202026%20-%20V%26M%20TI%20-%20Evaluations%20des%20recettes.pdf ; fichier : `data/raw/tva/plf2026_voies_et_moyens_tome1.pdf`
- [ ] `dotations_compensations_execution_2023` : **8 091,397 M€** (exercice 2023 (exécution))
  - Mesure : Somme des prélèvements de compensation du levier (lignes 3104, 3107, 3119 à 3123, 3130, 3135, 3145, 3146, 3159, 3163, 3165), exécution ; somme calculée par le moteur
  - Où : Projet de loi de finances pour 2025, annexe « Évaluation des voies et moyens », tome I (recettes), Tableau des prélèvements au profit des collectivités, colonne « Exécution 2023 » (fr_budget.agrege.dotations.montant_psr)
  - Document : https://www2.assemblee-nationale.fr/static/17/Annexes-DL/PLF-2025/Voies_et_moyens_Tome_1_2025.pdf ; fichier : `data/raw/tva/plf2025_voies_et_moyens_tome1.pdf`
- [ ] `dotations_compensations_execution_2024` : **8 389,295 M€** (exercice 2024 (exécution))
  - Mesure : Somme des prélèvements de compensation du levier (lignes 3104, 3107, 3119 à 3123, 3130, 3135, 3145, 3146, 3159, 3163, 3165), exécution ; somme calculée par le moteur
  - Où : Projet de loi de finances pour 2026, annexe « Évaluation des voies et moyens », tome I (recettes), Tableau des prélèvements au profit des collectivités, colonne « Exécution 2024 », pages 76 et 77 (fr_budget.agrege.dotations.montant_psr)
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1087930/file/PLF%202026%20-%20V%26M%20TI%20-%20Evaluations%20des%20recettes.pdf ; fichier : `data/raw/tva/plf2026_voies_et_moyens_tome1.pdf`

## retraites

### Référence de validation (6)

- [ ] `cor_aod_un_an_solde_apu_2ans_bas` : **0,05 point de PIB** (COR juin 2026)
  - Mesure : Augmentation d'un an de l'âge d'ouverture des droits, effet sur le solde primaire des APU à court terme (2 ans), borne basse des simulations (DG Trésor, I-MIP, OFCE)
  - Où : Conseil d'orientation des retraites, « Évolutions et perspectives des retraites en France », rapport annuel de juin 2026, et fichiers des tableaux et figures, Page 123 (page 125 du PDF), tableau 2.10, ligne « Solde primaire des APU (en pts de PIB) »
  - Document : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france ; fichier : `data/raw/retraites/cor_ra2026.pdf`, `data/raw/retraites/cor_ra2026_donnees_partie2.xlsx`
- [ ] `cor_aod_un_an_solde_apu_2ans_haut` : **0,4 point de PIB** (COR juin 2026)
  - Mesure : Augmentation d'un an de l'âge d'ouverture des droits, effet sur le solde primaire des APU à court terme (2 ans), borne haute des simulations (DG Trésor, I-MIP, OFCE)
  - Où : Conseil d'orientation des retraites, « Évolutions et perspectives des retraites en France », rapport annuel de juin 2026, et fichiers des tableaux et figures, Page 123 (page 125 du PDF), tableau 2.10, ligne « Solde primaire des APU (en pts de PIB) »
  - Document : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france ; fichier : `data/raw/retraites/cor_ra2026.pdf`, `data/raw/retraites/cor_ra2026_donnees_partie2.xlsx`
- [ ] `cor_aod_un_an_solde_apu_10ans_bas` : **0,3 point de PIB** (COR juin 2026)
  - Mesure : Augmentation d'un an de l'âge d'ouverture des droits, effet sur le solde primaire des APU à moyen terme (10 ans), borne basse des simulations (DG Trésor, I-MIP, OFCE)
  - Où : Conseil d'orientation des retraites, « Évolutions et perspectives des retraites en France », rapport annuel de juin 2026, et fichiers des tableaux et figures, Page 123 (page 125 du PDF), tableau 2.10, ligne « Solde primaire des APU (en pts de PIB) »
  - Document : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france ; fichier : `data/raw/retraites/cor_ra2026.pdf`, `data/raw/retraites/cor_ra2026_donnees_partie2.xlsx`
- [ ] `cor_aod_un_an_solde_apu_10ans_haut` : **0,6 point de PIB** (COR juin 2026)
  - Mesure : Augmentation d'un an de l'âge d'ouverture des droits, effet sur le solde primaire des APU à moyen terme (10 ans), borne haute des simulations (DG Trésor, I-MIP, OFCE)
  - Où : Conseil d'orientation des retraites, « Évolutions et perspectives des retraites en France », rapport annuel de juin 2026, et fichiers des tableaux et figures, Page 123 (page 125 du PDF), tableau 2.10, ligne « Solde primaire des APU (en pts de PIB) »
  - Document : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france ; fichier : `data/raw/retraites/cor_ra2026.pdf`, `data/raw/retraites/cor_ra2026_donnees_partie2.xlsx`
- [ ] `cor_aod_un_an_solde_apu_20ans_bas` : **0,3 point de PIB** (COR juin 2026)
  - Mesure : Augmentation d'un an de l'âge d'ouverture des droits, effet sur le solde primaire des APU à long terme (20 ans), borne basse des simulations (DG Trésor, I-MIP, OFCE)
  - Où : Conseil d'orientation des retraites, « Évolutions et perspectives des retraites en France », rapport annuel de juin 2026, et fichiers des tableaux et figures, Page 123 (page 125 du PDF), tableau 2.10, ligne « Solde primaire des APU (en pts de PIB) »
  - Document : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france ; fichier : `data/raw/retraites/cor_ra2026.pdf`, `data/raw/retraites/cor_ra2026_donnees_partie2.xlsx`
- [ ] `cor_aod_un_an_solde_apu_20ans_haut` : **0,65 point de PIB** (COR juin 2026)
  - Mesure : Augmentation d'un an de l'âge d'ouverture des droits, effet sur le solde primaire des APU à long terme (20 ans), borne haute des simulations (DG Trésor, I-MIP, OFCE)
  - Où : Conseil d'orientation des retraites, « Évolutions et perspectives des retraites en France », rapport annuel de juin 2026, et fichiers des tableaux et figures, Page 123 (page 125 du PDF), tableau 2.10, ligne « Solde primaire des APU (en pts de PIB) »
  - Document : https://www.cor-retraites.fr/rapports-du-cor/rapport-annuel-cor-juin-2026-evolutions-perspectives-retraites-france ; fichier : `data/raw/retraites/cor_ra2026.pdf`, `data/raw/retraites/cor_ra2026_donnees_partie2.xlsx`

## assurance_chomage

### Entrée du calcul (20)

- [ ] `chomage_taux_contribution_2026` : **4 %** (2026)
  - Mesure : Taux de la contribution patronale d'assurance chômage (hors modulation), « ramené à 4 % depuis le 1er mai 2025 »
  - Où : Unédic, « Paramètres utiles de l'Assurance chômage », juillet 2026, Tableau des contributions, page 3
  - Document : https://www.unedic.org/publications/parametres-utiles ; fichier : `data/raw/assurance_chomage/unedic_parametres_utiles_juillet_2026.pdf`
- [ ] `chomage_contributions_principales_2026` : **30,3 Md€** (2026 (prévision d'octobre 2026))
  - Mesure : Contributions principales d'assurance chômage avant prélèvements de l'État
  - Où : Unédic, « Situation financière de l'Assurance chômage à horizon 2028 », prévisions financières d'octobre 2026, Tableau 4, ligne « Contributions principales », page 13
  - Document : https://www.unedic.org/publications/previsions-financieres-de-lunedic-octobre-2026 ; fichier : `data/raw/assurance_chomage/unedic_previsions_octobre_2026.pdf`
- [ ] `chomage_allocations_brutes_2026` : **38,1 Md€** (2026 (prévision d'octobre 2026))
  - Mesure : Allocations brutes et aides versées par l'Unédic
  - Où : Unédic, « Situation financière de l'Assurance chômage à horizon 2028 », prévisions financières d'octobre 2026, Tableau 4, ligne « Allocations brutes et aides », page 13
  - Document : https://www.unedic.org/publications/previsions-financieres-de-lunedic-octobre-2026 ; fichier : `data/raw/assurance_chomage/unedic_previsions_octobre_2026.pdf`
- [ ] `chomage_taux_contribution_2019` : **4,05 %** (2017-2025)
  - Mesure : Taux de la contribution patronale d'assurance chômage jusqu'au 30 avril 2025, « 4,05 %, dont 0,05 point correspondant à une contribution exceptionnelle temporaire mise en place au 1er octobre 2017 »
  - Où : Unédic, « Étude d'impact de la convention d'assurance chômage du 15 novembre 2024 », Fiche « Suppression de la contribution exceptionnelle de 0,05 point », page 55
  - Document : https://www.unedic.org/publications/etude-d-impact-de-la-convention-d-assurance-chomage-du-15-novembre-2024 ; fichier : `data/raw/assurance_chomage/unedic_etude_impact_convention_2024.pdf`
- [ ] `chomage_contributions_principales_2019` : **23 918 M€** (2019 (prévision de mars 2019))
  - Mesure : Contributions principales d'assurance chômage (contributions patronales, après la bascule des contributions salariales sur la CSG)
  - Où : Unédic, prévisions financières de mars 2019, Tableau des recettes et dépenses, ligne « Contributions principales », colonne 2019, page 13
  - Document : https://www.unedic.org/publications/previsions-financieres-de-lunedic-mars-2019 ; fichier : `data/raw/assurance_chomage/unedic_previsions_mars_2019.pdf`
- [ ] `chomage_contribution_points_0_05` : **0,05 point** (2025)
  - Mesure : Montant de la contribution exceptionnelle temporaire créée en 2017 et supprimée au 1er mai 2025
  - Où : Unédic, « Étude d'impact de la convention d'assurance chômage du 15 novembre 2024 », Fiche « Suppression de la contribution exceptionnelle de 0,05 point », page 55
  - Document : https://www.unedic.org/publications/etude-d-impact-de-la-convention-d-assurance-chomage-du-15-novembre-2024 ; fichier : `data/raw/assurance_chomage/unedic_etude_impact_convention_2024.pdf`
- [ ] `chomage_contribution_baisse_0_05_2026` : **385 M€** (2026 (trajectoire financière de février 2025))
  - Mesure : Moindres contributions en 2026 dues à la suppression de la contribution exceptionnelle de 0,05 point au 1er mai 2025, avant l'effet sur le financement de France Travail
  - Où : Unédic, « Étude d'impact de la convention d'assurance chômage du 15 novembre 2024 », Tableau « Impact financier », colonne 2026, page 55
  - Document : https://www.unedic.org/publications/etude-d-impact-de-la-convention-d-assurance-chomage-du-15-novembre-2024 ; fichier : `data/raw/assurance_chomage/unedic_etude_impact_convention_2024.pdf`
- [ ] `chomage_contribution_hausse_0_05_2019` : **288 M€** (2019)
  - Mesure : Recettes supplémentaires en 2019 de la contribution exceptionnelle de 0,05 point créée au 1er octobre 2017, avant l'effet sur la dotation à Pôle emploi (ligne (a))
  - Où : Unédic, « Étude d'impact de la convention d'assurance chômage 2017 », Tableau 2 « Impact financier », ligne « Contribution exceptionnelle (a) », colonne 2019, page 30
  - Document : https://www.unedic.org/publications/etude-dimpact-de-la-convention-dassurance-chomage-2017 ; fichier : `data/raw/assurance_chomage/unedic_etude_impact_convention_2017.pdf`
- [ ] `chomage_revalorisation_juillet_2023_taux` : **1,9 %** (2023)
  - Mesure : Revalorisation des allocations au 1er juillet 2023
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage, mode d'emploi », juin 2023, Page 1
  - Document : https://www.unedic.org/publications/revalorisation-des-allocations-dassurance-chomage-mode-demploi ; fichier : `data/raw/assurance_chomage/unedic_revalorisation_mode_emploi_2023.pdf`
- [ ] `chomage_revalorisation_juillet_2023_total_2023` : **222 M€** (2023)
  - Mesure : Effet de la revalorisation de 1,9 % au 1er juillet 2023 sur les dépenses d'allocations de 2023, total (somme des éléments revalorisés, montant maximal)
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage, mode d'emploi », juin 2023, Tableau 2, ligne « Total », 2023, page 5
  - Document : https://www.unedic.org/publications/revalorisation-des-allocations-dassurance-chomage-mode-demploi ; fichier : `data/raw/assurance_chomage/unedic_revalorisation_mode_emploi_2023.pdf`
- [ ] `chomage_revalorisation_juillet_2023_total_2024` : **293 M€** (2024)
  - Mesure : Effet de la revalorisation de 1,9 % au 1er juillet 2023 sur les dépenses d'allocations de 2024, total (somme des éléments revalorisés, montant maximal)
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage, mode d'emploi », juin 2023, Tableau 2, ligne « Total », 2024, page 5
  - Document : https://www.unedic.org/publications/revalorisation-des-allocations-dassurance-chomage-mode-demploi ; fichier : `data/raw/assurance_chomage/unedic_revalorisation_mode_emploi_2023.pdf`
- [ ] `chomage_revalorisation_juillet_2023_partie_fixe_2024` : **89 M€** (2024)
  - Mesure : Effet en 2024 de la revalorisation de la partie fixe au 1er juillet 2023
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage, mode d'emploi », juin 2023, Tableau 2, ligne « Partie fixe », 2024, page 5
  - Document : https://www.unedic.org/publications/revalorisation-des-allocations-dassurance-chomage-mode-demploi ; fichier : `data/raw/assurance_chomage/unedic_revalorisation_mode_emploi_2023.pdf`
- [ ] `chomage_revalorisation_juillet_2023_minimale_2024` : **13 M€** (2024)
  - Mesure : Effet en 2024 de la revalorisation de l'ARE minimale au 1er juillet 2023
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage, mode d'emploi », juin 2023, Tableau 2, ligne « ARE minimale », 2024, page 5
  - Document : https://www.unedic.org/publications/revalorisation-des-allocations-dassurance-chomage-mode-demploi ; fichier : `data/raw/assurance_chomage/unedic_revalorisation_mode_emploi_2023.pdf`
- [ ] `chomage_revalorisation_juillet_2023_plancher_aref_2024` : **2 M€** (2024)
  - Mesure : Effet en 2024 de la revalorisation du plancher de l'AREF au 1er juillet 2023
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage, mode d'emploi », juin 2023, Tableau 2, ligne « AREF plancher », 2024, page 5
  - Document : https://www.unedic.org/publications/revalorisation-des-allocations-dassurance-chomage-mode-demploi ; fichier : `data/raw/assurance_chomage/unedic_revalorisation_mode_emploi_2023.pdf`
- [ ] `chomage_allocations_brutes_2023` : **35 Md€** (2023 (réalisé))
  - Mesure : Allocations brutes et aides versées par l'Unédic
  - Où : Unédic, « Situation financière de l'Assurance chômage pour 2024-2027 », prévisions financières de juin 2024, Tableau 4, ligne « Allocations brutes et aides », colonne 2023, page 14
  - Document : https://www.unedic.org/publications/previsions-financieres-de-l-unedic-juin-2024 ; fichier : `data/raw/assurance_chomage/unedic_previsions_juin_2024.pdf`
- [ ] `chomage_coefficient_duree_2026` : **0,75 coefficient** (2026)
  - Mesure : Coefficient appliqué à la durée d'indemnisation (réforme de 2023, conjoncture « favorable »)
  - Où : Unédic, « Paramètres utiles de l'Assurance chômage », juillet 2026, Fiche « Durée d'indemnisation », page 5
  - Document : https://www.unedic.org/publications/parametres-utiles ; fichier : `data/raw/assurance_chomage/unedic_parametres_utiles_juillet_2026.pdf`
- [ ] `chomage_reforme_2023_moindres_depenses_2024` : **0,7 Md€** (2024 (prévisions de février 2023))
  - Mesure : Moindres dépenses (allocations et retraites complémentaires) de la réforme de 2023 (coefficient de 0,75 sur la durée d'indemnisation), deuxième année
  - Où : Unédic, « Effets de l'adaptation des règles d'assurance chômage à la conjoncture », version actualisée, Tableau « Synthèse des estimations des moindres dépenses », ligne 2024, page 22
  - Document : https://www.unedic.org/publications/effets-de-ladaptation-des-regles-dassurance-chomage-la-conjoncture ; fichier : `data/raw/assurance_chomage/unedic_effets_adaptation_conjoncture_2023.pdf`
- [ ] `chomage_reforme_2023_moindres_depenses_2025` : **3 Md€** (2025 (prévisions de février 2023))
  - Mesure : Moindres dépenses (allocations et retraites complémentaires) de la réforme de 2023, troisième année
  - Où : Unédic, « Effets de l'adaptation des règles d'assurance chômage à la conjoncture », version actualisée, Tableau « Synthèse des estimations des moindres dépenses », ligne 2025, page 22
  - Document : https://www.unedic.org/publications/effets-de-ladaptation-des-regles-dassurance-chomage-la-conjoncture ; fichier : `data/raw/assurance_chomage/unedic_effets_adaptation_conjoncture_2023.pdf`
- [ ] `chomage_reforme_2023_moindres_depenses_croisiere` : **4,5 Md€** (régime de croisière (horizon 2027))
  - Mesure : Moindres dépenses (allocations et retraites complémentaires) de la réforme de 2023 en régime de croisière
  - Où : Unédic, « Effets de l'adaptation des règles d'assurance chômage à la conjoncture », version actualisée, Tableau « Synthèse des estimations des moindres dépenses », ligne « En régime de croisière », page 22
  - Document : https://www.unedic.org/publications/effets-de-ladaptation-des-regles-dassurance-chomage-la-conjoncture ; fichier : `data/raw/assurance_chomage/unedic_effets_adaptation_conjoncture_2023.pdf`
- [ ] `chomage_reforme_2023_allocations_croisiere` : **4,2 Md€** (régime de croisière (horizon 2027))
  - Mesure : Moindres dépenses d'allocations de la réforme de 2023 en régime de croisière, hors versements aux caisses de retraite complémentaire (0,3 Md€)
  - Où : Unédic, « Effets de l'adaptation des règles d'assurance chômage à la conjoncture », version actualisée, Page 22, texte « En régime de croisière, à horizon 2027 »
  - Document : https://www.unedic.org/publications/effets-de-ladaptation-des-regles-dassurance-chomage-la-conjoncture ; fichier : `data/raw/assurance_chomage/unedic_effets_adaptation_conjoncture_2023.pdf`

### Référence de validation (5)

- [ ] `chomage_allocations_brutes_2018` : **33 499 M€** (2018 (estimation de mars 2019))
  - Mesure : Allocations brutes versées par l'Unédic
  - Où : Unédic, prévisions financières de mars 2019, Tableau des recettes et dépenses, ligne « Allocations brutes », colonne 2018, page 13
  - Document : https://www.unedic.org/publications/previsions-financieres-de-lunedic-mars-2019 ; fichier : `data/raw/assurance_chomage/unedic_previsions_mars_2019.pdf`
- [ ] `chomage_revalorisation_avril_2023_taux` : **1,9 %** (2023)
  - Mesure : Revalorisation des allocations au 1er avril 2023
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage de 1,9 % dès le 1er avril », actualité, Titre et premier paragraphe
  - Document : https://www.unedic.org/actualites/revalorisation-des-allocations-dassurance-chomage-de-19-des-le-1er-avril ; fichier : `data/raw/assurance_chomage/unedic_communique_revalorisation_avril_2023.html`
- [ ] `chomage_revalorisation_avril_2023_cumul` : **590 M€** (2023-2024)
  - Mesure : Coût de la revalorisation de 1,9 % au 1er avril 2023 « au cumul pour 2023 et 2024 », hors dégressivité
  - Où : Unédic, « Revalorisation des allocations d'assurance chômage de 1,9 % dès le 1er avril », actualité, Avant-dernier paragraphe
  - Document : https://www.unedic.org/actualites/revalorisation-des-allocations-dassurance-chomage-de-19-des-le-1er-avril ; fichier : `data/raw/assurance_chomage/unedic_communique_revalorisation_avril_2023.html`
- [ ] `chomage_revalorisation_juillet_2018_taux` : **0,7 %** (2018)
  - Mesure : Revalorisation des allocations au 1er juillet 2018
  - Où : Unédic, « Les allocations d'assurance chômage sont revalorisées de 0,70 % à partir du 1er juillet », actualité, Titre
  - Document : https://www.unedic.org/actualites/les-allocations-dassurance-chomage-sont-revalorisees-de-070-partir-du-1er ; fichier : `data/raw/assurance_chomage/unedic_communique_revalorisation_juillet_2018.html`
- [ ] `chomage_revalorisation_juillet_2018_cout` : **200 M€** (2018-2019)
  - Mesure : Coût de la revalorisation de 0,70 % au 1er juillet 2018 pour le second semestre 2018 et l'année 2019, hors Mayotte (« de l'ordre de 200 millions d'€ »)
  - Où : Unédic, « Les allocations d'assurance chômage sont revalorisées de 0,70 % à partir du 1er juillet », actualité, Dernier paragraphe
  - Document : https://www.unedic.org/actualites/les-allocations-dassurance-chomage-sont-revalorisees-de-070-partir-du-1er ; fichier : `data/raw/assurance_chomage/unedic_communique_revalorisation_juillet_2018.html`

### Non repéré (2)

- [ ] `chomage_avenant_rci_croisiere_sans_prolongement` : **900 M€** (régime de croisière)
  - Mesure : Effet de l'avenant 2026 sur les ruptures conventionnelles en régime de croisière, hypothèse d'aucun prolongement seniors (borne haute de l'économie)
  - Où : Unédic, « Situation financière de l'Assurance chômage à horizon 2028 », prévisions financières d'octobre 2026, Encadré 1, tableau A, page 8
  - Document : https://www.unedic.org/publications/previsions-financieres-de-lunedic-octobre-2026 ; fichier : `data/raw/assurance_chomage/unedic_previsions_octobre_2026.pdf`
- [ ] `chomage_avenant_rci_croisiere_prolongement_total` : **730 M€** (régime de croisière)
  - Mesure : Effet de l'avenant 2026 sur les ruptures conventionnelles en régime de croisière, hypothèse de recours total au prolongement seniors (borne basse de l'économie)
  - Où : Unédic, « Situation financière de l'Assurance chômage à horizon 2028 », prévisions financières d'octobre 2026, Encadré 1, tableau A, page 8
  - Document : https://www.unedic.org/publications/previsions-financieres-de-lunedic-octobre-2026 ; fichier : `data/raw/assurance_chomage/unedic_previsions_octobre_2026.pdf`

## croissance

### Non repéré (11)

- [ ] `mesange_pib_1an_depense_generique` : **0,78 % d'écart du PIB au compte central** (Mésange 2017 (choc au 1er trimestre 2015))
  - Mesure : Hausse de la dépense publique d'un montant de 1 point de PIB : effet sur le PIB en volume à 1 an
  - Où : Document de travail G 2017/04, « Le modèle macroéconométrique Mésange réestimation et nouveautés », Insee et DG Trésor, Page 106, section 4.1.2, tableau, ligne « PIB en volume », colonne « 1 an »
  - Document : https://www.insee.fr/fr/statistiques/fichier/2848300/G2017-04.pdf ; fichier : `data/raw/croissance/insee_mesange_2017.pdf`
- [ ] `mesange_pib_1an_cotisations_employeurs` : **0,2 % d'écart du PIB au compte central** (Mésange 2017 (choc au 1er trimestre 2015))
  - Mesure : Baisse des cotisations sociales employeurs de 1 % du PIB ex ante : effet sur le PIB en volume à 1 an
  - Où : Document de travail G 2017/04, « Le modèle macroéconométrique Mésange réestimation et nouveautés », Insee et DG Trésor, Page 108, section 4.1.3, tableau, ligne « PIB en volume », colonne « 1 an »
  - Document : https://www.insee.fr/fr/statistiques/fichier/2848300/G2017-04.pdf ; fichier : `data/raw/croissance/insee_mesange_2017.pdf`
- [ ] `mesange_pib_1an_cotisations_salaries` : **0,38 % d'écart du PIB au compte central** (Mésange 2017 (choc au 1er trimestre 2015))
  - Mesure : Baisse des cotisations sociales salariés de 1 % du PIB ex ante : effet sur le PIB en volume à 1 an
  - Où : Document de travail G 2017/04, « Le modèle macroéconométrique Mésange réestimation et nouveautés », Insee et DG Trésor, Page 111, section 4.1.4, tableau, ligne « PIB en volume », colonne « 1 an »
  - Document : https://www.insee.fr/fr/statistiques/fichier/2848300/G2017-04.pdf ; fichier : `data/raw/croissance/insee_mesange_2017.pdf`
- [ ] `mesange_pib_1an_tva` : **0,32 % d'écart du PIB au compte central** (Mésange 2017 (choc au 1er trimestre 2015))
  - Mesure : Hausse de la TVA de 1 % du PIB ex ante : effet sur le PIB en volume à 1 an (valeur absolue de -0,32)
  - Où : Document de travail G 2017/04, « Le modèle macroéconométrique Mésange réestimation et nouveautés », Insee et DG Trésor, Page 113, section 4.1.5, tableau, ligne « PIB en volume », colonne « 1 an »
  - Document : https://www.insee.fr/fr/statistiques/fichier/2848300/G2017-04.pdf ; fichier : `data/raw/croissance/insee_mesange_2017.pdf`
- [ ] `mesange_pib_1an_csg` : **0,41 % d'écart du PIB au compte central** (Mésange 2017 (choc au 1er trimestre 2015))
  - Mesure : Baisse de la CSG de 1 % du PIB ex ante : effet sur le PIB en volume à 1 an
  - Où : Document de travail G 2017/04, « Le modèle macroéconométrique Mésange réestimation et nouveautés », Insee et DG Trésor, Page 116, section 4.1.6, tableau, ligne « PIB en volume », colonne « 1 an »
  - Document : https://www.insee.fr/fr/statistiques/fichier/2848300/G2017-04.pdf ; fichier : `data/raw/croissance/insee_mesange_2017.pdf`
- [ ] `mesange_pib_1an_impot_revenu` : **0,41 % d'écart du PIB au compte central** (Mésange 2017 (choc au 1er trimestre 2015))
  - Mesure : Baisse de l'impôt sur le revenu de 1 % du PIB ex ante : effet sur le PIB en volume à 1 an
  - Où : Document de travail G 2017/04, « Le modèle macroéconométrique Mésange réestimation et nouveautés », Insee et DG Trésor, Page 118, section 4.1.7, tableau, ligne « PIB en volume », colonne « 1 an »
  - Document : https://www.insee.fr/fr/statistiques/fichier/2848300/G2017-04.pdf ; fichier : `data/raw/croissance/insee_mesange_2017.pdf`
- [ ] `mesange_pib_1an_taxe_carbone` : **0,51 % d'écart du PIB au compte central** (Mésange 2017 (choc au 1er trimestre 2015))
  - Mesure : Hausse de la taxe carbone de 1 point de PIB : effet sur le PIB en volume à 1 an (valeur absolue de -0,51)
  - Où : Document de travail G 2017/04, « Le modèle macroéconométrique Mésange réestimation et nouveautés », Insee et DG Trésor, Page 121, section 4.1.8, tableau, ligne « PIB en volume », colonne « 1 an »
  - Document : https://www.insee.fr/fr/statistiques/fichier/2848300/G2017-04.pdf ; fichier : `data/raw/croissance/insee_mesange_2017.pdf`
- [ ] `ofce_multiplicateur_recettes` : **0,5 point de PIB par point de PIB d'impulsion** (juillet 2025)
  - Mesure : Multiplicateur retenu pour la hausse des recettes
  - Où : OFCE Policy brief n° 146, « Quelles trajectoires pour les finances publiques de la France ? » (Heyer, Plane, Ragot, Sampognaro, Timbeau), Page 17, « avec un multiplicateur respectif à 0,5 et 1 »
  - Document : https://www.ofce.fr/pdf/pbrief/2025/OFCEpbrief146.pdf ; fichier : `data/raw/croissance/ofce_policy_brief_146.pdf`
- [ ] `ofce_multiplicateur_depenses` : **1 point de PIB par point de PIB d'impulsion** (juillet 2025)
  - Mesure : Multiplicateur retenu pour la baisse des dépenses
  - Où : OFCE Policy brief n° 146, « Quelles trajectoires pour les finances publiques de la France ? » (Heyer, Plane, Ragot, Sampognaro, Timbeau), Page 17, « avec un multiplicateur respectif à 0,5 et 1 »
  - Document : https://www.ofce.fr/pdf/pbrief/2025/OFCEpbrief146.pdf ; fichier : `data/raw/croissance/ofce_policy_brief_146.pdf`
- [ ] `ofce_persistance_ecart_production` : **0,7 sans unité** (juillet 2025)
  - Mesure : Paramètre rho de l'équation de l'écart de production (valeur usuelle dans les études empiriques)
  - Où : OFCE Policy brief n° 146, « Quelles trajectoires pour les finances publiques de la France ? » (Heyer, Plane, Ragot, Sampognaro, Timbeau), Page 15, encadré 3, liste des paramètres
  - Document : https://www.ofce.fr/pdf/pbrief/2025/OFCEpbrief146.pdf ; fichier : `data/raw/croissance/ofce_policy_brief_146.pdf`
- [ ] `ofce_effet_ecart_production_solde` : **0,5 point de PIB de solde par point d'écart de production** (juillet 2025)
  - Mesure : Paramètre alpha, effet du ralentissement sur les recettes (valeur usuelle en France)
  - Où : OFCE Policy brief n° 146, « Quelles trajectoires pour les finances publiques de la France ? » (Heyer, Plane, Ragot, Sampognaro, Timbeau), Page 15, encadré 3, liste des paramètres
  - Document : https://www.ofce.fr/pdf/pbrief/2025/OFCEpbrief146.pdf ; fichier : `data/raw/croissance/ofce_policy_brief_146.pdf`

## dynamique_dette

### Entrée du calcul (7)

- [ ] `dette_etat_negociable_nominal_fin_2025` : **2 670,3 Md€** (2025 (exécution))
  - Mesure : Encours de la dette négociable de l'État, valeur nominale, fin 2025
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 40, tableau « Évolution de l'encours de la dette négociable », ligne « Ensemble de la dette – valeur nominale »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_btf_fin_2025` : **195,9 Md€** (2025 (exécution))
  - Mesure : Encours des titres à court terme (BTF), fin 2025
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 40, même tableau, ligne « BTF »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_emissions_mlt_2026` : **310 Md€** (2026 (révisé au PLF 2027))
  - Mesure : Émissions de titres à moyen et long terme, nettes des rachats, 2026 révisé
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 32, tableau de financement, colonne « 2026 révisé »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_amortissements_mlt_nominal_2026` : **167,5 Md€** (2026 (révisé au PLF 2027))
  - Mesure : Amortissement de titres d'État à moyen et long terme, valeur nominale, 2026 révisé
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 32, tableau de financement, ligne « valeur nominale », colonne « 2026 révisé »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_variation_btf_2026` : **9,6 Md€** (2026 (révisé au PLF 2027))
  - Mesure : Variation de l'encours de titres à court terme, 2026 révisé
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 32, tableau de financement, colonne « 2026 révisé »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_emissions_mlt_2027` : **340 Md€** (PLF 2027)
  - Mesure : Émissions de titres à moyen et long terme, nettes des rachats, 2027
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 32, tableau de financement, colonne « 2027 PLF »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_variation_btf_2027` : **2,2 Md€** (PLF 2027)
  - Mesure : Variation de l'encours de titres à court terme, 2027
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 32, tableau de financement, colonne « 2027 PLF »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`

### Référence de validation (2)

- [ ] `dette_etat_choc_taux_100pb_an_1` : **3,4 Md€** (PLF 2027)
  - Mesure : Surcoût de charge de la dette d'un choc de +1 point sur toute la courbe au 1er janvier 2027, première année (comptabilité maastrichtienne)
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 40, « Simulation d'un choc de taux et sensibilité à l'inflation »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_choc_taux_100pb_an_5` : **19 Md€** (PLF 2027)
  - Mesure : Même choc, cinquième année (« environ » dans la source)
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 40, « Simulation d'un choc de taux et sensibilité à l'inflation »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`

### Non repéré (3)

- [ ] `dette_etat_taux_10_ans_fin_2026` : **4,2 %** (PLF 2027)
  - Mesure : Hypothèse de taux à 10 ans, fin 2026
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 33, « Scénario de taux à moyen et long terme »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_taux_10_ans_fin_2027` : **4,3 %** (PLF 2027)
  - Mesure : Hypothèse de taux à 10 ans, fin 2027, puis stabilisation à ce niveau
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 33, « Scénario de taux à moyen et long terme »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`
- [ ] `dette_etat_taux_3_mois_fin_2026` : **3 %** (PLF 2027)
  - Mesure : Hypothèse de taux à 3 mois, fin 2026, puis stabilisation à ce niveau
  - Où : Projet de loi de finances pour 2027, projet annuel de performances de la mission « Engagements financiers de l'État » (programme 117, charge de la dette et trésorerie de l'État), Page 34, « Scénario de taux à court terme »
  - Document : https://www.assemblee-nationale.fr/dyn/contenu/visualisation/1128231/file/PAP%202027%20-%20Engagements%20financiers%20de%20l%27Etat.pdf ; fichier : `data/raw/dette/plf2027_pap_engagements_financiers_etat.pdf`

## menages_types

### Entrée du calcul (42)

- [ ] `insee_salaire_net_median_2024` : **2 190 euros par mois** (2024)
  - Mesure : Salaire net médian en équivalent temps plein, secteur privé, ensemble
  - Où : Insee Première n° 2079, « Les salaires dans le secteur privé en 2024 », Page 2, figure 3 (distribution des salaires nets mensuels en EQTP), ligne « Médiane », colonne « Ensemble »
  - Document : https://www.insee.fr/fr/statistiques/8657156 ; fichier : `data/raw/menages/insee_premiere_2079.pdf`
- [ ] `insee_salaire_net_p95_2024` : **5 593 euros par mois** (2024)
  - Mesure : 95e centile du salaire net en équivalent temps plein, secteur privé, ensemble
  - Où : Insee Première n° 2079, « Les salaires dans le secteur privé en 2024 », Page 2, figure 3, ligne « 95e centile », colonne « Ensemble »
  - Document : https://www.insee.fr/fr/statistiques/8657156 ; fichier : `data/raw/menages/insee_premiere_2079.pdf`
- [ ] `service_public_apprenti_18_20_ans_1re_annee` : **0,43 fraction du SMIC** (septembre 2026)
  - Mesure : Rémunération brute mensuelle minimale d'un apprenti de 18 à 20 ans en 1re année, en part du SMIC
  - Où : Fiche « Contrat d'apprentissage » (vérifiée le 8 septembre 2026), Tableau « Rémunération brute mensuelle minimale d'un apprenti », ligne « 1re année », colonne « 18-20 ans » : « 43 % du Smic »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2918 ; fichier : `data/raw/menages/service_public/F2918.html`
- [ ] `service_public_apprenti_18_20_ans_2e_annee` : **0,51 fraction du SMIC** (septembre 2026)
  - Mesure : Rémunération brute mensuelle minimale d'un apprenti de 18 à 20 ans en 2e année, en part du SMIC
  - Où : Fiche « Contrat d'apprentissage » (vérifiée le 8 septembre 2026), Même tableau, ligne « 2e année », colonne « 18-20 ans » : « 51 % du Smic »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2918 ; fichier : `data/raw/menages/service_public/F2918.html`
- [ ] `service_public_apprenti_18_20_ans_3e_annee` : **0,67 fraction du SMIC** (septembre 2026)
  - Mesure : Rémunération brute mensuelle minimale d'un apprenti de 18 à 20 ans en 3e année, en part du SMIC
  - Où : Fiche « Contrat d'apprentissage » (vérifiée le 8 septembre 2026), Même tableau, ligne « 3e année », colonne « 18-20 ans » : « 67 % du Smic »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2918 ; fichier : `data/raw/menages/service_public/F2918.html`
- [ ] `drees_pension_brute_moyenne_droit_direct_2023` : **1 666 euros par mois** (2023)
  - Mesure : Pension mensuelle moyenne de droit direct, majoration pour trois enfants comprise, des retraités résidant en France, fin 2023, brute
  - Où : Les retraités et les retraites, édition 2025, fiche 5 « Le niveau des pensions », Premier paragraphe de la fiche : « s’élève à 1 666 euros bruts » ; tableau 1, ligne 2023
  - Document : https://drees.solidarites-sante.gouv.fr/sites/default/files/2025-07/Fiche%2005%20-%20Le%20niveau%20des%20pensions.pdf ; fichier : `data/raw/menages/drees_retraites_2025_fiche05.pdf`
- [ ] `dss_revalorisation_pensions_base_2024_01` : **1,053 coefficient** (1er janvier 2024)
  - Mesure : Coefficient de revalorisation des pensions de vieillesse de base au 1er janvier 2024
  - Où : Instruction interministérielle n° DSS/3A/2023/189 du 28 novembre 2023 relative à la revalorisation des pensions de vieillesse au 1er janvier 2024, Résumé et point 1 : « revalorisés d’un coefficient de 1,053 au 1er janvier 2024, soit un taux de 5,3 % »
  - Document : https://legislation.lassuranceretraite.fr/Pdf/instruction_ministerielle_2023_189_28112023.pdf ; fichier : `data/raw/menages/dss_instruction_2023_189.pdf`
- [ ] `dss_revalorisation_pensions_base_2025_01` : **1,022 coefficient** (1er janvier 2025)
  - Mesure : Coefficient de revalorisation des pensions de vieillesse de base au 1er janvier 2025
  - Où : Instruction interministérielle n° DSS/SD3A/DB/2024/176 du 13 décembre 2024 relative à la revalorisation des pensions de vieillesse au 1er janvier 2025, Résumé et point 1 : « revalorisés d’un coefficient de 1,022 au 1er janvier 2025, soit un taux de 2,2 % »
  - Document : https://legislation.lassuranceretraite.fr/Pdf/instruction_ministerielle_2024_176_13122024.pdf ; fichier : `data/raw/menages/dss_instruction_2024_176.pdf`
- [ ] `insee_revenu_median_non_salaries_classiques_2023` : **2 620 euros par mois** (2023)
  - Mesure : Revenu d'activité mensuel médian des non-salariés classiques (hors agriculture et micro-entrepreneurs)
  - Où : Insee Première n° 2060, « Les revenus d'activité des non-salariés en 2023 » (juin 2025), Page 1 : « Un non-salarié classique sur deux gagne plus de 2 620 euros par mois » ; figure 2
  - Document : https://www.insee.fr/fr/statistiques/8590189 ; fichier : `data/raw/menages/insee_premiere_2060.pdf`
- [ ] `independant_abattement_assiette` : **0,26 fraction** (2025)
  - Mesure : Abattement forfaitaire appliqué au revenu brut pour former l'assiette unique des cotisations et de la CSG-CRDS
  - Où : Page « Réforme de l'assiette sociale et du barème des cotisations sociales » (mise à jour le 7 mai 2026), Section « Pour aller plus loin sur la réforme de l'assiette » : « le revenu brut abattu de 26 % »
  - Document : https://www.urssaf.fr/accueil/independant/comprendre-payer-cotisations/reforme-cotisations-independants.html ; fichier : `data/raw/menages/independants/urssaf_reforme_assiette.pdf`
- [ ] `independant_abattement_plancher` : **0,0176 fraction du PSS** (2025)
  - Mesure : Plancher de l'abattement, en part du plafond annuel de la Sécurité sociale
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 1er, art. D. 136-5, I : « 1,76 % de la valeur annuelle du plafond »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_abattement_plafond` : **1,3 fraction du PSS** (2025)
  - Mesure : Plafond de l'abattement, en part du plafond annuel de la Sécurité sociale
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 1er, art. D. 136-5, II : « 130 % de la valeur annuelle du plafond »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_taux_t1` : **0,015 fraction** (2025)
  - Mesure : Maladie-maternité : taux T1 (assiette à 40 % du PSS)
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 2° : « T1 est égal à 1,5 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_taux_t2` : **0,04 fraction** (2025)
  - Mesure : Maladie-maternité : taux T2 (assiette à 60 % du PSS)
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 3° : « T2 est égal à 4 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_taux_t3` : **0,065 fraction** (2025)
  - Mesure : Maladie-maternité : taux T3 (assiette à 110 % du PSS)
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 4° : « T3 est égal à 6,5 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_taux_t4` : **0,077 fraction** (2025)
  - Mesure : Maladie-maternité : taux T4 (assiette à 200 % du PSS)
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 5° : « T4 est égal à 7,7 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_taux_t5` : **0,085 fraction** (2025)
  - Mesure : Maladie-maternité : taux de base T5 jusqu'à 3 PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-1 : « 8,50 % pour la fraction des revenus qui n'excède pas trois fois » le PSS ; art. D. 621-2, 6°
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_taux_au_dela_3_pss` : **0,065 fraction** (2025)
  - Mesure : Maladie-maternité : taux de la part au-delà de 3 PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-1 : « 6,5 % pour la part au-delà de ce montant »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_ij_taux` : **0,005 fraction** (2025)
  - Mesure : Indemnités journalières (artisans, commerçants) : taux, jusqu'à 5 PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-3, I : « 0,50 % pour les travailleurs indépendants mentionnés à l'article L. 631-1 »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_ij_assiette_minimale` : **0,4 fraction du PSS** (2025)
  - Mesure : Indemnités journalières : assiette minimale, en part du PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-3, I : « ne peut être calculée sur une assiette inférieure à 40 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_retraite_base_plafonnee` : **0,1715 fraction** (2025)
  - Mesure : Retraite de base des artisans et commerçants : taux plafonné (jusqu'à 1 PSS), hors part déplafonnée
  - Où : Page « Réforme de l'assiette sociale et du barème des cotisations sociales » (mise à jour le 7 mai 2026), Tableau « Cotisations retraite de base pour les artisans, commerçant et PLNR », nouveau : « 17,87 % (17,15 + 0,72) »
  - Document : https://www.urssaf.fr/accueil/independant/comprendre-payer-cotisations/reforme-cotisations-independants.html ; fichier : `data/raw/menages/independants/urssaf_reforme_assiette.pdf`
- [ ] `independant_retraite_base_deplafonnee` : **0,0072 fraction** (2025)
  - Mesure : Retraite de base : taux sur la totalité de l'assiette
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 3, I, 1° b) : « 0,60 % » remplacé par « 0,72 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_retraite_complementaire_t1` : **0,081 fraction** (2025)
  - Mesure : Retraite complémentaire des artisans et commerçants : taux jusqu'à 1 PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 3, I, 2°, art. D. 635-7, 1° : « 8,1 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_retraite_complementaire_t2` : **0,091 fraction** (2025)
  - Mesure : Retraite complémentaire : taux de 1 à 4 PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 3, I, 2°, art. D. 635-7, 2° : « 9,1 % »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_invalidite_deces` : **0,013 fraction** (2026)
  - Mesure : Invalidité-décès : taux jusqu'à 1 PSS
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Invalidité - décès en métropole » : « 1,30 % »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `independant_allocations_familiales_taux` : **0,031 fraction** (2026)
  - Mesure : Allocations familiales : taux plein (au-delà de 140 % du PSS), progressif de 110 % à 140 %
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Allocations familiales en métropole » : « Taux progressif de 0 % à 3,10 % » entre 110 % et 140 % du Pass
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `independant_formation_artisan` : **0,0029 fraction du PSS** (2026)
  - Mesure : Contribution à la formation professionnelle d'un artisan, en part du PSS
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « CFP […] - Artisan en métropole » : « Sur la base de 48 060 € (1 Pass) 0,29 % »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `independant_csg_crds` : **0,097 fraction** (2026)
  - Mesure : CSG-CRDS des indépendants sur les revenus d'activité
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « CSG-CRDS en métropole » : « Revenus d'activité 9,70 % »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `service_public_csg_activite_deductible` : **0,068 fraction** (2026)
  - Mesure : Part déductible de l'impôt de la CSG sur les revenus d'activité
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Tableau « Taux selon la nature des revenus », ligne « Revenus d'activité salariée » : « 9,2 % 6,8 % 0,5 % »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_crds_activite` : **0,005 fraction** (2026)
  - Mesure : Taux de la CRDS sur les revenus d'activité
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Même ligne : CRDS « 0,5 % »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `independant_maladie_seuil_s0` : **0,2 fraction du PSS** (2025)
  - Mesure : Maladie-maternité : seuil sous lequel le taux est nul
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 1° : « inférieur à 20 % » du PSS
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_seuil_s1` : **0,4 fraction du PSS** (2025)
  - Mesure : Maladie-maternité : seuil du taux T1
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 2° et 3° : « 40 % » du PSS
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_seuil_s2` : **0,6 fraction du PSS** (2025)
  - Mesure : Maladie-maternité : seuil du taux T2
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 3° et 4° : « 60 % » du PSS
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_seuil_s3` : **1,1 fraction du PSS** (2025)
  - Mesure : Maladie-maternité : seuil du taux T3
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 4° et 5° : « 110 % » du PSS
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_seuil_s4` : **2 fraction du PSS** (2025)
  - Mesure : Maladie-maternité : seuil du taux T4
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-2, 5° et 6° : « 200 % » du PSS
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_maladie_seuil_s5` : **3 fraction du PSS** (2025)
  - Mesure : Maladie-maternité : seuil du taux de base T5 et de la part à 6,5 %
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-1 et D. 621-2, 6° : « trois fois » le PSS
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_ij_plafond` : **5 fraction du PSS** (2025)
  - Mesure : Indemnités journalières : plafond de l'assiette, en PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 2, art. D. 621-3, I : « n'excédant pas cinq fois le plafond annuel »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_retraite_complementaire_plafond` : **4 fraction du PSS** (2025)
  - Mesure : Retraite complémentaire : plafond de l'assiette, en PSS
  - Où : Décret n° 2024-688 du 5 juillet 2024 fixant les modalités de calcul des cotisations et contributions sociales des travailleurs indépendants (JORF du 6 juillet 2024, texte 13), Article 3, I, 2°, art. D. 635-7, 2° : « dans la limite de quatre fois le plafond annuel »
  - Document : https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000049888566 ; fichier : `data/raw/menages/independants/jorf_decret_2024_688.pdf`
- [ ] `independant_allocations_familiales_seuil_bas` : **1,1 fraction du PSS** (2026)
  - Mesure : Allocations familiales : seuil sous lequel le taux est nul, en PSS
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Allocations familiales en métropole » : « inférieurs à 52 866 € (110 % du plafond annuel » 
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `independant_allocations_familiales_seuil_haut` : **1,4 fraction du PSS** (2026)
  - Mesure : Allocations familiales : seuil du taux plein, en PSS
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Même tableau : « supérieurs à 67 284 € (140 % du Pass) 3,10 % »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `independant_retraite_base_assiette_minimale_heures_smic` : **450 heures** (2026)
  - Mesure : Retraite de base : assiette minimale, en heures de SMIC horaire
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Vos cotisations minimales », retraite de base : « 5 409 € (450 × Smic horaire) »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `independant_invalidite_assiette_minimale` : **0,115 fraction du PSS** (2026)
  - Mesure : Invalidité-décès : assiette minimale, en part du PSS
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Vos cotisations minimales », invalidité-décès : « 5 527 € (11,5 % du Pass) »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`

### Référence de validation (23)

- [ ] `service_public_bmaf_2026` : **478,16 euros par mois** (avril 2026)
  - Mesure : Base mensuelle de calcul des allocations familiales au 1er avril 2026
  - Où : Actualité « Prestations familiales et sociales : les nouveaux montants au 1er avril » (publiée le 24 mars 2026, mise à jour le 1er avril 2026), Paragraphe « Allocations familiales revalorisées au 1er avril 2026 » : « Elle s’élève à 478,16 € »
  - Document : https://www.service-public.gouv.fr/particuliers/actualites/A16506 ; fichier : `data/raw/menages/service_public/A16506.html`
- [ ] `service_public_bmaf_2025` : **474,37 euros par mois** (avril 2025)
  - Mesure : Base mensuelle de calcul des allocations familiales au 1er avril 2025
  - Où : Actualité « Prestations familiales et sociales : les nouveaux montants au 1er avril » (publiée le 24 mars 2026, mise à jour le 1er avril 2026), Même paragraphe : « contre 474,37 € depuis le 1er avril 2025 »
  - Document : https://www.service-public.gouv.fr/particuliers/actualites/A16506 ; fichier : `data/raw/menages/service_public/A16506.html`
- [ ] `service_public_pa_montant_forfaitaire_2026` : **638,28 euros par mois** (avril 2026)
  - Mesure : Montant forfaitaire de la prime d'activité, personne seule sans enfant
  - Où : Fiche « Prime d'activité : salarié ou fonctionnaire » (vérifiée le 1er juin 2026), Section « Montant » : « Le montant forfaitaire (montant de base du calcul de la prime d'activité) est égal à 638,28 € » ; tableau « Montants forfaitaires de la prime d'activité », ligne 0, colonne « Vous vivez seul »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2882 ; fichier : `data/raw/menages/service_public/F2882.html`
- [ ] `service_public_pa_part_revenus_professionnels_2026` : **0,5985 fraction** (avril 2026)
  - Mesure : Part des revenus professionnels ajoutée au montant forfaitaire de la prime d'activité
  - Où : Fiche « Prime d'activité : salarié ou fonctionnaire » (vérifiée le 1er juin 2026), Section « Montant » : « 59,85 % du montant des revenus professionnels du foyer »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2882 ; fichier : `data/raw/menages/service_public/F2882.html`
- [ ] `service_public_pa_seuil_bonification_2026` : **726,29 euros par mois** (avril 2026)
  - Mesure : Revenu professionnel mensuel au-delà duquel la bonification individuelle de la prime d'activité est due
  - Où : Fiche « Prime d'activité : salarié ou fonctionnaire » (vérifiée le 1er juin 2026), Section « Montant » : « Cette bonification est due si le salaire mensuel moyen est supérieur à 726,29 € »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2882 ; fichier : `data/raw/menages/service_public/F2882.html`
- [ ] `service_public_af_deux_enfants_2026` : **152,25 euros par mois** (avril 2026)
  - Mesure : Allocations familiales pour deux enfants, ressources de 79 980 € ou moins, montant de base après CRDS
  - Où : Fiche « Allocations familiales (famille de 2 enfants ou plus) » (vérifiée le 1er juin 2026), Tableau « Montants des allocations familiales », ligne « 79 980 € ou moins », colonne « Montant de base »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F13213 ; fichier : `data/raw/menages/service_public/F13213.html`
- [ ] `service_public_ars_6_10_ans_2026` : **426,87 euros par enfant** (rentrée 2026)
  - Mesure : Allocation de rentrée scolaire pour un enfant de 6 à 10 ans, après CRDS
  - Où : Fiche « Allocation de rentrée scolaire (ARS) » (vérifiée le 4 août 2026), Tableau « Montant de l'ARS selon l'âge de l'enfant », ligne « 6 à 10 ans »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F1878 ; fichier : `data/raw/menages/service_public/F1878.html`
- [ ] `service_public_asf_2026` : **200,78 euros par mois et par enfant** (avril 2026)
  - Mesure : Allocation de soutien familial par enfant
  - Où : Fiche « Allocation de soutien familial (ASF) : parents séparés » (vérifiée le 1er avril 2026), Section « Quel est le montant de l'allocation de soutien familial (ASF) ? » : « Le montant de l'ASF s'élève à 200,78 € par mois et par enfant »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F815 ; fichier : `data/raw/menages/service_public/F815.html`
- [ ] `service_public_csg_pension_seuil_taux_zero_1_part_2026` : **13 048 euros de revenu fiscal de référence** (2026)
  - Mesure : Revenu fiscal de référence 2024 au-delà duquel la CSG sur les pensions n'est plus à taux zéro, 1 part
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », tableau « Taux selon le revenu fiscal de référence (RFR) 2024 du foyer », ligne « 1 part », colonne « Taux zéro » : « Jusqu'à 13 048 € »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_seuil_taux_reduit_1_part_2026` : **17 057 euros de revenu fiscal de référence** (2026)
  - Mesure : Plafond du taux réduit de CSG sur les pensions, 1 part
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », tableau « Taux selon le revenu fiscal de référence (RFR) 2024 du foyer », ligne « 1 part », colonne « Taux réduit » : « De 13 049 € à 17 057 € »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_seuil_taux_median_1_part_2026` : **26 472 euros de revenu fiscal de référence** (2026)
  - Mesure : Plafond du taux médian de CSG sur les pensions, 1 part
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », tableau « Taux selon le revenu fiscal de référence (RFR) 2024 du foyer », ligne « 1 part », colonne « Taux médian » : « De 17 058 € à 26 472 € »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_majoration_demi_part_taux_zero_2026` : **3 484 euros** (2026)
  - Mesure : Majoration du seuil du taux zéro par demi-part supplémentaire
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », tableau « Taux selon le revenu fiscal de référence (RFR) 2024 du foyer », ligne « Demi-part supplémentaire », colonne « Taux zéro » : « 3 484 € »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_majoration_demi_part_taux_reduit_2026` : **4 555 euros** (2026)
  - Mesure : Majoration du plafond du taux réduit par demi-part supplémentaire
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », tableau « Taux selon le revenu fiscal de référence (RFR) 2024 du foyer », ligne « Demi-part supplémentaire », 3e valeur : « 4 555 € »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_majoration_demi_part_taux_median_2026` : **7 066 euros** (2026)
  - Mesure : Majoration du plafond du taux médian par demi-part supplémentaire
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », tableau « Taux selon le revenu fiscal de référence (RFR) 2024 du foyer », ligne « Demi-part supplémentaire », 4e valeur : « 7 066 € »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_taux_reduit_2026` : **0,038 fraction** (2026)
  - Mesure : Taux réduit de CSG sur les pensions de retraite
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », liste « Il existe 4 taux de CSG sur les pensions de retraite » : « Taux réduit ( 3,8 % ) »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_taux_median_2026` : **0,066 fraction** (2026)
  - Mesure : Taux médian de CSG sur les pensions de retraite
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », liste « Il existe 4 taux de CSG sur les pensions de retraite » : « Taux médian ( 6,6 % ) »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `service_public_csg_pension_taux_normal_2026` : **0,083 fraction** (2026)
  - Mesure : Taux normal de CSG sur les pensions de retraite
  - Où : Fiche « CSG et CRDS sur les revenus d'activité et de remplacement » (vérifiée le 1er juin 2026), Section « Pension de retraite », liste « Il existe 4 taux de CSG sur les pensions de retraite » : « Taux normal ( 8,3 % ) »
  - Document : https://www.service-public.gouv.fr/particuliers/vosdroits/F2971 ; fichier : `data/raw/menages/service_public/F2971.html`
- [ ] `urssaf_retraite_complementaire_maximale_2026` : **17 494 euros par an** (2026)
  - Mesure : Cotisation maximale de retraite complémentaire (assiette de 4 PSS)
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Cotisations maximales », « Régime vieillesse complémentaire » : « Cotisation maximale 17 494 € »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `urssaf_ij_maximale_2026` : **1 202 euros par an** (2026)
  - Mesure : Cotisation maximale d'indemnités journalières (assiette de 5 PSS)
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Cotisations maximales », « Maladie 2 » : « Cotisation maximale 1 202 € »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `urssaf_invalidite_maximale_2026` : **625 euros par an** (2026)
  - Mesure : Cotisation maximale d'invalidité-décès (assiette de 1 PSS)
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Cotisations maximales », « Invalidité-décès » : « Cotisation maximale 625 € »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `urssaf_ij_minimale_2026` : **96 euros par an** (2026)
  - Mesure : Cotisation minimale d'indemnités journalières (assiette de 40 % du PSS)
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Vos cotisations minimales » : « Montant minimal annuel 96 € »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `urssaf_formation_artisan_2026` : **139 euros par an** (2026)
  - Mesure : Contribution à la formation professionnelle d'un artisan
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Vos cotisations minimales », formation professionnelle : « 139 € pour les artisans »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`
- [ ] `urssaf_retraite_base_minimale_2026` : **967 euros par an** (2026)
  - Mesure : Cotisation minimale de retraite de base (assiette de 450 heures de SMIC)
  - Où : Page « Taux de cotisations - Artisan, commerçant et profession libérale non réglementée » (mise à jour le 27 février 2026), Tableau « Vos cotisations minimales », retraite de base : « 5 409 € (450 × Smic horaire) », « 17,87 % », « Montant minimal annuel 967 € »
  - Document : https://www.urssaf.fr/accueil/outils-documentation/taux-baremes/taux-cotisations-ac-plnr.html ; fichier : `data/raw/menages/independants/urssaf_taux_ac_plnr.pdf`

### Non repéré (1)

- [ ] `drees_pension_nette_moyenne_droit_direct_2023` : **1 541 euros par mois** (2023)
  - Mesure : Même pension, nette des prélèvements sociaux
  - Où : Les retraités et les retraites, édition 2025, fiche 5 « Le niveau des pensions », Premier paragraphe de la fiche : « soit 1 541 euros nets des prélèvements sociaux » ; tableau 1, ligne 2023
  - Document : https://drees.solidarites-sante.gouv.fr/sites/default/files/2025-07/Fiche%2005%20-%20Le%20niveau%20des%20pensions.pdf ; fichier : `data/raw/menages/drees_retraites_2025_fiche05.pdf`

## Hypothèses

- [ ] `tva_repartition_produits_mixtes_stable` : **0 écart relatif de la part au taux réduit par rapport à l'année de référence (2023)**, plage -0,004 à 0,004
  - Répartition par taux des produits relevant de plusieurs taux de TVA, stable d'une année à l'autre
  - Sources : plf2025_voies_et_moyens_tome2 ; instruments : tva
- [ ] `tva_ecart_territorial_stable` : **0 écart relatif par rapport au montant de 2023**, plage -0,062 à 0,062
  - Écart de TVA dû aux taux particuliers d'outre-mer et de Corse, au niveau de 2023 pour toutes les années
  - Sources : plf2025_voies_et_moyens_tome2 ; instruments : tva
- [ ] `dette_part_refinancement_debut_annee` : **0 fraction du refinancement annuel**, plage 0 à 1
  - Part du refinancement de l'année réalisée dès le 1er janvier plutôt qu'au fil de l'année
  - Sources : plf2027_pap_engagements_financiers_etat ; instruments : dynamique_dette
- [ ] `baseline_part_refinancee` : **0,194 fraction de la dette de début d'année**, plage 0,193 à 0,194
  - Part de la dette publique refinancée chaque année au taux de marché, de 2031 à 2046
  - Sources : plf2027_pap_engagements_financiers_etat ; instruments : baseline
- [ ] `baseline_ajustement_stock_flux` : **0 points de PIB par an**, plage 0 à 0,5
  - Ajustement stock-flux annuel de 2031 à 2046
  - Sources : plf2027_resf ; instruments : baseline
- [ ] `baseline_cout_vieillissement_variantes` : **0 écart en 2046 à la variation 2030-2046 du scénario de référence, points de PIB**, plage -0,358 à 0,948
  - Variation du coût du vieillissement après 2030 selon les variantes de l'Ageing Report 2024
  - Sources : ce_ageing_report_2024 ; instruments : baseline
- [ ] `baseline_croissance_volume` : **0,609 % par an (valeur centrale et borne basse : Ageing Report en 2031, la série varie ensuite ; borne haute maintenue sur toute la période)**, plage 0,609 à 1
  - Croissance du PIB en volume de 2031 à 2046
  - Sources : ce_ageing_report_2024, plf2027_resf ; instruments : baseline
- [ ] `baseline_taux_marche` : **3,609 % (valeur centrale et borne basse : Ageing Report en 2031, la série varie ensuite ; borne haute maintenue sur toute la période)**, plage 3,609 à 4,3
  - Taux d'intérêt de marché auquel la dette est refinancée de 2031 à 2046
  - Sources : ce_ageing_report_2024, plf2027_resf ; instruments : baseline
- [ ] `scenario_rendement_constant_pib` : **0 écart relatif au rendement de l'année de référence rapporté au PIB**, plage 0 à 0
  - Rendement d'une mesure constant en points de PIB après son entrée en vigueur
  - Sources : insee_comptes_nationaux_2025, plf2027_resf ; instruments : tva, accises_energie, impot_societes
- [ ] `accises_masses_volumiques` : **0 écart relatif aux masses volumiques de la Base Carbone (gazole 832, essences 747, fioul domestique 845 kg/m³)**, plage -0,016 à 0,016
  - Masses volumiques servant à convertir en litres les ventes de carburants publiées en tonnes
  - Sources : ademe_base_carbone_pci_masse_volumique, sdes_conso_produits_petroliers ; instruments : accises_energie
- [ ] `accises_gpl_part_carburant` : **0 fraction des ventes de GPL**, plage 0 à 1
  - Part des ventes de GPL taxée au tarif carburant plutôt qu'au tarif combustible
  - Sources : sdes_conso_produits_petroliers, openfisca_france_176_1_2 ; instruments : accises_energie
- [ ] `accises_tarif_moyen_gnr_2024` : **24,81 €/hl**, plage 18,82 à 24,81
  - Tarif moyen d'accise appliqué en 2024 aux ventes de gazole non routier
  - Sources : ministere_guide_fiscalite_energies_2026 ; instruments : accises_energie
- [ ] `depenses_fiscales_ecart_depense` : **0 écart relatif au coût prévu**, plage -0,362 à 0,575
  - Écart entre le coût réalisé et le coût prévu d'une dépense fiscale
  - Sources : plf2024_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `depenses_fiscales_ecart_impot_revenu` : **0 écart relatif au coût prévu**, plage 0 à 0,062
  - Écart entre le coût réalisé et le coût prévu des dépenses fiscales (impôt sur le revenu)
  - Sources : plf2024_voies_et_moyens_tome2, plf2025_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `depenses_fiscales_ecart_impot_revenu_et_societes` : **0 écart relatif au coût prévu**, plage -0,02 à 0,012
  - Écart entre le coût réalisé et le coût prévu des dépenses fiscales (impôt sur le revenu et impôt sur les sociétés)
  - Sources : plf2024_voies_et_moyens_tome2, plf2025_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `depenses_fiscales_ecart_impot_societes` : **0 écart relatif au coût prévu**, plage -0,17 à 0,087
  - Écart entre le coût réalisé et le coût prévu des dépenses fiscales (impôt sur les sociétés)
  - Sources : plf2024_voies_et_moyens_tome2, plf2025_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `depenses_fiscales_ecart_autres_impots_directs` : **0 écart relatif au coût prévu**, plage -0,035 à 0,024
  - Écart entre le coût réalisé et le coût prévu des dépenses fiscales (autres impôts directs)
  - Sources : plf2024_voies_et_moyens_tome2, plf2025_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `depenses_fiscales_ecart_enregistrement_timbre` : **0 écart relatif au coût prévu**, plage 0 à 4,948
  - Écart entre le coût réalisé et le coût prévu des dépenses fiscales (droits d'enregistrement et de timbre)
  - Sources : plf2024_voies_et_moyens_tome2, plf2025_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `depenses_fiscales_ecart_autres_droits` : **0 écart relatif au coût prévu**, plage 0 à 2,8
  - Écart entre le coût réalisé et le coût prévu des dépenses fiscales (autres droits)
  - Sources : plf2024_voies_et_moyens_tome2, plf2025_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `depenses_fiscales_ecart_impots_locaux` : **0 écart relatif au coût prévu**, plage 0 à 0,2
  - Écart entre le coût réalisé et le coût prévu des dépenses fiscales (impôts locaux)
  - Sources : plf2024_voies_et_moyens_tome2, plf2025_voies_et_moyens_tome2, plf2026_voies_et_moyens_tome2 ; instruments : depenses_fiscales
- [ ] `credits_missions_ecart_execution` : **0 écart relatif aux crédits votés en loi de finances initiale**, plage -0,147 à 0,09
  - Écart entre les dépenses constatées et les crédits votés d'une mission du budget général
  - Sources : dgfip_plrg_2023, dgfip_plrg_2024, dgfip_plrg_2025 ; instruments : credits_missions
- [ ] `dotations_elasticite_investissement_communes` : **0,14 variation relative de l'investissement pour une variation relative de 1 des dotations**, plage 0,1 à 0,4
  - Élasticité de court terme de l'investissement des communes aux dotations de l'État
  - Sources : cdc_eclairages_8_dotations_investissement ; instruments : dotations_collectivites
- [ ] `dotations_elasticite_investissement_gfp` : **0,19 variation relative de l'investissement pour une variation relative de 1 des dotations**, plage 0,1 à 0,22
  - Élasticité de court terme de l'investissement des groupements à fiscalité propre (EPCI) aux dotations de l'État
  - Sources : cdc_eclairages_8_dotations_investissement ; instruments : dotations_collectivites
- [ ] `dotations_elasticite_investissement_departements` : **0,4 variation relative de l'investissement pour une variation relative de 1 des dotations**, plage 0,1 à 0,62
  - Élasticité de court terme de l'investissement des départements aux dotations de l'État
  - Sources : cdc_eclairages_8_dotations_investissement ; instruments : dotations_collectivites
- [ ] `dotations_elasticite_investissement_regions` : **0,32 variation relative de l'investissement pour une variation relative de 1 des dotations**, plage 0,1 à 0,32
  - Élasticité de court terme de l'investissement des régions aux dotations de l'État
  - Sources : cdc_eclairages_8_dotations_investissement ; instruments : dotations_collectivites
- [ ] `croissance_multiplicateur_depenses` : **0,78 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,78 à 1
  - Multiplicateur à un an d'une variation des dépenses publiques (crédits des missions, dotations, rémunérations)
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_multiplicateur_prestations` : **0,41 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,41 à 1
  - Multiplicateur à un an d'une variation des prestations (indexation, prime d'activité)
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_multiplicateur_tva` : **0,32 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,32 à 0,5
  - Multiplicateur à un an d'une variation de la TVA
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_multiplicateur_accises` : **0,51 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,5 à 0,51
  - Multiplicateur à un an d'une variation des accises sur les carburants
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_multiplicateur_cotisations_employeurs` : **0,2 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,2 à 0,5
  - Multiplicateur à un an d'une variation des cotisations patronales ou des allègements généraux
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_multiplicateur_csg` : **0,41 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,41 à 0,5
  - Multiplicateur à un an d'une variation de la CSG
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_multiplicateur_impot_revenu` : **0,41 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,41 à 0,5
  - Multiplicateur à un an d'une variation de l'impôt sur le revenu (barème et dépenses fiscales de l'impôt sur le revenu)
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_multiplicateur_autres_prelevements` : **0,5 point de PIB d'écart de production par point de PIB d'impulsion**, plage 0,2 à 0,51
  - Multiplicateur à un an d'une variation des autres prélèvements (impôt sur les sociétés, autres dépenses fiscales)
  - Sources : insee_mesange_2017, ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_persistance_ecart_production` : **0,7 sans unité**, plage 0,7 à 0,7
  - Part de l'écart de production d'une année qui subsiste l'année suivante
  - Sources : ofce_policy_brief_146 ; instruments : croissance
- [ ] `croissance_effet_ecart_production_solde` : **0,5 point de PIB de solde par point d'écart de production**, plage 0,5 à 0,63
  - Effet d'un point d'écart de production sur le solde public
  - Sources : ofce_policy_brief_146, intereconomics_2019_mourre_poissonnier, plf2027_resf ; instruments : croissance
- [ ] `retraites_duree_montee_en_charge` : **4 années**, plage 4 à 4,9
  - Durée de montée en charge du relèvement d'un an de l'âge effectif moyen de départ
  - Sources : cor_rapport_annuel_2026 ; instruments : retraites
- [ ] `menages_ecart_evolution_salaire_smic` : **0 écart relatif**, plage -0,002 à 0
  - Écart entre l'évolution des salaires médian et du 95e centile et celle du SMIC net, de 2024 à l'année simulée
  - Sources : insee_premiere_2079, insee_note_conjoncture_2026_03_salaires ; instruments : menages_types
- [ ] `menages_ecart_evolution_pension_moyenne` : **0 écart relatif**, plage 0 à 0,01
  - Écart entre l'évolution de la pension moyenne de droit direct et la revalorisation des pensions de base, de fin 2023 à l'année simulée
  - Sources : drees_retraites_2025_fiche05, dss_instruction_2023_189, dss_instruction_2024_176, cor_rapport_annuel_2026 ; instruments : menages_types
- [ ] `menages_ecart_evolution_revenu_independant` : **0 écart relatif**, plage -0,006 à 0
  - Écart entre l'évolution du revenu médian des non-salariés et celle du SMIC horaire brut, de 2023 à l'année simulée
  - Sources : insee_premiere_2060, insee_premiere_2114 ; instruments : menages_types
- [ ] `retraites_part_departs_non_decales` : **0,151 fraction**, plage 0,058 à 0,151
  - Part des départs à la retraite qui ne sont pas décalés par un relèvement de l'âge légal (ex-invalidité, handicap, inaptitude au travail)
  - Sources : drees_retraites_2025_donnees ; instruments : retraites
- [ ] `retraites_part_emploi_avant_liquidation` : **0,6772 fraction**, plage 0,5585 à 0,7997
  - Part en emploi, l'année précédant la liquidation, des personnes dont le départ est décalé
  - Sources : drees_retraites_2025_donnees ; instruments : retraites
- [ ] `retraites_ecart_pension_liquidants` : **-0,048 fraction**, plage -0,065 à -0,048
  - Écart entre la pension de droit direct des nouveaux retraités et celle de l'ensemble des retraités
  - Sources : drees_retraites_2025_donnees ; instruments : retraites
- [ ] `chomage_retour_prelevements` : **0,5 part du taux plein**, plage 0 à 1
  - Part du taux plein de CSG et de CRDS sur les allocations chômage qui revient aux administrations publiques quand les allocations varient
  - Sources : openfisca_france_176_1_2, unedic_parametres_utiles_juillet_2026 ; instruments : assurance_chomage
- [ ] `chomage_duree_rapport_hypotheses_unedic` : **1 rapport**, plage 0,896 à 1,104
  - Rapport à la valeur centrale de l'économie d'une réduction de la durée d'indemnisation, selon les hypothèses de l'Unédic sur le prolongement des droits des seniors
  - Sources : unedic_previsions_octobre_2026 ; instruments : assurance_chomage
- [ ] `chomage_duree_rang_croisiere` : **4 rang d'année**, plage 4 à 5
  - Rang de l'année où un changement du coefficient appliqué à la durée d'indemnisation produit son plein effet (1 = année d'entrée en vigueur)
  - Sources : unedic_effets_adaptation_conjoncture_2023 ; instruments : assurance_chomage
