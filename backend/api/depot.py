"""In-memory storage of the runs.

Restarting the server erases every run (wanted for this project). It only
works with a single Uvicorn process: two workers would not share the runs.
"""

from __future__ import annotations

from moteur.modeles import Partie


class DepotParties:
    def __init__(self) -> None:
        self._parties: dict[str, Partie] = {}

    def ajouter(self, partie: Partie) -> Partie:
        self._parties[partie.id] = partie
        return partie

    def lire(self, run_id: str) -> Partie | None:
        return self._parties.get(run_id)

    def vider(self) -> None:
        """Remove every run (used by the tests)."""
        self._parties.clear()


depot = DepotParties()


def get_depot() -> DepotParties:
    """FastAPI dependency; tests can override it with ``app.dependency_overrides``."""
    return depot
