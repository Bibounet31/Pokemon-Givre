"""Exploration rules: moving on the map and changing maps.

Pure functions: they read and update a :class:`Partie` but know nothing about
HTTP, so they are tested without starting the server.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .cartes import Carte
from .modeles import Direction, Evenement, Partie

PAS: dict[Direction, tuple[int, int]] = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}


@dataclass(frozen=True, slots=True)
class ResultatDeplacement:
    evenement: Evenement
    dans_les_herbes: bool = False


def case_devant(partie: Partie) -> tuple[int, int]:
    """The tile the player is facing (used to talk, open a chest…)."""
    dx, dy = PAS[partie.position.orientation]
    return partie.position.x + dx, partie.position.y + dy


def deplacer(partie: Partie, direction: Direction, cartes: Mapping[str, Carte]) -> ResultatDeplacement:
    """Turn the player towards ``direction`` and move one tile if it is free.

    Walking into a wall is not an error: the player only turns and the event is ``bloque``.
    Stepping on an exit teleports the player to the destination map.
    """
    position = partie.position
    position.orientation = direction
    carte = cartes[position.carte]
    x, y = case_devant(partie)

    if carte.bloquee(x, y):
        return ResultatDeplacement(Evenement(type="bloque"))

    sortie = carte.sortie_en(x, y)
    if sortie is not None:
        destination = sortie.proprietes["vers_carte"]
        position.carte = destination
        position.x = int(sortie.proprietes["vers_x"])
        position.y = int(sortie.proprietes["vers_y"])
        return ResultatDeplacement(Evenement(type="changement_carte", carte=destination))

    position.x, position.y = x, y
    # Wild encounters (TAUX_RENCONTRE, Notion task 61) will turn this into a "rencontre" event.
    return ResultatDeplacement(Evenement(type="deplace"), dans_les_herbes=(x, y) in carte.herbes)
