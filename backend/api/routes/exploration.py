"""Exploration actions: move and interact with the tile in front of the player."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from moteur import donnees
from moteur.exploration import deplacer
from moteur.interaction import InteractionNonDisponible
from moteur.interaction import interagir as interagir_devant

from ..dependances import ERREURS_ACTION, PartieEnExploration
from ..schemas import Deplacement, Erreur, ReponseDeplacement, ReponseInteraction

router = APIRouter(prefix="/runs/{run_id}", tags=["exploration"])


@router.post("/move", responses=ERREURS_ACTION)
async def deplacer_joueur(partie: PartieEnExploration, deplacement: Deplacement) -> ReponseDeplacement:
    resultat = deplacer(partie, deplacement.direction, donnees.cartes())
    return ReponseDeplacement(partie=partie, evenement=resultat.evenement, dans_les_herbes=resultat.dans_les_herbes)


@router.post(
    "/interact",
    responses={**ERREURS_ACTION, 501: {"model": Erreur, "description": "Pas encore implémenté"}},
)
async def interagir(partie: PartieEnExploration) -> ReponseInteraction:
    """Talk to an NPC, open a chest, heal or challenge a trainer on the tile in front of the player.

    Contract only: implemented by Notion task 64.
    """
    try:
        evenement = interagir_devant(partie, donnees.cartes())
    except InteractionNonDisponible as erreur:
        raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, detail=str(erreur)) from erreur
    return ReponseInteraction(partie=partie, evenement=evenement)
