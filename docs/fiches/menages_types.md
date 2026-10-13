---
module: menages_types
statut: beta
mise_a_jour: 2026-10-13
---

# Fiche : ménages types (cascade jusqu'au net après impôt)

Lot « ménages types », première partie (V1, prévu en parallèle de la phase 2). Fait en autonomie (instruction du mainteneur du 13 octobre 2026). Les choix du § 5, les 65 valeurs saisies (3 de l'Insee, 2 de la DREES, 2 de la Direction de la Sécurité sociale, 22 de service-public.gouv.fr, 36 du décret n° 2024-688 et des pages de l'Urssaf) et les trois corrections d'OpenFisca propres aux apprentis sont **à relire**.

## 1. Question posée

Pour un ménage type, combien coûte le travail à l'employeur, et que reste-t-il au ménage ? Les étapes sont le salaire brut, le net avant impôt, l'impôt sur le revenu, les prestations et le net après impôt. Cette première partie montre la situation sans réforme. Les effets des leviers viendront ensuite.

## 2. Profils

| Profil | Salaires | Enfants | Source du niveau de salaire |
|--------|----------|---------|-----------------------------|
| Célibataire au SMIC | SMIC à temps plein | aucun | OpenFisca (paramètres du SMIC) |
| Célibataire, salaire médian | médiane | aucun | Insee Première n° 2079 : 2 190 € nets par mois en 2024 |
| Cadre célibataire, 95e centile | 95e centile, salarié cadre | aucun | Insee Première n° 2079 : 5 593 € nets par mois en 2024 (2,55 fois la médiane) |
| Couple marié, deux enfants | médiane et SMIC | nés en 2016 et 2019 | Insee, OpenFisca |
| Parent seul, un enfant | SMIC, case T | né en 2019 | OpenFisca |
| Artisan | revenu d'un indépendant, aucun salaire | aucun | Insee Première n° 2060 : revenu d'activité médian des non-salariés classiques, 2 620 € par mois en 2023 |
| Retraité seul | pension moyenne de droit direct, aucun salaire | aucun | DREES, « Les retraités et les retraites » 2025, fiche 5 : 1 666 € bruts par mois fin 2023 (retraités résidant en France) |
| Apprenti de 19 ans | salaire minimum de l'apprentissage, contrat débuté le 1er septembre 2024 | aucun | service-public.gouv.fr, fiche F2918 : 43 % du SMIC en 1re année, 51 % en 2e, 67 % en 3e (18 à 20 ans) |

Les huit profils de la spécification sont couverts.

## 3. Méthode de calcul

Moteur : `moteur/src/fr_budget/menages/types.py`, avec OpenFisca-France 176.1.2 et les corrections du registre.

- **Année.** On calcule les revenus de 2025 :
  - les salaires et les prestations sont additionnés sur les douze mois de 2025 ;
  - l'impôt est celui dû sur ces revenus (impôt 2026), variable `impot_revenu_restant_a_payer` ;
  - les salaires de 2024 sont supposés égaux à ceux de 2025, car les prestations se calculent sur des ressources passées.
- **Salaires de l'Insee.** Le salaire net de l'Insee, net de cotisations, CSG et CRDS, correspond à `salaire_net` dans OpenFisca. On le porte en 2025 en gardant son rapport au SMIC net, puis on cherche par dichotomie le salaire brut qui donne ce net avec la législation de 2025.
  - Médiane : 2 821 € bruts par mois.
  - 95e centile, en cadre : environ 7 170 €.
- **Lignes.**
  - Coût employeur : `salaire_super_brut`.
  - Brut : `salaire_de_base`.
  - Net avant impôt : `salaire_net_a_payer`.
  - Prestations : `ppa`, `af`, `cf`, `asf`, `rsa` et `ars`.
  - Net après impôt : net avant impôt, moins l'impôt, plus les prestations.
- **Hypothèses d'emploi.** Ce sont celles du cas validé contre le modèle Urssaf : effectif de 4, taux AT/MP de 2,08 %, pas de mutuelle d'entreprise.

- **Apprenti.**
  - Salaire brut de chaque mois : pourcentage du SMIC de l'année d'exécution du contrat (43 %, 51 % puis 67 %), nul avant le contrat. Au-delà de la 3e année, le contrat est terminé : le calcul s'arrête au lieu de prolonger le dernier taux.
  - La rémunération d'apprenti qu'OpenFisca calcule lui-même est neutralisée. Elle repose sur des pourcentages antérieurs à la fiche F2918 et s'ajoute au salaire de base.
  - Trois corrections d'OpenFisca 176.1.2 (registre `corrections_openfisca.yaml`) appliquent les exonérations de la fiche F2918 :
    - cotisations salariales : sous 79 % du SMIC (contrat conclu avant le 1er mars 2025) ou 50 % (depuis) ;
    - CSG et CRDS : totale (avant), ou sous 50 % du SMIC (depuis) ;
    - impôt sur le revenu : dans la limite du SMIC, mois par mois.

