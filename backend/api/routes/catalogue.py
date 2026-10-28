"""Read-only reference data: starters and maps."""

from __future__ import annotations

from functools import cache

from fastapi import APIRouter, HTTPException, status

from moteur import donnees
from moteur.cartes import TAILLE_TUILE
from moteur.modeles import Starter

from ..schemas import Calques, CarteReponse, Erreur, ObjetVisible

router = APIRouter(tags=["catalogue"])

# Objects the front-end draws; exits and the spawn point stay server-side.
TYPES_VISIBLES = frozenset({"pnj", "dresseur", "soin", "tour_accueil", "tour_adversaire", "coffre"})


@router.get("/starters")
def lister_starters() -> list[Starter]:
    return list(donnees.starters().values())


@cache
def _carte_reponse(map_id: str) -> CarteReponse | None:
    """Maps never change while the server runs, so each response is built once."""
    carte = donnees.cartes().get(map_id)
    if carte is None:
        return None
    return CarteReponse(
        id=carte.id,
        titre=carte.titre,
        largeur=carte.largeur,
        hauteur=carte.hauteur,
        taille_tuile=TAILLE_TUILE,
        calques=Calques(**carte.calques),
        objets=[
            ObjetVisible(
                nom=o.nom, type=o.type, x=o.x, y=o.y, largeur=o.largeur, hauteur=o.hauteur, proprietes=o.proprietes
            )
            for o in carte.objets
            if o.type in TYPES_VISIBLES
        ],
    )


@router.get("/maps/{map_id}", responses={404: {"model": Erreur, "description": "Carte inconnue"}})
def lire_carte(map_id: str) -> CarteReponse:
    reponse = _carte_reponse(map_id)
    if reponse is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Carte introuvable")
    return reponse
