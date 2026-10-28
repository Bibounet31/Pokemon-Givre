"""Battle actions: attack, switch, item, capture or flee."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from ..dependances import ERREURS_ACTION, PartieEnCombat
from ..schemas import ActionCombat, Erreur, ReponseCombat

router = APIRouter(prefix="/runs/{run_id}/battle", tags=["combat"])


@router.post(
    "/actions",
    responses={**ERREURS_ACTION, 501: {"model": Erreur, "description": "Pas encore implémenté"}},
)
async def agir(partie: PartieEnCombat, action: ActionCombat) -> ReponseCombat:
    """Play one battle turn: the server resolves both sides and returns the log.

    Contract only: implemented by Notion tasks 20, 22, 24, 25, 28, 29 and 67.
    """
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail="Combat pas encore disponible (tâche 20)")