- **Artisan.**
  - Entreprise individuelle à l'impôt sur le revenu, au régime réel, artisan (cotisations de la Sécurité sociale des indépendants).
  - Le revenu de l'Insee, net de cotisations, sert de résultat fiscal. Il est porté de 2023 à 2025 comme le SMIC horaire brut.
  - Les cotisations suivent l'assiette réformée de 2025 : revenu brut (avant cotisations et CSG déductible) moins un abattement de 26 %, compris entre 1,76 % et 130 % du plafond annuel de la Sécurité sociale.
    - Elles sont calculées par `moteur/src/fr_budget/menages/independants.py`, et non par OpenFisca : OpenFisca 176.1.2 applique les nouveaux taux à l'ancienne assiette.
    - Le revenu brut est retrouvé par dichotomie, à partir du résultat fiscal.
  - OpenFisca calcule l'impôt sur le revenu, avec le résultat fiscal en entrée (`rpns_imposables`). Il calcule aussi le RSA et la prime d'activité, qu'il lit dans `rpns_autres_revenus`. Sans cette seconde entrée, il versait un RSA à l'artisan.
- **Retraité.**
  - Pension brute de chaque mois : pension moyenne de fin 2023, multipliée par les coefficients de revalorisation des pensions de base au 1er janvier 2024 (1,053) et 2025 (1,022).
  - La CSG d'une pension dépend du revenu fiscal de référence de l'avant-dernière année, qui dépend à son tour de la CSG. Deux mesures arrêtent cette chaîne :
    - les pensions sont données de 2023 à 2025, et le revenu fiscal de référence de 2021 et 2022 est fixé à celui que le modèle calcule pour 2023 (point fixe) ;
    - le revenu fiscal de référence des années passées est calculé avant tout le reste. Sinon, OpenFisca met à zéro la CSG quand la même variable revient pour une autre année dans un même calcul, et le résultat dépend de l'ordre des calculs (constaté, puis vérifié par un test).

## 4. Données

