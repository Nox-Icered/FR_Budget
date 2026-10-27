# Confrontation des leviers à des sources indépendantes

Règle de publication (CLAUDE.md) : un levier est confronté à une source indépendante de l'administration (IPP, OFCE, Cour des comptes, Commission européenne) et l'écart est publié. Lot du 14 octobre 2026, fait en autonomie ; les valeurs saisies sont **à relire** (`registres/references/chiffrages.yaml`, champ `independante: true`).

Méthode de recherche : documents publiés par l'IPP, l'OFCE, la Cour des comptes (copies de la DILA sur vie-publique.fr, ccomptes.fr ne répondant pas depuis l'environnement de travail), le HCFP et, à défaut, Fipeco. Chaque valeur a été relue dans le document téléchargé ; l'empreinte du fichier lu est notée dans la localisation. Les documents ne sont pas reproduits dans le dépôt (licence non précisée) : seuls l'URL, la citation et l'empreinte y figurent.

Tests : `moteur/tests/validation/test_confrontations_independantes.py` (tolérance ±10 %) ; affichage : page Validation (colonne « Confrontation à une source indépendante » et mention sur chaque référence).

## Résultats

| Levier | Mesure (source) | Modèle | Référence | Écart |
|--------|-----------------|-------:|----------:|------:|
| TVA | Un point des quatre taux, recettes (IPP, juin 2025) | 14,18 Md€ | 13,0 | +9,1 % |
| TVA | Même mesure, net des achats des administrations (IPP) | 11,59 Md€ | 11,0 | +5,4 % |
| Impôt sur le revenu | Gel du barème 2026, inflation de 1 % (IPP, octobre 2025) | 1,89 Md€ | 1,1 | **+71,5 %** |
| Impôt sur le revenu | Même mesure, inflation de 1,3 % (IPP, juin 2025) | 2,45 Md€ | 1,4 | **+75,2 %** |
| Impôt sur le revenu | Gel total du barème, revalorisation évitée de 1,1 % (OFCE, juin 2025) | 2,08 Md€ | 1,2 | **+73,0 %** |
| Indexation | Gel des pensions de base 2026, inflation de 1 % (IPP) | 2,89 Md€ | 2,4 | **+20,2 %** |
| Indexation | Même mesure, inflation de 1,3 % (IPP) | 3,75 Md€ | 3,0 | **+25,1 %** |
| Rémunérations publiques | Point d'indice +1 %, trois fonctions publiques (Cour des comptes, juin 2017) | 1,88 Md€ | 2,07 | −9,2 % |
| Rémunérations publiques | Même mesure, État y compris opérateurs | 0,80 Md€ | 0,88 | −9,0 % |
| Rémunérations publiques | Même mesure, territoriale | 0,58 Md€ | 0,64 | −9,6 % |
| Rémunérations publiques | Même mesure, hospitalière | 0,50 Md€ | 0,55 | −9,3 % |
| Rémunérations publiques | Point d'indice +1 %, hors cotisations des employeurs (Fipeco, juillet 2026, source de second rang) | 2,37 Md€ | 2,5 | −5,1 % |

## Lecture des écarts

- **Impôt sur le revenu.** Le modèle reprend le chiffrage de l'administration (évaluation préalable du PLF 2025, `fr_budget.agrege.impot_revenu`), qui reproduit aussi le chiffrage du gel de 2026 du PLF 2026 (1,9 Md€). L'IPP et l'OFCE, avec leurs propres microsimulations (TAXIPP, INES), trouvent 40 % de moins. Le calcul par décile du modèle (fiche `impot_revenu.md`, § 3 : 1,09 Md€ pour 1 %) est proche de ces deux sources. L'écart porte donc sur les chiffrages officiels eux-mêmes ; leur cause (paramètres gelés, comportements, données de revenus) n'est pas établie. Le levier reste en bêta. Décision du mainteneur (27 octobre 2026) : la valeur centrale reste le chiffrage officiel ; l'écart est publié tel quel.
- **Pensions de base.** Le bloc « pensions » du modèle comprend les pensions de base et de l'État, de droit direct et dérivé, avec leurs majorations (comptes de la protection sociale). L'IPP ne détaille pas son périmètre au-delà de « pensions de retraite », complémentaires non gelées. Une partie de l'écart peut venir du périmètre ; elle n'est pas établie.
- **TVA.** L'IPP chiffre la hausse des quatre taux, pas du seul taux normal (levier du simulateur) ; la comparaison porte sur la ligne « ensemble » du modèle. La part payée par chaque type de contribuable vient chez l'IPP d'un document de travail de la DG Trésor.
- **Point d'indice.** La Cour des comptes ne précise pas si les cotisations des employeurs sont comprises ; le chiffre renvoie à des données de la direction du budget. Fipeco exclut les cotisations des employeurs.

## Avis du HCFP sur les PLF et PLFSS 2026 (déposé le 27 octobre 2026)

Avis n° HCFP-2025-5 du 9 octobre 2025 (fichier déposé par le mainteneur, sha256 130ae291dcad2c898327892305f1c8af79efaa836fd7e371d8fbfe3cd67b04ae, non reproduit). Le HCFP juge les prévisions du Gouvernement ; il ne produit pas ses propres chiffrages de mesures. Ce qu'il apporte :

- **Impôt sur le revenu** (page 17, § 67) : « À l'exception du gel du barème de l'impôt sur le revenu, qui doit rapporter 1,9 Md€, dont le chiffrage semble vraisemblable, les mesures nouvelles sont très peu documentées. » C'est une appréciation, pas une estimation : elle ne compte pas comme confrontation indépendante, mais elle est notée dans la fiche du levier.
- **Pensions** (page 21, note 10) : le gel de 2026 (3,6 Md€) se décompose en 2,9 Md€ sur les retraites (CAS pensions compris), 1,1 Md€ sur les autres prestations et −0,4 Md€ d'IR et de CSG. Ces montants viennent du scénario du Gouvernement ; ils sont ajoutés comme référence officielle (`indexation_pensions_gel_2026_hcfp`, non indépendante). Le modèle donne 2,89 Md€ (-0,5 %) : l'écart avec l'IPP (2,4 Md€) oppose donc l'IPP au chiffrage du Gouvernement.
- **Impôt sur les sociétés, accises** : seulement les montants du Gouvernement (surtaxe prolongée : 4 Md€ ; fiscalité énergétique : 1,6 Md€ de mesures nouvelles, tableau 5), sans estimation propre ni rendement unitaire. Rien d'utilisable pour ces leviers.

## Autres documents lus le 27 octobre 2026 (ccomptes.fr de nouveau joignable)

Bilan : aucun de ces documents ne fournit d'estimation indépendante comparable aux leviers ; l'impôt sur les sociétés et les accises restent en bêta.


- **Impôt sur les sociétés.** Le fichier de la Cour des comptes à l'adresse indiquée ci-dessous (point 1) est un document de travail de l'Insee : O. Arnal, U. Di Nallo, J.-P. Martin, « La réforme du taux statutaire de l'impôt sur les sociétés », document de travail n° 2025-18, septembre 2025 (109 pages, sha256 72f3d866562fccaa98f5b1ab615e4eb5bbd268a5c4052943a2e5d5e877c833b2). Il mesure le taux implicite d'imposition (20,7 % en 2016, 17,5 % en 2022) ; il ne chiffre ni le coût de la baisse du taux, ni le rendement d'un point de taux. Rien d'utilisable pour le levier. Le rapport d'évaluation de la Cour lui-même reste à trouver.
- **Accises (CPO, 2019).** Rapport « La fiscalité environnementale au défi de l'urgence climatique » (225 pages, sha256 d32d1883fff1af3a2e0f8d0f1be4374538adb56a253c596fe32ee9058b6803f8). Il reprend les chiffrages du PLF 2018 (convergence gazole-essence et trajectoire carbone, chiffrages de l'administration) et simule des trajectoires de la composante carbone jusqu'en 2030 avec le modèle ThreeME, comportements compris. Il ne donne pas de rendement statique d'un centime par litre : rien de comparable au levier, qui ne compte aucun changement de comportement.
- **Accises (Cour des comptes, 2024).** Observations définitives S2024-0646, « La place de la fiscalité de l'énergie dans la politique énergétique et climatique française », 6 septembre 2024 (149 pages, adresse corrigée fournie par le mainteneur : https://www.ccomptes.fr/sites/default/files/2024-09/20240906-S2024-0646-Place-fiscalite-energie-dans-politique-energetique-et-climatique-francaise_0.pdf, sha256 d2765ebb4f6f9188b6ae31c8e93f04f03d4aef3afde18c47b4be376c223b69ad). Le rapport donne le rendement global des accises (tableau n° 2 : fraction « autres produits énergétiques », 32,0 Md€ en 2021 et 32,5 Md€ en 2022, brut, « d'après données budgétaires »), qui couvre tous les produits pétroliers et non les seuls gazole et essences du levier, et une revue de la littérature sur les élasticités-prix (annexe), utile pour la V3 (élasticités comportementales). Il ne chiffre pas le rendement d'un centime par litre : rien de comparable au levier.

