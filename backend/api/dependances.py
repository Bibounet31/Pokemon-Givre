"""Reusable FastAPI dependencies: load a run (404) and check its mode (409).

Every dependency and route that reads or changes a run is ``async def`` and never awaits:
FastAPI then runs it on the event loop instead of a worker thread, so one request is handled
from the 409 check to the response before the next one starts (no lock needed).
A ``def`` route would run in a thread pool, and two clicks could play the same turn twice.

Use the annotated types in a route signature instead of repeating the checks::

    @router.post("/runs/{run_id}/move")
    async def deplacer(partie: PartieEnExploration, ...): ...
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status

from moteur.modeles import Mode, Partie

from .depot import DepotParties, get_depot
from .schemas import Erreur

DepotDep = Annotated[DepotParties, Depends(get_depot)]


async def partie_existante(run_id: str, depot: DepotDep) -> Partie:
    partie = depot.lire(run_id)
    if partie is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Partie introuvable")
    return partie


PartieDep = Annotated[Partie, Depends(partie_existante)]


def partie_en_mode(mode: Mode) -> Callable[[Partie], Awaitable[Partie]]:
    """Dependency factory: the run must be in ``mode``, otherwise 409 and nothing changes."""

    async def verifier(partie: PartieDep) -> Partie:
        if partie.mode != mode:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail=f"Action impossible en mode {partie.mode} (attendu : {mode})",
            )
        return partie

    return verifier


PartieEnChoixStarter = Annotated[Partie, Depends(partie_en_mode(Mode.choix_starter))]
PartieEnExploration = Annotated[Partie, Depends(partie_en_mode(Mode.exploration))]
PartieEnCombat = Annotated[Partie, Depends(partie_en_mode(Mode.combat))]

# Error responses documented in OpenAPI (and therefore typed on the front-end).
ERREUR_404: dict[int | str, dict[str, Any]] = {404: {"model": Erreur, "description": "Partie inconnue"}}
ERREURS_ACTION: dict[int | str, dict[str, Any]] = {
    **ERREUR_404,
    409: {"model": Erreur, "description": "Action impossible dans le mode actuel"},
}
