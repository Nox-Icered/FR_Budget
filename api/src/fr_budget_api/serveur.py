"""Lancement de l'API sans journal d'accès (règle 5 de CLAUDE.md).

Usage (depuis api/) : ``uv run python -m fr_budget_api.serveur``
"""

from __future__ import annotations

import uvicorn

from fr_budget_api.app import application

PORT_PAR_DEFAUT = 8000


def main() -> None:
    uvicorn.run(application, port=PORT_PAR_DEFAUT, access_log=False)


if __name__ == "__main__":
    main()