## Leviers sans confrontation indépendante (recherche du 14 octobre 2026)

| Levier | Ce qui a été trouvé |
|--------|---------------------|
| Accises sur les carburants | Aucun rendement par centime publié par une source indépendante. Pistes non lues (ccomptes.fr inaccessible) : CPO, « La fiscalité environnementale au défi de l'urgence climatique » (2019) ; Cour des comptes, « La place de la fiscalité de l'énergie dans la politique énergétique et climatique » (2024). |
| Impôt sur les sociétés | Ordre de grandeur indirect seulement (blog de l'IPP, 2024) ; surtaxe : montants publiés repris du gouvernement. Piste : Cour des comptes, « La réforme du taux statutaire de l'impôt sur les sociétés » (septembre 2025), à déposer. |
| CSG | Aucune valeur d'un point par assiette ; Fipeco et la Cour reprennent la Commission des comptes de la sécurité sociale. |
| Cotisations patronales et allègements | Coût des allègements : Cour des comptes (77,3 Md€ en 2024) et rapport Bozio-Wasmer, tous deux repris des annexes du PLFSS ; pas de chiffrage propre d'un point de cotisation. |
| Prime d'activité | Coût total (Cour des comptes, avril 2026 : 10,6 Md€ en 2024) ; aucun chiffrage indépendant d'un point de la fraction des revenus. |
| Dotations, crédits par mission, dépenses fiscales | Montants repris des documents budgétaires (Cour des comptes, OFGL, Fipeco) ; pas d'estimation indépendante d'une variation. |
| Retraites (âge de départ) | Déjà confronté aux modèles cités par le COR (tableau 2.10) ; Cour des comptes à rechercher. |

Pour ces leviers, la règle de publication ne peut pas être remplie avec les sources accessibles : ils restent en bêta, et la page Validation l'affiche (« Aucune pour l'instant »).

