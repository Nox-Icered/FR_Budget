---
levier: indexation_pensions_prestations
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : revalorisation des pensions et prestations

Lot 2.8 du plan (phase 2). Décisions du mainteneur du 12 octobre 2026, options (a) et bornes de -2 à +1 point :
- périmètre : pensions de base, pensions de l'État et prestations revalorisées par la loi ;
- effet net des retours aux administrations publiques, avec l'effet brut affiché à côté ;
- validation sur les chiffrages des PLFSS 2026 et 2027.

## 1. Question posée

Que changent pour le solde et la dette des pensions et prestations revalorisées de x point de plus (ou de moins) que la revalorisation prévue par la loi ? Exemple : « revalorisation inférieure de 1 point à la revalorisation légale ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Écart à la revalorisation légale, en points | 0 (revalorisation selon l'inflation) | de -2 à +1, par pas de 0,1 | règles légales (§ 3) |

Repère pour la borne basse : le gel de 2026 proposé par le PLFSS 2026 correspondait à -1,0 point, soit l'inflation hors tabac prévue pour 2025.

L'écart s'applique une fois, l'année choisie. Le niveau des prestations reste ensuite décalé d'autant : l'effet est tenu constant en points de PIB, comme pour le point d'indice.

Le levier ne peut pas être combiné avec les crédits de la mission « Solidarité, insertion et égalité des chances ». Cette mission finance l'AAH et la prime d'activité (programmes 157 et 304), qui sont comprises dans le levier. Le moteur refuse la combinaison, et le site bloque l'un quand l'autre est réglé.

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/indexation.py`, levier dans `scenario.py`).
- **Assiette** : prestations versées en 2024 par les administrations publiques, d'après les comptes de la protection sociale de la DREES, détaillées par code de prestation et par sous-secteur (S13111, S13112, S1313, S13141, S13142). L'extraction est faite par `pipelines/indexation/extraire_drees.py`. Les montants sont tenus constants en part du PIB nominal : PIB de l'INSEE pour 2025, croissance nominale du RESF 2027 ensuite.

| Bloc | Prestations | 2024 (Md€) | Revalorisation | Retour aux APU |
|------|-------------|-----------:|----------------|----------------|
| Pensions | pensions de base de droit direct et dérivé, majorations, pensions de l'État | 277,7 | janvier | CSG, CRDS, CASA, impôt sur le revenu |
| Minimum vieillesse | ASPA et anciennes allocations | 4,9 | janvier | aucun |
| Invalidité | pensions d'invalidité | 10,2 | avril | comme les pensions |
| AAH | allocation aux adultes handicapés | 13,8 | avril | aucun |
| ASI | allocation supplémentaire d'invalidité | 0,3 | avril | aucun |
| Famille | AF, CF, ASF, PAJE (base, naissance, adoption, PreParE), ARS | 26,1 | avril | CRDS |
| Handicap de l'enfant | AEEH, AJPP | 1,9 | avril | aucun |
| Rentes d'accidents du travail | rentes et rentes des ayants droit | 5,8 | avril | aucun |
| RSA | RSA socle | 12,0 | avril | aucun |
| Prime d'activité | prime d'activité | 10,6 | avril | aucun |
| **Total** | | **363,3** (370,2 en 2025) | | |

- **Dates de revalorisation.** Pour les pensions, le PLFSS 2027 (page 106) indique : « la revalorisation automatique des pensions au 1er janvier ». Pour les autres blocs, c'est la date de la dernière valeur du paramètre d'OpenFisca correspondant : montant de l'ASPA, revalorisation des pensions d'invalidité, montants de l'AAH, de l'ASI, du RSA et de la prime d'activité, BMAF, salaire minimum des rentes d'accidents du travail.
- **Exclusions** :
  - pensions complémentaires (Agirc-Arrco, Ircantec…) et supplémentaires : elles sont décidées par les partenaires sociaux ou par les régimes ;
  - aides au logement : leur indexation est propre ;
  - allocations chômage ;
  - retraite du combattant et pensions militaires d'invalidité : leur revalorisation suit des règles propres ;
  - complément de libre choix du mode de garde (7,3 Md€) : à relire, voir § 6 ;
  - prestations de santé, de dépendance (APA, PCH) et d'action sociale.
- **Retours sur les pensions.** Calculés avec OpenFisca (législation 2020) pour chaque tranche de 100 € de la distribution des pensions brutes totales de l'EIR 2020 (DREES, tableau 5), et pondérés par la masse de pension de chaque tranche. Pour la dernière tranche, « supérieur à 4 500 € », la pension retenue est 4 500 €. La CSG dépend du revenu fiscal de référence de N-2 : la pension est donc reprise de 2018 à 2020.

| Foyer | CSG, CRDS, CASA | Avec l'impôt sur le revenu |
|-------|----------------:|---------------------------:|
| Personne seule | 6,4 % | 21,5 % |
| Couple de deux retraités, même pension | 7,9 % | 25,4 % |

  Ces deux foyers forment les bornes de la fourchette ; la valeur centrale est à mi-chemin (choix à relire, faute d'une source sur la part des retraités en couple).
- **Coût d'un point de revalorisation en plus**, en année pleine, en Md€ de 2025 :
  - brut : 3,70 ;
  - net des prélèvements sociaux : 3,49 ;
  - net de l'impôt sur le revenu en plus : 3,01 (2,96 à 3,07).

  L'effet dans le scénario est moins le coût net. L'année d'entrée en vigueur n'en compte que 93,4 % : les prestations revalorisées en avril n'y pèsent que neuf mois (`scenario.facteur_premiere_annee`, ajouté après la revue de la PR).

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `drees_comptes_protection_sociale_csv` | prestations par code et par sous-secteur des APU | édition 2025, données 2024 |
| `drees_eir2020_distribution_pensions_xlsx` | distribution des pensions brutes totales (tableau agrégé, pas de micro-données) | fin 2020 |
| `plfss2026_projet_loi_pdf` | gel de 2026 (3,6 Md€), inflation hors tabac prévue pour 2025 | PLFSS 2026 |
| `plfss2027_projet_loi_pdf` | gel des prestations familiales de 2027 (0,5 Md€), inflation prévue pour 2026, date de revalorisation des pensions | PLFSS 2027 |
| `senat_rapport_plfss2026_tome1_pdf` | retour de CSG du gel (0,2 Md€), sous-indexation de 0,5 point (1,5 Md€), gel des prestations familiales (0,3 Md€) | 15 novembre 2025 |

Huit valeurs sont saisies dans `registres/references/chiffrages.yaml`, à relire.

## 5. Hypothèses et choix

- **Montants de 2024 tenus constants en part du PIB.** Les pensions ont crû plus vite que le PIB ces dernières années (revalorisations de 5,3 % en 2024 et de 2,2 % en 2025, PLFSS 2027) : l'assiette des années de validation est donc probablement sous-estimée.
- **Retours de 2020.** La législation et les pensions sont celles de 2020. Les seuils de CSG sont revalorisés chaque année, si bien que les taux par tranche bougent peu ; cela n'est pas vérifié.
- **Pensions d'invalidité** : même retour que les pensions de retraite. La CSG d'OpenFisca a le même barème pour les deux (paramètre `pensions_retraite_invalidite`).
- **Autres prestations** : aucun retour. OpenFisca ne modélise de prélèvement que sur les prestations familiales (CRDS).

## 6. Validation

Convention des PLFSS (« nets des effets CSG et CASA ») : le modèle est comparé net des prélèvements sociaux, avant impôt sur le revenu, pour la première année civile, avec la date de revalorisation de chaque bloc. Test : `moteur/tests/validation/test_levier_indexation.py`. Tolérance : ±10 %.

| Mesure | Millésime | Référence | Modèle | Écart | Dans la tolérance |
|--------|-----------|----------:|-------:|------:|-------------------|
| Gel de 2026, toutes prestations (1,0 point) | PLFSS 2026 | 3,60 Md€ | 3,35 Md€ | -6,9 % | oui |
| Sous-indexation de 0,5 point des pensions de base en 2027 | PLFSS 2026, lettre rectificative | 1,50 | 1,38 | -8,2 % | oui |
| Gel de 2026, prestations familiales (1,0 point) | PLFSS 2026, étude d'impact | 0,30 | 0,20 | -32,6 % | non |
| Gel des prestations familiales au 1er avril 2027 (2,1 points) | PLFSS 2027 | 0,50 | 0,44 | -12,7 % | non |
| Gel de l'AAH en 2026 (1,0 point) | PLFSS 2026 (rapport spécial du Sénat, page 27) | 122,4 M€ | 107,6 M€ | -12,1 % | non |

En brut, le gel de 2026 vaut 3,57 Md€ dans le modèle, contre 3,8 Md€ dans la référence (3,6 + 0,2 de CSG).

Le modèle est toujours en dessous des références. Explications possibles, non chiffrées :
- les montants de 2024 sont tenus en part du PIB (§ 5) ;
- le gel des plafonds de ressources n'est pas compté, alors que les PLFSS gèlent aussi les plafonds (article 44, VII et VIII) et réduisent ainsi le nombre de bénéficiaires ;
- le complément de libre choix du mode de garde est exclu : le compter ajouterait environ 0,06 Md€ au gel familial de 2026 et 0,12 Md€ à celui de 2027 ;
- l'inflation prévue n'est qu'une approximation du coefficient légal de revalorisation.

Le levier reste en bêta. Les références viennent toutes du Gouvernement ou du Parlement (qui reprend les évaluations du Gouvernement) : aucune source indépendante n'est encore confrontée. Il faudrait le rapport de la Cour des comptes sur la sécurité sociale ou une évaluation de l'IPP ou de l'OFCE.

## 7. Limites connues

- Les retraites complémentaires ne sont pas comprises. Une sous-indexation décidée à l'Agirc-Arrco (0,4 point en 2024-2026) relève des partenaires sociaux.
- Le retour d'impôt sur le revenu est celui de l'année ; l'impôt est en partie prélevé à la source, donc l'effet de calendrier est négligé.
- Aucun effet sur la consommation, la TVA ni le recours aux minima.
- Une mesure ciblée par montant de pension (PLFSS 2027 : revalorisation limitée aux pensions inférieures à 1 260 €) n'est pas modélisable avec ce levier uniforme.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-14 | Confrontation à l'IPP (gel des pensions de base 2026), `docs/validation/confrontations_independantes.md` | 2 nouvelles références indépendantes, hors tolérance (+20,2 % et +25,1 %) |
| 2026-10-12 | Ajout de la référence du gel de l'AAH en 2026 (demande du mainteneur) | 1 nouvelle référence, hors tolérance (-12,1 %) |
| 2026-10-12 | Revue de la PR : effet de la première année réduit aux mois qui suivent la revalorisation ; une mesure à zéro ne bloque plus de combinaison | aucun test de validation (ils portaient déjà sur la première année) |
| 2026-10-12 | Création du levier : extraction des comptes de la protection sociale et de la distribution des pensions de la DREES | 4 nouvelles références de validation, 2 dans la tolérance ; tableau : 36 sur 50 |
