---
module: menages_types
statut: beta
mise_a_jour: 2026-10-13
---

# Fiche : ménages types (cascade jusqu'au net après impôt)

Lot « ménages types », première partie (V1, prévu en parallèle de la phase 2). Fait en autonomie (instruction du mainteneur du 13 octobre 2026). Les choix du § 5 et les 10 valeurs saisies (2 de l'Insee, 8 barèmes de service-public.gouv.fr) sont **à relire**.

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

La spécification prévoit aussi un retraité, un indépendant et un étudiant ou apprenti. Ces profils demandent d'autres sources (pension médiane, cotisations des indépendants) : ils viendront dans une deuxième partie.

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

## 4. Données

| Jeu de données | Ce qu'il apporte |
|----------------|------------------|
| `insee_premiere_2079_pdf` | médiane et 95e centile des salaires nets en équivalent temps plein, 2024 (page 2, figure 3) |
| `registres/references/menages/impots_gouv_ir2026.json` | résultats du simulateur officiel de l'impôt (validation) |
| `service_public_*_html` (5 pages de service-public.gouv.fr) | barèmes de la prime d'activité, des allocations familiales, de l'ARS et de l'ASF au 1er avril 2026 ; base mensuelle des allocations familiales 2025 et 2026 (validation) |
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
- Référence : simulateur du RSA et de la prime d'activité de mesdroitssociaux.gouv.fr, sans connexion, interrogé le 13 octobre 2026 par `outils/references_prestations/generer.mjs`. Le simulateur de la CAF n'a pas été utilisé : il est protégé par un test anti-robot, que le projet ne contourne pas.
- Cas : `registres/references/menages/cas_prestations.json`, écrit par `pipelines/menages/cas_prestations.py` (choix 7 à 9).
- Tolérance : 2 € par mois. Le simulateur reçoit des ressources arrondies à l'euro et donne un montant à l'euro.

| Ménage type | Simulateur | Modèle | Écart |
|-------------|-----------:|-------:|------:|
| Célibataire au SMIC | 230 € | 230,87 € | +0,87 € |
| Parent seul, un enfant | non obtenu | 289,24 € | — |
| Couple, deux enfants | non obtenu | 91,50 € | — |

Limites :
- Le cas du célibataire a été saisi avec les scripts de mise au point qui ont précédé `generer.mjs` (mêmes étapes), avec une date de naissance de 1990 au lieu de 1995. L'âge n'a pas d'effet sur la prime d'activité au-delà de 25 ans.
- **Deux cas manquent.** Le 13 octobre 2026, le service des communes (geo.api.gouv.fr), que le simulateur utilise à l'étape du logement, n'était plus joignable, et le simulateur renvoyait une erreur 500 à cette étape. Les étapes précédentes (foyer, ressources) passent pour les deux cas. Il suffit de relancer `npm run generer -- parent_isole_1_enfant couple_2_enfants` quand le service répond.

Le module reste en bêta.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-13 | Validation des prestations : barèmes publiés et simulateur officiel de la prime d'activité | 9 nouveaux tests de validation (8 barèmes, 1 cas du simulateur), tous réussis |
| 2026-10-13 | Création : cinq ménages types salariés, cascade jusqu'au net après impôt | 11 nouveaux tests de validation (impôt, parts, revenu fiscal de référence), tous réussis |
