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

1. Cour des comptes, « La réforme du taux statutaire de l'impôt sur les sociétés », 22 septembre 2025 : https://www.ccomptes.fr/sites/default/files/2025-09/20250922-reforme-taux-statutaire-impot-sur-les-societes.pdf
2. Cour des comptes, « La place de la fiscalité de l'énergie dans la politique énergétique et climatique française », septembre 2024 : https://www.ccomptes.fr/sites/default/files/2024-08/20240906-S2024-0646-Place-fiscalite-energie-dans-politique-energetique-et-climatique-francaise_0.pdf
3. CPO, « La fiscalité environnementale au défi de l'urgence climatique », septembre 2019 : https://www.ccomptes.fr/system/files/2019-09/20190918-CPO-fiscalite-environnementale_0.pdf
4. HCFP, avis n° 2025-5 sur les PLF et PLFSS 2026 : https://www.hcfp.fr/sites/default/files/2025-10/Avis%20HCFP%202025%20%E2%80%93%205%20PLF-PLFSS%202026_0.pdf
