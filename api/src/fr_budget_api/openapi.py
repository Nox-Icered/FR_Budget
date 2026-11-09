"""Écrit la description OpenAPI de l'API publique (``api/openapi-v1.json``), versionnée dans le
dépôt : toute modification du contrat se voit dans la revue de code.

Usage (depuis ``api/``) : ``uv run python -m fr_budget_api.openapi``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import fr_budget_api.app  # noqa: F401 (charge l'application avant sa sous-application)
from fr_budget_api.publique import creer_api_publique

FICHIER = Path(__file__).parents[2] / "openapi-v1.json"


def description() -> dict[str, Any]:
    schema: dict[str, Any] = creer_api_publique().openapi()
    schema["servers"] = [{"url": "/v1"}]
    return schema


def texte() -> str:
    return json.dumps(description(), ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def main() -> None:
    FICHIER.write_text(texte(), encoding="utf-8")


if __name__ == "__main__":
    main()
