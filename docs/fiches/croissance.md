---
module: croissance
statut: beta
mise_a_jour: 2026-10-12
---

# Fiche : effet de croissance (multiplicateur budgétaire)

Lot 3.2 du plan (phase 3). Ce lot a été fait en autonomie (instruction du mainteneur du 12 octobre 2026). Les choix du § 5 et les 11 valeurs saisies sont **à relire**.

## 1. Question posée

Une mesure qui améliore le solde (hausse d'impôt, baisse de dépense) ralentit l'activité pendant quelques années. Cela réduit les recettes et augmente le ratio de dette, dont le PIB est le dénominateur. Une mesure qui dégrade le solde fait l'inverse. De combien cela change-t-il le solde et la dette ?

## 2. Ce que l'utilisateur règle

Une case « Inclure l'effet de la mesure sur l'activité (multiplicateur) », **décochée par défaut**, sur le simulateur. Son état passe dans le lien partagé (paramètre `c=1`) et dans la comparaison.

## 3. Méthode de calcul

Moteur : `moteur/src/fr_budget/croissance.py`. Intégration dans le scénario : `scenario(mesures, croissance=True)`.

Le calcul reprend le modèle simple de l'OFCE (Policy brief n° 146, juillet 2025, encadré 3, page 15) :

- **Impulsion.** L'impulsion d'une année est l'opposé de la variation de l'effet de la mesure sur le solde primaire. Une hausse d'impôt permanente donne une impulsion négative l'année d'entrée, puis nulle.
- **Écart de production.** OG(t) = ρ × OG(t−1) + m × impulsion(t). Le multiplicateur m dépend de l'instrument (§ 4) ; ρ = 0,7. Avec plusieurs mesures, les écarts s'additionnent.
- **Solde.** Le solde primaire reçoit l'effet de la mesure, plus α × OG(t), avec α = 0,5.
- **Dette.** Le PIB effectif vaut le PIB de la baseline multiplié par (1 + OG). Au premier ordre :

  d(t) = d(t−1) × (1 + r) / (1 + g) × (1 + OG(t−1) − OG(t)) − pb(t) + sfa(t)

  Dans le terme en OG, la dette de l'année précédente est celle de la baseline. Le calcul reste ainsi linéaire dans la valeur des leviers, ce dont le site statique a besoin. L'erreur est de l'ordre du produit de l'écart de dette par l'écart de production : environ 0,01 point pour une mesure de 1 point de PIB.
- **Fourchette.**
  - Valeur centrale : multiplicateur central.
  - Bornes : effet bas ou haut de la mesure, croisé avec le multiplicateur de chaque mesure, qui varie dans sa plage indépendamment des autres. La dette et le solde étant linéaires dans chaque multiplicateur, l'extrême de chaque année est la trajectoire au multiplicateur central plus, pour chaque mesure, l'écart le plus bas (ou le plus haut) de ses deux bornes. Jusqu'au 28 octobre 2026, un même bout de la plage valait pour toutes les mesures, ce qui rétrécissait la fourchette quand des mesures avaient des effets de signes opposés (revue de code).
  - Les variantes de la baseline encadrent les niveaux, comme sans l'effet de croissance.
- **Site.** Pour chaque levier, l'export donne le supplément d'une unité du levier pour un multiplicateur de 1. Le site ajoute m fois ce supplément.
  - Test de concordance : `api/tests/test_api_croissance.py`.

## 4. Multiplicateurs par instrument

Pour chaque catégorie, la valeur centrale est la variante du modèle Mésange (Insee et DG Trésor, document de travail G 2017/04) la plus proche ; il s'agit de l'effet sur le PIB à un an d'un choc de 1 % du PIB. La plage est bornée par cette variante et par le multiplicateur de l'OFCE : 0,5 pour les recettes, 1 pour les dépenses (Policy brief n° 146, page 17).

| Catégorie | Leviers | Centrale | Plage | Variante de Mésange |
|-----------|---------|---------:|------:|---------------------|
| Dépenses | crédits des missions, dotations, rémunérations | 0,78 | 0,78 à 1 | dépense publique générique (page 106) |
| Prestations | indexation, prime d'activité | 0,41 | 0,41 à 1 | aucune ; CSG et impôt sur le revenu (pages 116 et 118) |
| TVA | taux normal | 0,32 | 0,32 à 0,5 | TVA (page 113) |
| Accises | gazole, essences | 0,51 | 0,5 à 0,51 | taxe carbone (page 121) |
| Cotisations employeurs | taux, allègements généraux | 0,20 | 0,20 à 0,5 | cotisations employeurs (page 108) |
| CSG | activité, retraites, capital | 0,41 | 0,41 à 0,5 | CSG (page 116) |
| Impôt sur le revenu | seuils du barème, curseur des dépenses fiscales de l'IR | 0,41 | 0,41 à 0,5 | impôt sur le revenu (page 118) |
| Autres prélèvements | IS, surtaxe, autres dépenses fiscales, dépenses choisies une à une | 0,5 | 0,20 à 0,51 | aucune ; extrêmes des variantes de prélèvements |

## 5. Choix faits en autonomie, et leurs limites

1. **Modèle simple de l'OFCE plutôt que les profils de Mésange.** Mésange publie la réponse du PIB année par année, mais pour un choc permanent. Elle contient des effets d'offre de long terme : une baisse de cotisations y augmente le PIB de 1,7 % à long terme. Le modèle de l'OFCE ne garde que l'effet de demande, qui s'éteint.
   - Conséquence : l'effet de croissance est transitoire. À long terme, il ne reste dans la dette que le cumul des recettes perdues.
   - Limite : les effets d'offre (emploi, capital, incitations) ne sont pas représentés, ni dans un sens ni dans l'autre.
2. **Multiplicateur central = Mésange.** Le multiplicateur de Mésange est propre à l'instrument et vient d'un modèle officiel ; celui de l'OFCE sert de borne.
   - Conséquence : pour les recettes, la valeur centrale est au bas de la plage, sauf pour les accises. Pour les dépenses, elle est aussi au bas de la plage.
   - Lecture : le résultat central est plutôt favorable aux hausses d'impôts et aux baisses de dépenses. La borne haute de la fourchette montre l'autre lecture.
3. **Prestations.** Mésange n'a pas de variante de prestations. La valeur centrale reprend le canal du revenu des ménages (CSG, impôt sur le revenu) ; la borne haute est le multiplicateur des dépenses de l'OFCE, qui range les prestations parmi les dépenses.
4. **Impôt sur les sociétés.** Il n'existe pas de variante dans Mésange 2017 : le multiplicateur des recettes de l'OFCE est pris comme valeur centrale, avec une plage large.
5. **ρ et α sans plage.** Une seule source a été saisie pour chacun (valeurs « usuelles » citées par l'OFCE). La fourchette sous-estime donc l'incertitude. Une seconde source (Commission européenne, OCDE) est à ajouter.
6. **Pas de conjoncture ni de politique monétaire.** Le multiplicateur ne dépend ni de l'état de l'économie (plus élevé en récession selon l'OFCE, page 14), ni d'une réaction de la BCE. Les variantes de Mésange sont à taux d'intérêt réels inchangés.
7. **Mésange 2017 date.** Le modèle a été réestimé en 2017 sur des données antérieures. Le document de l'Insee de 2024 (DT 2024-07) donne des intervalles de confiance seulement pour l'investissement public : il n'est pas repris.
8. **Dépenses fiscales choisies une à une.** Le site les regroupe dans un levier générique, qui prend le multiplicateur des « autres prélèvements », même pour une dépense de l'impôt sur le revenu (correction après la revue de la PR, pour que le site et le moteur concordent).
   - Limite : une dépense de l'impôt sur le revenu choisie seule a un multiplicateur central de 0,5 au lieu de 0,41.
9. **Poids des données du site.** Le supplément de croissance double les réponses exportées : la page du simulateur passe d'environ 225 à 610 ko compressés. Depuis le lot 3.6, ces données sont chargées à part, une fois par visite : la page elle-même ne pèse plus que 27 ko compressés.

## 6. Validation

Aucune validation indépendante n'est possible à ce stade : les paramètres sont repris des sources, pas estimés. Les tests vérifient :

- les calculs construits à la main (`moteur/tests/unitaires/test_croissance.py`) ;
- la reprise exacte des valeurs saisies (centrale de Mésange, bornes de Mésange et de l'OFCE) ;
- la concordance du calcul du site avec celui du moteur (`api/tests/test_api_croissance.py`) ;
- l'interrupteur désactivé par défaut, sans effet sur les autres résultats (`moteur/tests/unitaires/test_scenario_croissance.py`).

Une confrontation à un chiffrage ex post de l'effet d'une consolidation passée (par exemple les prévisions de l'OFCE) reste à faire.

Le module reste en bêta.

## 7. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-28 | Revue de code : multiplicateur de chaque mesure indépendant dans les bornes (au lieu d'un bout commun) ; moteur et site | aucun test de validation (interrupteur désactivé par défaut) ; une mesure seule : inchangé ; TVA +2 points et défense +20 % en 2027, écart de dette 2030 : [−0,915 ; −0,670] → [−1,032 ; −0,521] ; 2 tests unitaires et 1 test du site ajoutés |
| 2026-10-12 | Revue de la PR : dépenses fiscales choisies une à une rattachées aux « autres prélèvements » | aucun test de validation ; 1 test unitaire ajouté |
| 2026-10-12 | Création du module | aucun test de validation (interrupteur désactivé par défaut) ; 59 nouveaux tests unitaires et d'API, tous passent |
