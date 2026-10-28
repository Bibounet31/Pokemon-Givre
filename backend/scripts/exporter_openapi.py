"""Write the API's OpenAPI schema to ``backend/openapi.json``.

The front-end generates its TypeScript types from this file (``npm run gen:api``),
so the two sides can never disagree on the contract. A test fails when the file
is out of date: after changing a route or a model, run from ``backend/``::

    python -m scripts.exporter_openapi
"""

from __future__ import annotations

import json
from pathlib import Path

from api.main import app

CHEMIN = Path(__file__).resolve().parents[1] / "openapi.json"


def generer() -> str:
    return json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n"


if __name__ == "__main__":
    CHEMIN.write_text(generer(), encoding="utf-8")
    print(f"Wrote {CHEMIN}")
