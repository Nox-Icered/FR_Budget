# API

API FastAPI sans état (lot 1.4 du plan). Elle ne stocke rien et ne journalise aucune donnée saisie : elle se lance sans journal d'accès, et un test vérifie qu'aucun paramètre de requête n'apparaît dans les journaux du serveur.

## Lancer

    cd api
    uv sync
    uv run uvicorn fr_budget_api.app:application --no-access-log

Documentation interactive : `/docs`.

## Points d'entrée

| Chemin | Contenu |
|---|---|
| `GET /sante` | État du service |
| `GET /version` | Version du moteur, empreintes SHA-256 des registres et des données traitées (pour qu'un scénario partagé reproduise le même résultat) |
| `GET /registres/{nom}` | `sources`, `jeux-de-donnees`, `hypotheses`, `leviers`, `chiffrages` |
| `GET /comptes-apu?sous_secteur=S13&indicateur=dette_maastricht` | Série annuelle des comptes des APU (INSEE), en Md€, avec sa source |
| `GET /depenses-par-fonction?annee=2024&sous_secteur=S13` | Dépenses par fonction COFOG (Eurostat), en Md€, avec sa source |

Sous-secteurs, indicateurs et codes : voir `docs/fiches/comptes_apu.md`.

À venir : `GET /baseline` (lot 1.3) et `POST /scenario`.
