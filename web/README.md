# Site

Site statique Next.js (TypeScript), mobile d'abord. Tous les textes affichés sont dans `messages/fr.json`, pour préparer la version anglaise ; un test vérifie qu'aucun n'emploie un terme du registre des libellés interdits (`moteur/tests/unitaires/test_neutralite_site.py`).

Les pages sont générées à partir des fichiers de `donnees/`, produits par l'export de l'API (mêmes fonctions que les points d'entrée). Aucun chiffre n'est calculé dans le site : ratios au PIB et libellés viennent du moteur.

## Construire

    cd web
    pnpm install
    pnpm donnees   # export de l'API vers web/donnees/ (nécessite uv)
    pnpm test
    pnpm build     # site statique dans web/out/

## Pages

| Chemin | Contenu |
|---|---|
| `/` | Comptes des APU de la dernière année par sous-secteur (Md€ et % du PIB), dépenses par fonction |
| `/sources/` | Registre des sources |
| `/hypotheses/` | Registre des hypothèses, avec plages et justification |
| `/validation/` | Statut des leviers et références saisies pour la validation |
