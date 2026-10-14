# Simulateur public du budget des administrations publiques françaises

Projet open source, en construction : un site où chacun choisit une réforme et voit son effet chiffré sur le budget des administrations publiques, la dette de N à N+20, des ménages types et les entreprises. Chaque chiffre renvoie à sa source, à ses hypothèses et à son calcul.

Ce n'est pas une prévision officielle. Le site ne classe pas les réformes et n'en recommande aucune.

## État

Phase 0 (cadrage). Aucun levier n'est encore validé. Voir le [plan](docs/plan.md) et la [spécification](docs/specification.md).

## Organisation du dépôt

| Dossier | Contenu |
|---------|---------|
| `docs/` | Spécification, plan, méthodologie, fiches des leviers et modules |
| `registres/` | Registres des sources, données, hypothèses, leviers et chiffrages de référence |
| `data/raw/` | Fichiers sources tels que téléchargés |
| `data/processed/` | Tables produites par les scripts de `pipelines/` |
| `pipelines/` | Scripts d'extraction et de transformation rejouables |
| `moteur/` | Moteur de calcul en Python (paquet `fr_budget`) et ses tests |
| `api/` | API FastAPI sans état (phase 1) |
| `web/` | Site Next.js (phase 1) |
| `outils/` | Contrôles du dépôt |

## Développer

Prérequis : [uv](https://docs.astral.sh/uv/).

```sh
cd moteur
uv sync
uv run ruff check && uv run ruff format --check
uv run mypy
uv run pytest
```

Contrôles avant commit : `uv tool install pre-commit && pre-commit install`.

## Licences

- Code : [AGPL-3.0](LICENSE), comme OpenFisca-France utilisé par le moteur.
- Registres et données produites par le projet : [Licence Ouverte 2.0](LICENCE-DONNEES.md), sauf les tables dérivées des données de l'Urssaf, sous [ODbL 1.0](LICENCE-ODBL.txt) comme leurs jeux d'origine (liste dans `LICENCE-DONNEES.md`). Chaque source garde sa licence d'origine, indiquée dans le registre.
