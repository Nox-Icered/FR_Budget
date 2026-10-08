# API

API FastAPI sans état (lot 1.4 du plan). Elle ne stocke rien et ne journalise aucune donnée saisie : l'application désactive elle-même le journal d'accès d'uvicorn, et des tests vérifient qu'aucun paramètre de requête n'apparaît dans les journaux du serveur.

## Lancer

    cd api
    uv sync
    uv run python -m fr_budget_api.serveur

Documentation interactive : `/docs`.

## Points d'entrée

| Chemin | Contenu |
|---|---|
| `GET /sante` | État du service |
| `GET /version` | Empreintes SHA-256 du code du moteur, des registres et des données traitées (pour qu'un scénario partagé reproduise le même résultat) |
| `GET /registres/{nom}` | `sources`, `jeux-de-donnees`, `hypotheses`, `leviers`, `chiffrages` |
| `GET /comptes-apu?sous_secteur=S13&indicateur=dette_maastricht` | Série annuelle des comptes des APU (INSEE), en Md€, avec sa source |
| `GET /depenses-par-fonction?annee=2024&sous_secteur=S13` | Dépenses par fonction COFOG (Eurostat), en Md€, avec sa source |
| `GET /validation` | Pour chaque référence de validation : valeur du modèle, référence, écart relatif, tolérance, résultat (`fr_budget.validation`) |

Sous-secteurs, indicateurs et codes : voir `docs/fiches/comptes_apu.md`.

À venir : `GET /baseline` (lot 1.3) et `POST /scenario`.
