---
levier: impot_revenu_structure
statut: beta
mise_a_jour: 2026-11-05
---

# Fiche : plafond de l'avantage procuré par le quotient familial

Lot V2 « impôt sur le revenu (structure) », premier levier. Plan validé par le mainteneur le 5 novembre 2026 (option B révisée : calage sur le chiffrage de l'IGF et de l'IGAS de 2026, baisses de 2013 et 2014 en validation, Cour des comptes en confrontation). Les choix du § 5 et les 13 valeurs saisies sont **à relire**.

## 1. Question posée

Que changent pour le solde et la dette des plafonds de l'avantage procuré par le quotient familial relevés ou abaissés de x % ? Exemple : « baisse de 10 % des plafonds par demi-part ».

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| Variation des plafonds de l'avantage par demi-part pour charges de famille | 0 (plafond général lu dans OpenFisca pour les revenus de 2025) | de -25 à +25 %, par pas de 1 % | `openfisca_france_176_1_2` (`plaf_qf.plafond_avantages_procures_par_demi_part.general`) |

Borne : -25 % est la plus forte baisse chiffrée (PLF 2014, `qf_plafond_2013` → `qf_plafond_2014`). La même amplitude est retenue à la hausse.

## 3. Méthode de calcul

- Moteur : agrégé (`moteur/src/fr_budget/agrege/quotient_familial.py`, levier `ir_plafond_quotient_familial` dans `scenario.py`).
- **Valeur centrale** : chiffrage de l'IGF et de l'IGAS (`qf_baisse_10_rendement_igf_2026` pour une baisse de `qf_baisse_10_taux_igf_2026` %, législation 2026, modèle Ines 2024 sur l'ERFS 2022), rapporté à un point de baisse et ramené en euros de 2025 par le PIB nominal.
- **Plage** : les deux baisses votées, chiffrées par le Gouvernement dans l'exposé général des motifs (`qf_baisse_plafond_rendement_2013`, `qf_baisse_plafond_rendement_2014`), divisées par la baisse en % (`baisse_historique`) et portées en euros de 2025 par le PIB nominal (`rendement_transpose`). Elles donnent un rendement par point plus faible : il fixe la borne basse.
- **Effet dans le scénario** : x fois le rendement d'un point, avec le signe opposé (une hausse des plafonds coûte), tenu constant en part du PIB.
- **Ménages types** (`moteur/src/fr_budget/menages/leviers.py`) : plafonds `general` et `celib_enf` d'OpenFisca multipliés par 1 + x. Aucun ménage type n'atteint le plafond : l'effet est nul pour eux. Un couple de cadres au 95e centile avec deux enfants paie 904 € de plus pour une baisse de 25 % (test `test_plafond_quotient_familial`).

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|
| `igf_igas_politiques_familiales_2026_pdf` | 580 M€ pour une baisse de 10 %, 1 892 447 ménages (annexe IV, tableau 15, page 184) | juin 2026 |
| `plf2013_projet_loi_pdf` | baisse de 2 336 à 2 000 € (page 42), rendement 0,5 Md€ (page 19) | PLF 2013 |
| `plf2014_projet_loi_pdf` | baisse de 2 000 à 1 500 € (page 42), 1 Md€ (page 9) | PLF 2014 |
| `ccomptes_famille_fiscalite_2023_pdf` | déplafonnement : 4,9 Md€ (page 51) ; coût du quotient familial par décile, 11 730 M€ (tableau 19, page 73) | revenus 2020 |
| `igf_igas_depenses_socio_fiscales_famille_2021_pdf` | montant du quotient familial avant et après les baisses de 2013 et 2014 (note 24, page 22) | juillet 2021 |

Les annexes « Évaluations préalables des articles » des PLF 2013 et 2014, plus précises, sont sur budget.gouv.fr, inaccessible depuis l'environnement de travail. **À déposer** pour remplacer les montants arrondis.

## 5. Choix à relire

1. **Calage sur l'IGF et l'IGAS.** C'est le seul chiffrage sur la législation actuelle. Il sert au calage, pas à la validation.
2. **Transposition par le PIB.** Les chiffrages de 2013 et 2014 sont portés à aujourd'hui en gardant leur part du PIB nominal, comme pour les autres leviers. La part des familles plafonnées a pu changer en dix ans.
3. **Linéarité.** Une baisse de x % rapporte x fois l'effet d'1 %. Une baisse plus forte touche davantage de foyers : le rendement par point augmente avec l'ampleur, ce que montre l'écart de 2013 (§ 6).
4. **Plafonds concernés.** Les deux plafonds baissés en 2013 et en 2014 (demi-part pour charges de famille et première part du parent isolé). Les plafonds des demi-parts liées à la situation du contribuable (invalidité, anciens combattants) ne bougent pas, comme lors de ces deux baisses.
5. **Calendrier.** Effet en année pleine dès l'année d'entrée.

## 6. Validation

Test : `moteur/tests/validation/test_levier_quotient_familial.py`. Tolérance : ±10 %.

| Référence | Millésime | Référence | Modèle | Écart | Dans la tolérance |
|-----------|-----------|----------:|-------:|------:|-------------------|
| Baisse de 2 336 à 2 000 € (-14,4 %) | PLF 2013 | 0,50 Md€ | 0,58 Md€ | +16,0 % | non |
| Baisse de 2 000 à 1 500 € (-25 %) | PLF 2014 | 1,00 Md€ | 1,02 Md€ | +2,4 % | oui |

Lecture :
- Les deux références sont arrondies (au dixième et au milliard) ; l'arrondi de 1 Md€ peut à lui seul faire ±5 %.
- Montants constatés après coup (IGF-IGAS 2021, note 24) : le quotient familial passe de 12,4 à 12,2 Md€ après la baisse de 2013, puis à 11,6 Md€ après celle de 2014, soit environ 0,2 et 0,6 Md€, bien moins que les prévisions. Ces écarts mêlent l'effet de la mesure et l'évolution des revenus : ils ne sont pas comptés en validation.
- **Confrontation indépendante** (Cour des comptes, 2023) : aucun chiffrage indépendant de la même mesure. Contrôle de vraisemblance : relever les plafonds de 25 % coûte au plus 1,10 Md€ sur les revenus de 2020, sous les 4,9 Md€ d'une suppression du plafond (test `test_hausse_maximale_sous_le_cout_du_deplafonnement`).
- Le levier reste en **bêta** : une référence hors tolérance, pas de confrontation indépendante de la même mesure.

## 7. Limites connues

- Pas de changement de comportement (déclaration, optimisation).
- Les seuils et prestations qui dépendent du nombre de parts ne sont pas touchés : seul le plafond change.
- La réponse non linéaire au-delà de ±25 % n'est pas modélisée (curseur borné).

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-11-05 | Création du levier | 2 nouvelles références de validation : 2014 dans la tolérance (+2,4 %), 2013 hors tolérance (+16,0 %) |