## Fichiers à déposer par le mainteneur (ccomptes.fr et hcfp.fr injoignables)

1. Cour des comptes, « La réforme du taux statutaire de l'impôt sur les sociétés », 22 septembre 2025 (l'adresse ci-après donne le document de travail de l'Insee, lu, voir ci-dessus ; le rapport de la Cour reste à trouver) : https://www.ccomptes.fr/sites/default/files/2025-09/20250922-reforme-taux-statutaire-impot-sur-les-societes.pdf
2. ~~Cour des comptes, « La place de la fiscalité de l'énergie dans la politique énergétique et climatique française », septembre 2024~~ (lu le 27 octobre 2026, voir ci-dessus) : https://www.ccomptes.fr/sites/default/files/2024-08/20240906-S2024-0646-Place-fiscalite-energie-dans-politique-energetique-et-climatique-francaise_0.pdf
3. ~~CPO, « La fiscalité environnementale au défi de l'urgence climatique », septembre 2019~~ (lu le 27 octobre 2026, voir ci-dessus) : https://www.ccomptes.fr/system/files/2019-09/20190918-CPO-fiscalite-environnementale_0.pdf
4. ~~HCFP, avis n° 2025-5 sur les PLF et PLFSS 2026~~ : déposé le 27 octobre 2026 (voir ci-dessus).
