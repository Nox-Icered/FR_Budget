---
# En-tête lu par la vérification des registres : l'identifiant doit exister dans
# registres/leviers.yaml (levier) ou désigner un module documenté (module).
levier: identifiant_du_registre
statut: non_publie
mise_a_jour: AAAA-MM-JJ
---

# Fiche : <libellé neutre du levier>

Modèle de fiche. Une fiche se lit sans ouvrir le code. Chaque chiffre renvoie à une ligne de registre (`registres/`) ; aucun chiffre n'est écrit en dur dans la fiche.

## 1. Question posée

Ce que la fiche permet de chiffrer, en une ou deux phrases, avec un exemple de réglage neutre (« hausse de 1 point du taux normal »).

## 2. Ce que l'utilisateur règle

| Paramètre | Valeur actuelle | Plage proposée sur le site | Source de la valeur actuelle |
|-----------|-----------------|----------------------------|------------------------------|
| | renvoi au registre | | identifiant de source |

## 3. Méthode de calcul

- Moteur : OpenFisca, agrégé ou module structurel.
- Formule, en clair puis en notation.
- Fonctions du code qui la mettent en œuvre (`moteur/src/fr_budget/…`), chacune testée.
- Année de référence, montée en charge éventuelle (effet la première année, puis en année pleine).

## 4. Données

| Jeu de données (`registres/datasets.yaml`) | Ce qu'il apporte | Millésime |
|--------------------------------------------|------------------|-----------|

## 5. Hypothèses

| Hypothèse (`registres/hypotheses.yaml`) | Valeur centrale | Plage | Effet sur le résultat |
|-----------------------------------------|-----------------|-------|-----------------------|

Comment les valeurs basse, centrale et haute du résultat sont tirées de ces plages.

## 6. Validation

- Références officielles (`registres/references/chiffrages.yaml`) : document, millésime, localisation.
- Tolérance : ±10 % sur le rendement à 1 an (règle de publication, `CLAUDE.md`).
- Source indépendante (IPP, OFCE, Cour des comptes, Commission européenne) et écart publié.
- Test automatisé : `moteur/tests/validation/…`.

| Référence | Millésime | Valeur de référence | Valeur du modèle | Écart | Dans la tolérance |
|-----------|-----------|---------------------|------------------|-------|-------------------|

## 7. Limites connues

Ce que le calcul ne prend pas en compte (comportements, effets de prix, interactions avec d'autres leviers), et l'ordre de grandeur de ce que cela peut changer quand il est connu et sourcé.

## 8. Journal

| Date | Changement | Tests qui ont bougé |
|------|------------|---------------------|