| Jeu de données | Ce qu'il apporte |
|----------------|------------------|
| `insee_premiere_2079_pdf` | médiane et 95e centile des salaires nets en équivalent temps plein, 2024 (page 2, figure 3) |
| `registres/references/menages/impots_gouv_ir2026.json` | résultats du simulateur officiel de l'impôt (validation) |
| `service_public_*_html` (5 pages de service-public.gouv.fr) | barèmes de la prime d'activité, des allocations familiales, de l'ARS et de l'ASF au 1er avril 2026 ; base mensuelle des allocations familiales 2025 et 2026 (validation) |
| `drees_retraites_2025_fiche05_pdf` | pension moyenne de droit direct, fin 2023 (fichier déposé par le mainteneur) |
| `dss_instruction_2023_189_pdf`, `dss_instruction_2024_176_pdf` | coefficients de revalorisation des pensions de base, 2024 et 2025 |
| `service_public_f2971_html` | seuils et taux de CSG sur les pensions, 2026 (validation) |
| `insee_premiere_2060_pdf` | revenu d'activité médian des non-salariés classiques, 2023 |
| `decret_2024_688_pdf`, `decret_2025_708_pdf` | barèmes et assiette réformée des indépendants, à partir des cotisations de 2025 (fichiers déposés par le mainteneur) |
| `urssaf_reforme_assiette_independants_pdf`, `urssaf_taux_ac_plnr_pdf` | abattement de 26 %, taux de 2025 et 2026, montants minimaux et maximaux (pages de l'Urssaf enregistrées par le mainteneur) |
| `service_public_f2918_html` | salaire minimum de l'apprenti et exonérations (cotisations, CSG-CRDS, impôt) |
| `registres/references/menages/mesdroitssociaux_pa_2026.json` | résultats du simulateur officiel du RSA et de la prime d'activité (validation) |

## 5. Choix faits en autonomie, et leurs limites

1. **Cadre au 95e centile.** La spécification demande « 2 à 3 fois le médian ». Le 9e décile (4 334 €) n'en vaut que 1,98 fois ; le 95e centile est publié et en vaut 2,55 fois. Il dépasse le plafond de la Sécurité sociale, comme voulu.
2. **Rapport au SMIC constant** de 2024 à 2025 (hypothèse `menages_ecart_evolution_salaire_smic`, sans plage). Limite : en 2025, le SMIC et les salaires n'ont pas forcément évolué au même rythme.
3. **Couple** : un salaire médian et un SMIC, marié (déclaration commune), deux enfants de 6 et 9 ans au 1er janvier 2025. La spécification ne fixe pas ces valeurs.
4. **Parent seul** : l'allocation de soutien familial est comptée (2 392 € par an). Cela suppose que l'autre parent ne verse pas de pension alimentaire, ce qui est la situation par défaut d'OpenFisca. Avec une pension versée, le revenu serait différent.
5. **Aides au logement non comptées** : elles dépendent du loyer et de la zone, que la spécification ne fixe pas. Le net après impôt des ménages modestes est donc sous-estimé.
6. **Mêmes salaires en 2024 et en 2025** pour les ressources des prestations. Limite : les ressources de 2024 sont un peu surestimées (le SMIC de 2024 était plus bas), ce qui peut réduire légèrement les prestations calculées.
7. **Validation des prestations sur 2026, pas sur 2025.** Le simulateur officiel applique la législation du jour et demande les ressources des quatre derniers mois (juin à septembre 2026). Les cas de validation reprennent donc les ménages types avec la législation et les salaires de 2026. Limite : les prestations de 2025 affichées sur le site ne sont validées qu'à travers les mêmes formules, avec les paramètres de 2025 (seule la base des allocations familiales de 2025 est vérifiée directement).
8. **Logement des cas de validation.** Le simulateur exige un logement. Les cas sont saisis en locataire d'un logement vide à Paris 11e (code postal 75011), pour un loyer de 700 € hors charges, et le modèle est calculé avec ce même logement. Ce logement est un choix, sans source. Pour le parent seul, OpenFisca calcule alors une aide au logement, qui réduit la prime d'activité du « forfait logement ». Les ménages types du site restent calculés sans logement (choix 5).
9. **Prestations déclarées au simulateur.** Les allocations versées (ASF, allocations familiales) sont déclarées comme ressources, avec le montant d'OpenFisca net de CRDS arrondi à l'euro. L'allocation de rentrée scolaire, versée en août, n'est pas déclarée : le simulateur ne la propose pas.
10. **Salaire saisi dans le simulateur.** Le formulaire demande les salaires « en net fiscaux avant prélèvement à la source ». Mais la CAF retient le montant net social (service-public.gouv.fr, fiche F2882), et OpenFisca le salaire net (`ppa_revenu_activite_individu`). C'est ce salaire net qui est saisi (1 478 € par mois au SMIC au lieu de 1 531 € nets imposables), pour que le modèle et le simulateur partent du même revenu. Limite : si le simulateur convertit le net fiscal en un autre revenu, cette conversion n'est pas testée.

11. **Apprenti** : 19 ans, contrat débuté le 1er septembre 2024, payé au minimum légal, vit seul (déclaration d'impôt propre).
    - Le contrat est conclu avant le 1er mars 2025, pour que toute l'année 2025 relève d'un seul régime d'exonération.
    - Son salaire est sous 79 % du SMIC : net égal au brut, aucun impôt, pas de prime d'activité. Son salaire est sous le plancher d'OpenFisca pour les apprenants : 55 % de 169 heures de SMIC (paramètre `def_pac.revenu_plafond_pac_non_scolaire`), soit 1 104 € par mois en juin 2025.
    - Limite : rattaché au foyer de ses parents, il changerait leur impôt, ce qui n'est pas montré.
    - Les aides au logement, souvent versées à un apprenti qui vit seul, ne sont pas comptées (choix 5).
12. **Pas de salaire de janvier à août 2024**, avant le contrat. Cela compte pour les ressources des prestations de 2025.
13. **Exonération d'impôt appliquée mois par mois** (limite : SMIC mensuel), comme dans le modèle de l'Urssaf. La loi fixe une limite annuelle, ce qui revient au même pour un salaire régulier.

14. **Pension moyenne et non médiane.** La spécification demande la pension médiane. La fiche 5 de la DREES (édition 2025) ne publie que la moyenne de fin 2023 et une distribution de fin 2020. La moyenne est retenue, et le libellé le dit.
    - Limite : la moyenne dépasse sans doute la médiane, car les pensions élevées la tirent vers le haut.
15. **Pension revalorisée comme les pensions de base** (hypothèse `menages_ecart_evolution_pension_moyenne`, nulle, sans plage). Les pensions complémentaires suivent d'autres règles, et la pension moyenne évolue aussi avec le renouvellement des générations.
16. **Retraité** né en 1955, seul, sans pension de réversion ni autre revenu. OpenFisca lui applique en 2025 le taux réduit de CSG (3,8 %), sans CASA. Son revenu fiscal de référence de 2023 (15 864 €) est sous le plafond du taux réduit de 2025 d'OpenFisca, une valeur que la page consultée ne publie pas.
    - Limite : la règle des deux années consécutives de dépassement n'est pas en jeu pour ce profil, et n'est pas testée.
17. **Pension stable avant 2023** pour le calcul du taux de CSG de 2023 (point fixe, § 3).

18. **Artisan, revenu médian de l'Insee.** Le profil est un artisan, ce qui détermine la formation professionnelle (0,29 % du plafond de la Sécurité sociale). Le revenu de l'Insee couvre tous les non-salariés classiques hors agriculture : artisans, commerçants et professions libérales.
19. **Revenu de l'Insee pris comme résultat fiscal.** L'Insee le définit comme le revenu professionnel imposable, avec certaines exonérations et cotisations facultatives réintégrées. Le profil n'a ni exonération ni cotisation facultative.
20. **Revenu porté en 2025 comme le SMIC horaire** (hypothèse `menages_ecart_evolution_revenu_independant`, nulle, sans plage). L'Insee constate une baisse du revenu moyen des non-salariés en 2023, en euros constants.
21. **Partage de la CSG-CRDS** (9,7 %, Urssaf) en 6,8 % déductible, 2,4 % non déductible et 0,5 % de CRDS. Ces taux viennent de la ligne « revenus d'activité salariée » de service-public.gouv.fr, faute de source propre aux indépendants.
22. **Non représentés** : début d'activité (ACRE, assiettes forfaitaires), conjoint collaborateur, cotisations facultatives, régime micro-entreprise.

### Profil saisi par l'utilisateur (page « Mon ménage »)

Le moteur (`fr_budget.menages.personnalise`) traduit la saisie en profil et calcule la même cascade que pour les ménages types (`cascade_profil`). Le site l'appelle par `POST /mon-menage`.

23. **Règle 5 (aucun stockage).** La saisie part dans le corps d'une requête POST, jamais dans l'adresse : elle n'apparaît donc pas dans les journaux d'accès, qui sont de toute façon désactivés. Le moteur et l'API ne mettent rien en cache. Les messages d'erreur ne reprennent aucune valeur saisie. Le navigateur ne garde rien : ni stockage local, ni paramètre dans l'adresse, ni remplissage automatique. Un test vérifie que le journal de l'API ne contient aucune valeur saisie.
    - Limite : l'hébergeur de l'API voit passer la requête chiffrée ; son contrat doit exclure la capture des corps de requête.
24. **Statuts proposés** : salarié (salaire brut mensuel, case « cadre »), retraité (pension brute mensuelle), artisan (résultat fiscal mensuel moyen). Les autres indépendants (commerçants, professions libérales, micro-entrepreneurs) ne sont pas proposés, car leurs barèmes ne sont pas codés.
25. **Montant constant** sur toutes les années de la simulation, comme pour les ménages types. Il sert aussi aux ressources des prestations et au revenu fiscal de référence des années antérieures.
26. **Deux adultes forment un couple marié ou pacsé** (déclaration commune). Le concubinage, avec deux déclarations, n'est pas proposé. Un adulte seul avec enfants est compté parent isolé (case T), sans pension alimentaire (choix 4).
27. **Seule l'année de naissance est demandée.** La naissance est fixée au 1er janvier pour un adulte et au 1er juillet pour un enfant. Limite : l'âge exact compte pour certaines prestations (majorations des allocations familiales, rentrée scolaire), qui peuvent donc différer de quelques mois.
28. **Bornes de saisie** (`personnalise.py`, exportées pour le formulaire) : un ou deux adultes, au plus 8 enfants, montant de 0 à 100 000 € par mois, adultes de 16 à 110 ans, enfants de 0 à 25 ans. Ce sont des garde-fous de saisie, pas des paramètres du modèle ; ils n'ont pas de source et ne changent aucun résultat dans les bornes.
29. **Pas de validation propre.** Le calcul est celui des ménages types, validé sur ces profils. Un ménage saisi hors de leurs situations (revenus élevés, familles nombreuses, couple retraité et salarié) n'est pas comparé à un simulateur officiel. La page porte le bandeau bêta des ménages types.
30. **Service de calcul non hébergé.** Le site est statique ; il appelle l'API à l'adresse fixée à la construction (`NEXT_PUBLIC_API_URL`), qui doit autoriser l'origine du site (`FR_BUDGET_ORIGINES`). Tant que l'API n'est pas hébergée, la page l'indique et ne calcule rien.

### Effet des leviers sur les ménages types

Module `fr_budget.menages.leviers`. Chaque levier qui change directement la législation d'un ménage devient une réforme d'OpenFisca-France (paramètres ou formules, noms vérifiés dans le paquet installé) ; la cascade est recalculée sous cette réforme. Le site publie, pour chaque ménage et chaque levier, une hausse et une baisse d'une unité (un point ou 1 %) ; l'API (`GET /menages-types/effet`) calcule toute valeur dans les bornes du levier.

| Levier | Traduction pour les ménages |
|--------|-----------------------------|
| CSG sur les revenus d'activité | taux de CSG déductible (`csg.activite.deductible`), comme la hausse de 2018 ; même écart sur la CSG de l'artisan, calculée hors d'OpenFisca, à revenu avant cotisations inchangé |
| CSG sur les pensions (taux plein) | taux plein de CSG déductible des pensions ; taux réduit et médian inchangés |
| Taux de cotisation patronale du secteur privé | cotisation ajoutée au coût employeur, assise sur l'assiette des cotisations, hors du champ des allègements (lecture de la CCSS) |
| Allègements généraux | taux de la réduction générale (`taux_allegement_general`) et réductions des taux maladie et famille multipliés par 1 + x |
| Seuils du barème de l'impôt sur le revenu | limites des tranches, plafonds des effets du quotient familial et seuils de la décote multipliés par 1 + x |
| Pente de la prime d'activité | fraction des revenus professionnels prise en compte |
| Indexation des pensions et prestations | base mensuelle des allocations familiales, montants de base du RSA et de la prime d'activité multipliés par 1 + x |

Les autres leviers n'ont pas d'effet direct sur la cascade (TVA et accises : consommation ; CSG sur le capital : pas de patrimoine ; impôt sur les sociétés ; dotations et crédits : entre administrations ; rémunérations publiques : aucun agent public ; âge de départ : pensions futures ; dépenses fiscales : situations absentes des profils). La page le dit.

31. **Année et durée.** La mesure s'applique aux revenus de 2025, du 1er janvier au 31 décembre : effet en année pleine, sans changement de comportement. Les revenus et la législation des années précédentes (ressources des prestations, revenu fiscal de référence) ne changent pas.
32. **Prime d'activité.** OpenFisca lit les paramètres de la prime d'activité aux mois des ressources, les trois mois qui précèdent le droit. Modifiés au 1er janvier, ils ne joueraient que sur dix mois de droits (constaté : 10/12 de l'effet). Ils sont donc modifiés dès le 1er octobre de l'année précédente, pour que tous les droits de 2025 en tiennent compte.
33. **Réduction générale.** OpenFisca la régularise mois par mois (cumul depuis janvier moins les mois précédents). Multiplier le montant mensuel fausserait cette régularisation (constaté : −221 € au lieu de −859 € pour 10 %). Le facteur s'applique donc au taux de la réduction.
34. **Incidence des cotisations patronales : deux lectures.** Par défaut, lecture comptable : la mesure change le coût employeur, pas le salaire brut. Le réglage d'incidence propose aussi la lecture répercutée (choix 40 à 44). La page montre le résultat dans la lecture choisie et l'écart dans les deux lectures.
35. **Part déductible.** Une hausse de CSG porte sur la part déductible, comme en 2018 ; elle réduit donc aussi l'impôt. Une hausse sur la part non déductible donnerait un net après impôt un peu plus bas.
36. **Pension du retraité non revalorisée par le levier d'indexation.** Le levier ne porte que sur les pensions de base. La part de base dans la pension moyenne de la DREES n'est pas dans les sources du registre : l'effet n'est pas chiffré pour ce ménage, et la page le dit. Une source (par exemple le fichier Excel associé à la fiche 5 de la DREES, ou une pension de base moyenne publiée) permettrait de le chiffrer.
37. **Seuils de l'impôt non arrondis.** La loi arrondit les seuils revalorisés à l'euro ; le modèle ne les arrondit pas (écart de quelques euros au plus).
38. **Fourchette.** L'effet d'une mesure sur un ménage type est un calcul de la législation. Pour les cotisations patronales et les allègements, les deux lectures de l'incidence bornent l'écart (valeur centrale : la lecture comptable, par défaut). Pour les autres leviers, aucune hypothèse incertaine n'intervient : valeurs basse, centrale et haute confondues, jusqu'à des élasticités sourcées.
39. **Contrôles.** Aucun simulateur officiel ne calcule une législation réformée. Chaque effet est donc comparé à une identité calculée sans la réforme : un point de CSG retire un point de l'assiette de la CSG (après l'abattement de 1,75 %) ; une cotisation patronale d'un point ajoute un point de l'assiette au coût ; 10 % d'allègements en plus retirent 10 % des allègements au coût ; des seuils relevés de 1 % donnent l'impôt du barème aux seuils relevés (cadre, une part) ; un point de pente ajoute un point des revenus d'activité à la prime ; un point d'indexation ajoute 1 % aux allocations familiales.

#### Réglage d'incidence des cotisations patronales

40. **Deux lectures, sans part intermédiaire.** Lecture comptable (aucune répercussion) et lecture répercutée (répercussion complète sur le salaire brut). Une répercussion partielle demanderait une élasticité sourcée, absente du registre d'hypothèses : elle n'est pas proposée. Les deux lectures bornent donc l'effet, sans prétendre dire laquelle est la bonne.
41. **Lecture répercutée.** Le salaire brut de chaque salarié est ajusté pour que son coût employeur annuel, sous la mesure, égale celui de la législation de référence (méthode de la sécante ; précision de 2 euros par an, car le coût calculé par OpenFisca avance par marches de moins d'un euro : taux de la réduction générale arrondi à quatre décimales, calcul en simple précision). Le salaire ajusté vaut pour toutes les années simulées, y compris 2024, dont les salaires servent de ressources aux prestations de 2025.
42. **Plancher du SMIC.** Le salaire ne descend pas sous le SMIC mensuel à temps plein (paramètre d'OpenFisca), ni sous le salaire saisi s'il est déjà plus bas (temps partiel). Au SMIC, une hausse reste donc au coût employeur, comme en lecture comptable ; une baisse ou des allègements accrus peuvent, eux, relever le salaire.
43. **Apprenti.** Son salaire est fixé par la loi en pourcentage du SMIC : il ne s'ajuste pas. Les retraités et les indépendants n'ont pas de cotisations patronales.
44. **Leviers concernés.** Taux de cotisation patronale et allègements généraux. Les autres leviers ne touchent pas le coût employeur ; la lecture répercutée n'a pas d'objet pour eux (refusée par l'API, y compris pour un scénario sans mesure sur les cotisations patronales).

#### Scénario de plusieurs leviers

Module `fr_budget.menages.leviers` (`legislation_scenario`, `cascade_scenario`, `cascade_profil_scenario`) ; API `POST /menages-types/scenario` et `POST /mon-menage` (champ `scenario`).

45. **Une seule réforme.** Toutes les mesures du scénario sont appliquées ensemble dans une même réforme d'OpenFisca, puis la cascade est recalculée : les interactions (par exemple CSG déductible et impôt, revenus et prime d'activité) sont donc prises en compte, sans addition d'effets séparés.
46. **Effet non chiffré.** Si l'effet d'une seule mesure n'est pas chiffré pour un ménage (indexation et pension du retraité), le scénario entier n'est pas chiffré pour ce ménage, plutôt que d'afficher un effet partiel.
47. **Leviers sans effet direct.** Les leviers du simulateur qui ne changent pas la cascade (TVA, accises, impôt sur les sociétés, dotations, crédits, rémunérations publiques, âge de départ, dépenses fiscales) sont écartés du calcul et listés dans la réponse (`ignorees`) ; un levier inconnu ou une valeur hors de ses bornes est refusé.
48. **Ménage saisi.** Le même scénario s'applique au ménage saisi, sans cache ni journal (règle 5) ; la réponse donne la cascade avant et après.

#### Effet du scénario dans le simulateur et sur « Mon ménage »

49. **Approximation dans le simulateur.** Le site est statique et ne peut pas lancer OpenFisca. Les cascades exactes sont exportées sur une grille de valeurs de chaque levier (pas d'une unité, de 10 % pour les allègements, plus ou moins une unité). Pour une mesure, chaque ligne de la cascade est interpolée entre les deux valeurs de la grille qui l'encadrent ; les écarts des mesures sont additionnés ligne par ligne ; une prestation ne devient jamais négative. Le même calcul existe dans le moteur (`approximation`) et sur le site (`web/lib/effets-menages.ts`) ; un test du site vérifie qu'ils donnent les mêmes valeurs.
50. **Contrôle publié.** 32 scénarios de contrôle (chaque levier à ses bornes et entre deux points de la grille ; tous les leviers à la moitié de leurs bornes et à leurs bornes) sont calculés exactement, en une seule réforme, et comparés à l'approximation. Écart maximal constaté sur le net après impôt : 61 € par an pour une mesure seule (couple, prime d'activité qui s'annule entre deux points de la grille), 291 € par an pour toutes les mesures à leurs bornes (salaire médian, que la hausse de la pente rend éligible à la prime d'activité). Ces deux écarts sont affichés sous le résultat. La lecture répercutée sur le salaire est contrôlée à part, sur les scénarios aux bornes qui touchent les cotisations patronales (chaque levier concerné seul, puis tous les leviers ensemble), et son écart maximal est affiché quand cette lecture est choisie : 309 € par an pour toutes les mesures à leurs bornes. Pour une mesure seule, les bornes sont des points de la grille : l'écart y est nul par construction et n'apprend rien ; les valeurs intermédiaires ne sont pas contrôlées pour cette lecture, dont le calcul exact ajuste le salaire par itérations (durée de l'export).
    - Limite : une première version additionnait les effets d'une seule unité ; elle s'écartait jusqu'à 1 900 € du calcul complet, à cause des seuils de la prime d'activité. Elle n'a pas été publiée.
51. **Lecture de l'incidence dans le simulateur.** Quand une mesure touche les cotisations patronales, le panneau propose les deux lectures et donne, pour chaque ménage, l'écart du net après impôt dans les deux lectures (fourchette).
52. **Lien vers « Mon ménage ».** Le simulateur transmet les mesures (et la lecture de l'incidence) dans l'adresse de la page « Mon ménage », jamais la saisie du ménage. La page refuse un lien que le service de calcul refuserait (levier inconnu, valeur hors bornes, lecture répercutée sans mesure sur les cotisations patronales, lecture inconnue) et le signale. La page envoie la saisie et les mesures au service de calcul, qui fait le calcul complet (sans approximation) ; rien n'est gardé ni journalisé.

## 6. Validation

**Impôt sur le revenu.**
- Test : `moteur/tests/validation/test_menages_impot_revenu.py`.
- Référence : simulateur officiel de l'impôt 2026 sur les revenus 2025, modèle simplifié, interrogé le 13 octobre 2026 par `outils/references_impots/generer.mjs`.
- Tolérance : 2 € par an. Le simulateur reçoit des salaires arrondis à l'euro et arrondit l'impôt à l'euro.

| Ménage type | Parts | Revenu fiscal de référence | Impôt, impots.gouv.fr | Impôt, modèle | Écart |
|-------------|------:|---------------------------:|----------------------:|--------------:|------:|
| Célibataire au SMIC | 1 | 15 959 € | 0 € | 0 € | 0 |
| Célibataire, médiane | 1 | 24 987 € | 1 243 € | 1 242 € | −1 € |
| Cadre, 95e centile | 1 | 63 806 € | 12 246 € | 12 246 € | 0 |
| Couple, deux enfants | 3 | 40 946 € | 0 € | 0 € | 0 |
| Parent seul, un enfant | 2 | 15 959 € | 0 € | 0 € | 0 |

Le nombre de parts et le revenu fiscal de référence sont identiques pour les cinq ménages.

**Salaire.** Pour le célibataire au SMIC, la cascade mensuelle (coût employeur, brut, net, imposable) est validée contre le modèle Urssaf (fiche `cascade_salaire`).

**Artisan.**
- **Impôt.** Le simulateur complet d'impots.gouv.fr (bénéfice en case 5KC) donne le même revenu fiscal de référence (33 142 €) et le même impôt (3 047 €) que le modèle.
- **Barème des cotisations.**
  - Aucun simulateur accessible n'applique l'assiette réformée : le modèle de l'Urssaf 11.1.0 garde l'ancienne. Les fonctions du barème sont donc confrontées aux montants que l'Urssaf calcule sur sa page des taux de 2026 (`moteur/tests/validation/test_menages_independant.py`, tolérance 1 €).
  - 5 montants sur 6 concordent : retraite de base minimale (967 €), indemnités journalières minimale (96 €) et maximale (1 202 €), invalidité-décès maximale (625 €), formation professionnelle (139 €).
  - Écart publié : l'Urssaf affiche une retraite complémentaire maximale de 17 494 €, soit 9,1 % de 4 plafonds. Le décret (art. D. 635-7) applique 8,1 % jusqu'à 1 plafond puis 9,1 %, ce qui donne 17 013 €. Le modèle suit le décret.
- **Non validé** : les cotisations de l'artisan type lui-même (11 401 € de cotisations, 3 367 € de CSG-CRDS sur 46 903 € de revenu brut). Aucun exemple chiffré publié ne porte sur un revenu comparable.

**Retraité.**
- Impôt : le simulateur d'impots.gouv.fr donne le même revenu fiscal de référence que le modèle (17 216 €) et le même impôt restant à payer (0 €). La pension est déclarée en case 1AS.
- CSG des pensions : les 9 valeurs du barème de 2026 publiées sur service-public.gouv.fr (fiche F2971) sont égales aux paramètres d'OpenFisca : seuils du taux zéro, du taux réduit et du taux médian, leurs majorations par demi-part, et les trois taux. Test : `moteur/tests/validation/test_menages_retraite.py`.
- Limite : les seuils de 2025, qui s'appliquent au profil (revenus de 2023), ne sont pas publiés sur la page consultée. Ils ne sont pas vérifiés directement.

**Apprenti.**
- La cascade mensuelle est comparée au modèle de calcul de l'Urssaf (fiche `cascade_salaire`, deux cas d'apprentis).
- Le brut, le net et le net imposable sont dans la tolérance de 0,50 € par mois.
- Le coût employeur est hors tolérance : +2,43 € et +2,22 € par mois. OpenFisca applique encore une exonération patronale propre aux apprentis au lieu de la réduction générale, et compte la taxe d'apprentissage. L'écart est publié tel quel.
- Impôt : le simulateur d'impots.gouv.fr donne 0 €, comme le modèle (déclaration sans salaire imposable). Le simulateur n'affiche pas de revenu fiscal de référence quand il est nul : le test lit une ligne absente comme 0.

**Barèmes des prestations.**
- Test : `moteur/tests/validation/test_menages_prestations.py`.
- Référence : fiches de service-public.gouv.fr, téléchargées le 13 octobre 2026 (montants au 1er avril 2026). Les montants publiés des prestations familiales sont nets de CRDS : le montant d'OpenFisca est multiplié par (1 − 0,5 %), taux de la CRDS dans OpenFisca.
- Tolérance : 0,02 €.

| Barème | Publié | Modèle | Écart |
|--------|-------:|-------:|------:|
| Base mensuelle des allocations familiales, avril 2026 | 478,16 € | 478,16 € | 0 |
| Base mensuelle des allocations familiales, avril 2025 | 474,37 € | 474,37 € | 0 |
| Prime d'activité : montant forfaitaire, personne seule | 638,28 € | 638,28 € | 0 |
| Prime d'activité : part des revenus professionnels | 59,85 % | 59,85 % | 0 |
| Prime d'activité : seuil de la bonification (59 heures de SMIC dans OpenFisca) | 726,29 € | 726,29 € | 0 |
| Allocations familiales, deux enfants, couple du ménage type | 152,25 € | 152,24 € | −0,01 € |
| Allocation de rentrée scolaire, 6 à 10 ans | 426,87 € | 426,86 € | −0,01 € |
| Allocation de soutien familial, parent seul du ménage type | 200,78 € | 200,77 € | −0,01 € |

Les écarts d'un centime viennent de l'arrondi du montant net de CRDS. La page de l'ASF donne aussi 201,78 € dans un intertitre, où la même phrase cite 200,78 € : c'est la valeur du texte (« Le montant de l'ASF s'élève à 200,78 € par mois et par enfant ») qui est retenue.

Le barème ne suffit pas pour la prime d'activité : la courbe de la bonification n'est pas publiée. Le montant complet est donc comparé au simulateur officiel.

**Prime d'activité, simulateur officiel.**
- Référence : simulateur du RSA et de la prime d'activité de mesdroitssociaux.gouv.fr, sans connexion, interrogé par `outils/references_prestations/generer.mjs`. Le simulateur de la CAF n'a pas été utilisé : il est protégé par un test anti-robot, que le projet ne contourne pas.
- Cas : `registres/references/menages/cas_prestations.json`, écrit par `pipelines/menages/cas_prestations.py` (choix 7 à 10).
- Montant comparé : la prime d'activité d'OpenFisca nette de CRDS (`ppa_nette_crds`), comme un montant versé.
- Tolérance : 2 € par mois. Le simulateur reçoit des ressources arrondies à l'euro et donne un montant à l'euro.

**Aucun cas n'est encore validé.** Le 13 octobre 2026, le service des communes (geo.api.gouv.fr), que le simulateur utilise à l'étape du logement, n'était plus joignable. Le simulateur renvoyait une erreur 500 à cette étape, et il exige une commune même pour une personne sans domicile stable. Les étapes foyer et ressources passent pour les trois cas. Il suffit de lancer `npm run generer` quand le service répond.

Un premier essai, fait avant la panne avec le célibataire au SMIC, n'est pas retenu comme référence : il ne part pas du même revenu que le modèle.
- Il saisissait le salaire net imposable (1 531 €), alors qu'OpenFisca calcule la prime d'activité sur le salaire net (1 478 €).
- Le simulateur a donné 230 € par mois. Le modèle donne 230,87 € (229,72 € net de CRDS) avec son salaire net de 1 478 €.
- Si le salaire net valait 1 531 €, OpenFisca donnerait 222,67 €, soit 7 € de moins que le simulateur.

Deux lectures sont possibles : soit le simulateur convertit le net fiscal saisi en un revenu plus bas, proche du net social ; soit le modèle s'écarte du simulateur. Le prochain relevé (choix 10) le dira.

Le module reste en bêta.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-13 | Effet du scénario dans le simulateur (approximation sur grille, contrôle publié) et sur « Mon ménage » (calcul complet) | Aucun test de validation ne bouge ; 5 nouveaux tests unitaires (approximation, grille), test d'API de l'export ; 4 tests du site (même approximation que le moteur sur les 32 scénarios de contrôle, adresse du scénario) |
| 2026-10-13 | Scénario de plusieurs leviers sur les ménages types et le ménage saisi (moteur et API) | Aucun test de validation ne bouge ; 5 nouveaux tests unitaires (mesures, scénario vide, deux leviers indépendants, non chiffré, profil saisi) ; 5 tests d'API |
| 2026-10-13 | Réglage d'incidence des cotisations patronales (lectures comptable et répercutée sur le salaire) | Aucun test de validation ne bouge ; 6 nouveaux tests unitaires (coût employeur gardé, plancher du SMIC, apprenti, allègements, mesure nulle, refus), tests d'API (refus de la lecture, export) |
| 2026-10-13 | Effet des leviers sur les ménages types (7 leviers traduits en réformes d'OpenFisca) | Aucun test de validation ne bouge ; 20 nouveaux tests unitaires (identités sans réforme), 6 tests d'API (route, refus, export) ; test du site (écart ligne par ligne) |
| 2026-10-13 | Profil saisi par l'utilisateur (moteur, `POST /mon-menage`, page « Mon ménage ») | Aucun test de validation ne bouge ; nouveaux tests unitaires (même cascade qu'un ménage type à saisie égale, bornes, absence de cache) et d'API (réponse, 422, journal sans valeur saisie, CORS) ; tests du site (corps POST, bornes) |
| 2026-10-13 | Profil artisan, cotisations selon l'assiette réformée de 2025 | Impôt : 2 nouveaux tests réussis (8 cas sur 8) ; barème : 6 nouveaux tests, 5 réussis, 1 hors tolérance (retraite complémentaire maximale, écart entre la page de l'Urssaf et le décret) ; test unitaire de l'ordre de la cascade et test de l'API adaptés à un indépendant |
| 2026-10-13 | Profil retraité (pension moyenne de la DREES, CSG selon le revenu fiscal de référence de l'avant-dernière année) | Impôt : 2 nouveaux tests réussis (7 cas sur 7) ; CSG des pensions : 9 nouveaux tests réussis ; test unitaire de l'ordre de la cascade et test de l'API adaptés à un ménage sans salaire |
| 2026-10-13 | Profil apprenti, avec trois corrections d'OpenFisca pour les apprentis | Impôt : 2 nouveaux tests réussis (6 cas sur 6) ; cascade Urssaf : 8 nouvelles comparaisons, 6 réussies, 2 hors tolérance (coût employeur) ; test unitaire de l'ordre de la cascade assoupli (brut égal au net possible pour l'apprenti) |
| 2026-10-13 | Validation des prestations : barèmes publiés ; cas du simulateur officiel de la prime d'activité préparés | 8 nouveaux tests de validation sur les barèmes, tous réussis ; aucun cas du simulateur (service des communes indisponible) |
| 2026-10-13 | Création : cinq ménages types salariés, cascade jusqu'au net après impôt | 11 nouveaux tests de validation (impôt, parts, revenu fiscal de référence), tous réussis |
