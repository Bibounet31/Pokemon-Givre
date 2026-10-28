"""Reference data (maps, starters…), read from disk once and cached.

PokéAPI is never called while playing: its data is imported once into
``backend/data/`` by a script (Notion task 10).
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

from pydantic import TypeAdapter

from .cartes import Carte, charger_cartes
from .modeles import Starter

DOSSIER_DONNEES = Path(__file__).resolve().parents[1] / "data"


@cache
def cartes() -> dict[str, Carte]:
    """Every map, keyed by id (``village``, ``route1``…)."""
    return charger_cartes()


@cache
def starters() -> dict[int, Starter]:
    """The starters offered on a new run, keyed by Pokédex number.

    Provisional data until the PokéAPI import (task 10) provides a full Pokédex.
    """
    brut = (DOSSIER_DONNEES / "starters.json").read_bytes()
    return {s.id: s for s in TypeAdapter(list[Starter]).validate_json(brut)}
