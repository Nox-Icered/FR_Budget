---
module: scenario
statut: non_publie
mise_a_jour: 2026-10-09
---

# Fiche : scénario (leviers, solde et dette)

Lot 2.1 du plan (phase 2). Relie un levier à la trajectoire : effet sur le solde primaire, puis sur la dette, comparé à la baseline.

## 1. Question posée

Si l'on applique une mesure à partir d'une année donnée, de combien changent le solde primaire et la dette publique, en points de PIB, chaque année jusqu'en 2046 ?

## 2. Ce que l'utilisateur règle

- Le levier et sa valeur. Premier levier : hausse ou baisse de x points du taux normal de TVA, de -10 à +10 points (la baisse s'arrête au taux intermédiaire de 10 % ; la hausse admise est de même ampleur).
- L'année d'entrée en vigueur, de 2027 (premier budget non voté, PLF 2027) à 2046.

## 3. Méthode

1. **Effet sur le solde primaire** : x fois le rendement d'un point du taux normal de TVA en 2025, net de la TVA payée par les administrations publiques (point net, 7,67 Md€ selon le modèle ; décision du mainteneur du 9 octobre 2026, option (a)), rapporté au PIB de 2025 (2 991,1 Md€, INSEE). Soit 0,256 point de PIB par point de TVA, tenu constant en points de PIB.
2. **Dette** : même formule et mêmes entrées que la baseline (taux apparent, croissance nominale, ajustement stock-flux), avec le solde primaire augmenté de l'effet. Une dette plus faible porte moins d'intérêts : cet effet est inclus.
3. **Fourchettes** : l'écart à la baseline varie avec la plage du rendement du levier ; le niveau varie avec la plage du levier et avec celle de la baseline, une hypothèse à la fois.
4. **Linéarité** : l'écart est proportionnel à x. Le site statique publie la réponse à +1 point pour chaque année d'entrée et la multiplie par x ; l'API `POST /scenario` calcule directement.

## 4. Données

Celles de la baseline (`docs/fiches/baseline.md`) et du levier TVA (`docs/fiches/tva.md`) ; PIB 2025 : `insee_comptes_nationaux_2025`.

## 5. Hypothèses et choix

- `scenario_rendement_constant_pib` : rendement constant en points de PIB (plage nulle, voir limites).
- Aucun effet de comportement des consommateurs (élasticités prévues en V3).
- Aucun effet sur la croissance : le multiplicateur budgétaire viendra comme un interrupteur désactivé par défaut.
- Plusieurs mesures s'additionnent, sans interaction.

## 6. Validation

Tests unitaires `moteur/tests/unitaires/test_scenario.py` : zéro point redonne la baseline, proportionnalité, absence d'effet avant l'entrée en vigueur, dette recalculée à la main, réponse unitaire. La validation du rendement est celle du levier TVA (page Validation : point net 2025 au taux normal à +2,2 % de la DG Trésor).

## 7. Limites

- **La fourchette du levier TVA est quasi nulle** : elle ne reprend que la plage de l'hypothèse de répartition des produits mixtes et ne couvre pas l'erreur du modèle (voir `docs/validation/levier_tva.md`). Le levier reste en bêta.
- Rendement proportionnel au PIB, sans élasticité sourcée.
- Pas d'effet de la mesure sur les prix, donc ni sur le déflateur ni sur les dépenses indexées.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
| 2026-10-09 | Scénario et levier « taux normal de TVA » | 10 tests unitaires créés ; baseline inchangée (14 tests réussis) |
| 2026-10-09 | Bornes du levier, réponse linéaire pour le site, `POST /scenario`, page Simulateur | 2 tests unitaires du moteur, 7 tests de l'API et 2 tests du site créés |
