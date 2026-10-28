"""Request and response bodies of the API (contract v2).

The game state itself (``Partie``, ``PokemonEquipe``…) lives in ``moteur.modeles``;
this module only adds what is specific to HTTP.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field

from moteur.modeles import Direction, EntreeJournal, Evenement, Modele, Partie
from moteur.regles import TAILLE_EQUIPE_MAX


class Erreur(Modele):
    """Body of every 4xx/5xx response."""

    detail: str


# ---------- catalogue ----------


class Calques(Modele):
    """Displayed tile layers, row by row (index = y * largeur + x). 0 = empty tile."""

    sol: list[int]
    decor: list[int]
    toits: list[int] = Field(description="Drawn above the player.")


class ObjetVisible(Modele):
    """An object the front-end draws (NPC, trainer, nurse, chest)."""

    nom: str
    type: str
    x: int
    y: int
    largeur: int
    hauteur: int
    proprietes: dict[str, str | int | float | bool]


class CarteReponse(Modele):
    id: str
    titre: str
    largeur: int
    hauteur: int
    taille_tuile: int
    calques: Calques
    objets: list[ObjetVisible]


# ---------- runs ----------


class NouvellePartie(Modele):
    graine: int | None = Field(None, description="Fixed seed (tests, replays). Random when omitted.")


class ChoixStarter(Modele):
    pokemon_id: int


# ---------- exploration ----------


class Deplacement(Modele):
    direction: Direction


class ReponseDeplacement(Modele):
    partie: Partie
    evenement: Evenement
    dans_les_herbes: bool = False


class ReponseInteraction(Modele):
    partie: Partie
    evenement: Evenement


# ---------- battle ----------


class ActionAttaquer(Modele):
    type: Literal["attack"]
    move_id: str = Field(description="One of the active Pokémon's moves, e.g. 'water-gun'.")


class ActionChanger(Modele):
    type: Literal["switch"]
    index: int = Field(ge=0, lt=TAILLE_EQUIPE_MAX, description="Index in partie.equipe.")


class ActionObjet(Modele):
    type: Literal["item"]
    objet: str = Field(description="Item name from the bag, e.g. 'potion' or 'ether'.")
    cible: int = Field(0, ge=0, lt=TAILLE_EQUIPE_MAX, description="Index in partie.equipe.")


class ActionCapturer(Modele):
    type: Literal["capture"]


class ActionFuir(Modele):
    type: Literal["flee"]


ActionCombat = Annotated[
    ActionAttaquer | ActionChanger | ActionObjet | ActionCapturer | ActionFuir,
    Field(discriminator="type"),
]


class ReponseCombat(Modele):
    partie: Partie
    journal: list[EntreeJournal] = Field(description="What happened during the turn, in order.")
