# API publique, version 1

L'API publique donne aux programmes (outils de journalistes, de chercheurs ou d'autres sites) les mêmes calculs que le simulateur. Elle est servie sous `/v1` par l'application FastAPI du dépôt (`api/`). Sa documentation interactive est sur `/v1/docs`, et sa description OpenAPI est versionnée dans `api/openapi-v1.json`.

**État** : prête, pas encore en ligne. L'hébergement reste à choisir par le responsable du projet ; voir le § 6.

## 1. Règles

- **Sans état.** Rien n'est stocké ni journalisé, pas même le journal d'accès du serveur. Aucun message d'erreur ne reprend une valeur envoyée.
- **Fourchettes.** Chaque résultat chiffré est donné en valeur basse, centrale et haute.
- **Traçabilité.** Chaque résultat porte la version du modèle et des données (`version`), ses sources et ses hypothèses (identifiants des registres, lisibles sur `/v1/registres/{nom}`).
- **Statut.** Les leviers « beta » ne sont pas validés. Les écarts aux références officielles, y compris hors tolérance, sont sur `/v1/validation`.
- **Neutralité.** L'API calcule ce que l'appelant demande. Elle ne recommande ni ne classe aucune mesure.
- **Licences.** Code sous AGPL-3.0-or-later, données produites sous Licence Ouverte 2.0. Chaque source garde sa licence, listée dans `/v1/registres/sources`.

## 2. Routes

| Méthode | Route | Rôle |
|---|---|---|
| GET | `/v1/` | présentation, version, licences, liste des routes |
| GET | `/v1/version` | version de l'API, du moteur et des données |
| GET | `/v1/leviers` | leviers réglables : libellé, unité, bornes, statut, rendement d'une unité, sources |
| GET | `/v1/leviers/{levier}` | un levier |
| GET | `/v1/interactions` | termes croisés chiffrés et interactions connues non chiffrées |
| POST | `/v1/scenario` | dette et solde primaire de 2025 à 2046 avec les mesures |
| POST | `/v1/deciles` | variation du revenu disponible par dixième de niveau de vie |
| POST | `/v1/objectif` | valeur d'un levier, pris seul, qui atteint une dette ou un solde visé |
| GET | `/v1/baseline` | trajectoire sans mesure |
| GET | `/v1/validation` | écarts du modèle aux références |
| GET | `/v1/registres/{nom}` | registres : `sources`, `datasets`, `hypotheses`, `leviers`, `chiffrages` |
| GET | `/v1/depenses-fiscales` | dépenses fiscales réglables une à une (`depense_fiscale_<code>`) |
| GET | `/v1/credits-missions` | missions de l'État réglables une à une (`credits_mission_<identifiant>`) |

## 3. Exemple

Hausse d'un point du taux normal de TVA, en vigueur en 2027 :

```
curl -X POST https://<adresse>/v1/scenario \
  -H "Content-Type: application/json" \
  -d '{"mesures": [{"levier": "tva_taux_normal", "valeur": 1, "annee": 2027}]}'
```

La réponse contient, pour chaque année :
- la dette et le solde primaire en % du PIB, en fourchette ;
- l'écart à la trajectoire sans mesure ;
- le statut de chaque levier, les sources, les hypothèses et la version.

## 4. Erreurs

Toutes les erreurs ont la même forme :

```
{"erreur": {"code": "mesure_invalide", "message": "…", "champs": []}}
```

| Code | Statut HTTP | Cause |
|---|---|---|
| `requete_invalide` | 422 | requête mal formée ou hors des bornes ; `champs` nomme les champs fautifs, sans leur valeur |
| `mesure_invalide` | 422 | levier inconnu ou interne, valeur hors des bornes, combinaison refusée (double compte) |
| `objectif_invalide` | 422 | levier inconnu ou année de l'objectif avant l'entrée en vigueur |
| `levier_inconnu`, `registre_inconnu` | 404 | identifiant inconnu |
| `requete_trop_grande` | 413 | corps de plus de 32 768 octets |

## 5. Garde-fous

- Au plus 40 mesures par requête, et un corps d'au plus 32 768 octets.
- Années d'entrée en vigueur de 2027 à 2046.
- Appels permis depuis tout domaine (CORS ouvert, sans cookies).
- **À la charge de l'hébergeur** : le plafond de requêtes par minute et par adresse. Le calcul d'objectif refait jusqu'à quelques centaines de scénarios ; il est le plus coûteux.

## 6. Mise en ligne (à décider)

Lancement : `uv run python -m fr_budget_api.serveur`, depuis `api/`.

L'hébergement doit :
- faire tourner Python 3.12 en continu ;
- n'enregistrer ni le contenu des requêtes, ni leurs paramètres ;
- plafonner le nombre de requêtes.

Deux réglages ensuite :
- `FR_BUDGET_ORIGINES`, l'adresse du site, pour la route `/mon-menage` ;
- `NEXT_PUBLIC_API_URL`, l'adresse de l'API, à la construction du site. La page « API » affiche alors l'adresse publique.

## 7. Stabilité du contrat

Une route ou un champ de `/v1` n'est ni retiré ni changé de sens. Des champs peuvent être ajoutés. Un changement incompatible passe par `/v2`. Le test `api/tests/test_api_publique.py` vérifie que `api/openapi-v1.json` reste à jour. Toute modification du contrat se voit donc dans la revue de code ; on régénère le fichier avec `uv run python -m fr_budget_api.openapi`.
