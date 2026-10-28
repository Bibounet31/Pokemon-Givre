"""Modèles Pydantic : ce que l'API reçoit et renvoie (contrat d'API v1)."""
from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Mode(str, Enum):
    choix_starter = "choix_starter"
    exploration = "exploration"
    combat = "combat"
    fin = "fin"


Direction = Literal["up", "down", "left", "right"]


class Starter(BaseModel):
    id: int
    nom: str
    nom_fr: str
    types: list[str]
    niveau: int


class PokemonEquipe(BaseModel):
    id: int
    nom: str
    nom_fr: str
    niveau: int


class Position(BaseModel):
    carte: str
    x: int
    y: int
    orientation: Direction = "down"


class Partie(BaseModel):
    id: str
    mode: Mode
    graine: int
    position: Position
    equipe: list[PokemonEquipe] = Field(default_factory=list)


class NouvellePartie(BaseModel):
    graine: int | None = None


class ChoixStarter(BaseModel):
    pokemon_id: int


class Deplacement(BaseModel):
    direction: Direction


class Evenement(BaseModel):
    """Ce qui s'est passé pendant l'action. Un mur n'est pas une erreur HTTP : c'est un événement."""
    type: Literal["deplace", "bloque", "changement_carte"]
    carte: str | None = None


class ReponseDeplacement(BaseModel):
    partie: Partie
    evenement: Evenement
    dans_les_herbes: bool = False


class ObjetVisible(BaseModel):
    nom: str
    type: str
    x: int
    y: int
    largeur: int
    hauteur: int
    proprietes: dict[str, Any]


class CarteReponse(BaseModel):
    id: str
    titre: str
    largeur: int
    hauteur: int
    taille_tuile: int
    calques: dict[str, list[int]]
    objets: list[ObjetVisible]
