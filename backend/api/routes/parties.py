"""Creating a run, reading it and choosing the starter."""

from __future__ import annotations

import random
import uuid

from fastapi import APIRouter, HTTPException, status

from moteur import donnees
from moteur.modeles import Mode, Partie, Position
from moteur.pokemon import creer_pokemon
from moteur.regles import CARTE_DE_DEPART

from ..dependances import ERREUR_404, ERREURS_ACTION, DepotDep, PartieDep, PartieEnChoixStarter
from ..schemas import ChoixStarter, Erreur, NouvellePartie

router = APIRouter(prefix="/runs", tags=["parties"])


def _position_de_depart() -> Position:
    depart = donnees.cartes()[CARTE_DE_DEPART].objet_de_type("depart")
    if depart is None:
        raise RuntimeError(f"Map {CARTE_DE_DEPART} has no 'depart' object")
    return Position(carte=CARTE_DE_DEPART, x=depart.x, y=depart.y)


@router.post("", status_code=status.HTTP_201_CREATED)
def creer_partie(depot: DepotDep, demande: NouvellePartie | None = None) -> Partie:
    graine = demande.graine if demande and demande.graine is not None else random.randrange(2**31)
    partie = Partie(id=uuid.uuid4().hex, mode=Mode.choix_starter, graine=graine, position=_position_de_depart())
    return depot.ajouter(partie)


@router.get("/{run_id}", responses=ERREUR_404)
def lire_partie(partie: PartieDep) -> Partie:
    return partie


@router.post(
    "/{run_id}/starter",
    responses={**ERREURS_ACTION, 422: {"model": Erreur, "description": "Pokémon qui n'est pas un starter"}},
)
def choisir_starter(partie: PartieEnChoixStarter, choix: ChoixStarter) -> Partie:
    starter = donnees.starters().get(choix.pokemon_id)
    if starter is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Ce Pokémon ne fait pas partie des starters")
    partie.equipe = [creer_pokemon(starter, starter.niveau)]
    partie.mode = Mode.exploration
    return partie
