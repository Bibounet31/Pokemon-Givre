"""FastAPI entry point.

Run from ``backend/``:  ``uvicorn api.main:app --reload``
Interactive docs: http://localhost:8000/docs
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import ORIGINES_CORS
from .routes import ROUTEURS


def create_app() -> FastAPI:
    app = FastAPI(title="Yboost Pokémon API", version="0.2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGINES_CORS,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    for routeur in ROUTEURS:
        app.include_router(routeur)
    return app


app = create_app()
