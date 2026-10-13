---
module: menages_types
statut: beta
mise_a_jour: 2026-10-13
---

# Fiche : ménages types (cascade jusqu'au net après impôt)

Lot « ménages types », première partie (V1, prévu en parallèle de la phase 2). Fait en autonomie (instruction du mainteneur du 13 octobre 2026). Les choix du § 5 et les 2 valeurs saisies sont **à relire**.

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

## 5. Choix faits en autonomie, et leurs limites

1. **Cadre au 95e centile.** La spécification demande « 2 à 3 fois le médian ». Le 9e décile (4 334 €) n'en vaut que 1,98 fois ; le 95e centile est publié et en vaut 2,55 fois. Il dépasse le plafond de la Sécurité sociale, comme voulu.
2. **Rapport au SMIC constant** de 2024 à 2025 (hypothèse `menages_ecart_evolution_salaire_smic`, sans plage). Limite : en 2025, le SMIC et les salaires n'ont pas forcément évolué au même rythme.
3. **Couple** : un salaire médian et un SMIC, marié (déclaration commune), deux enfants de 6 et 9 ans au 1er janvier 2025. La spécification ne fixe pas ces valeurs.
4. **Parent seul** : l'allocation de soutien familial est comptée (2 392 € par an). Cela suppose que l'autre parent ne verse pas de pension alimentaire, ce qui est la situation par défaut d'OpenFisca. Avec une pension versée, le revenu serait différent.
5. **Aides au logement non comptées** : elles dépendent du loyer et de la zone, que la spécification ne fixe pas. Le net après impôt des ménages modestes est donc sous-estimé.
6. **Mêmes salaires en 2024 et en 2025** pour les ressources des prestations. Limite : les ressources de 2024 sont un peu surestimées (le SMIC de 2024 était plus bas), ce qui peut réduire légèrement les prestations calculées.

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

**Pas encore validé** : les prestations (prime d'activité, allocations familiales, ASF, ARS). Le simulateur de la CAF n'a pas encore été interrogé. Le module reste en bêta.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-13 | Création : cinq ménages types salariés, cascade jusqu'au net après impôt | 11 nouveaux tests de validation (impôt, parts, revenu fiscal de référence), tous réussis |
