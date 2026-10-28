"""Game state models, shared by the rules engine and the HTTP API.

These Pydantic models are the single source of truth for the shape of a run.
The API returns them as they are, and the front-end TypeScript types are
generated from the resulting OpenAPI schema (see the README, "API types").
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator

from .regles import NB_ATTAQUES_MAX, NB_COMBATS_TOUR, TAILLE_EQUIPE_MAX


class Mode(StrEnum):
    """Top-level state of a run. Each route only works in one mode (otherwise 409)."""

    choix_starter = "choix_starter"
    exploration = "exploration"
    combat = "combat"
    fin = "fin"


Direction = Literal["up", "down", "left", "right"]


class Modele(BaseModel):
    """Base of every model: fields with a default are always present in responses,
    so the generated TypeScript types mark them as required (no needless ``?``).

    ``validate_assignment``: ``pokemon.pv = -3`` raises instead of corrupting the run.
    Changing a list in place (``partie.equipe.append(...)``) is not checked: reassign it instead.
    """

    model_config = ConfigDict(json_schema_serialization_defaults_required=True, validate_assignment=True)


# ---------- reference data (never changes during a run) ----------


class Statistiques(Modele):
    """The six battle stats. ``pv`` is the maximum HP."""

    pv: int = Field(ge=1)
    attaque: int = Field(ge=1)
    defense: int = Field(ge=1)
    attaque_spe: int = Field(ge=1)
    defense_spe: int = Field(ge=1)
    vitesse: int = Field(ge=1)


class AttaqueDeBase(Modele):
    """A move a species can learn, with its maximum PP."""

    id: str = Field(description="PokéAPI move name, e.g. 'water-gun'.")
    pp: int = Field(ge=1)


class Espece(Modele):
    """A Pokémon species as imported from PokéAPI."""

    id: int = Field(description="National Pokédex number.")
    nom: str = Field(description="PokéAPI (English) name, e.g. 'charmander'.")
    nom_fr: str
    types: list[str] = Field(min_length=1, max_length=2)
    stats_base: Statistiques
    attaques: list[AttaqueDeBase] = Field(min_length=1, max_length=NB_ATTAQUES_MAX)


class Starter(Espece):
    """A species offered at the start of the game, with its starting level."""

    niveau: int = Field(ge=1, le=100)


# ---------- state of a run (changes while playing) ----------


class Position(Modele):
    carte: str
    x: int
    y: int
    orientation: Direction = "down"


class AttaqueConnue(Modele):
    """A move known by a team member, with its remaining PP."""

    id: str
    pp: int = Field(ge=0)
    pp_max: int = Field(ge=1)

    @model_validator(mode="after")
    def _pp_au_plus_pp_max(self) -> AttaqueConnue:
        if self.pp > self.pp_max:
            raise ValueError(f"pp ({self.pp}) > pp_max ({self.pp_max})")
        return self


class PokemonEquipe(Modele):
    """A Pokémon of a team (the player's or an opponent's)."""

    id: int
    nom: str
    nom_fr: str
    types: list[str]
    niveau: int = Field(ge=1, le=100)
    stats: Statistiques = Field(description="Stats at the current level; stats.pv is the maximum HP.")
    pv: int = Field(ge=0, description="Current HP, between 0 and stats.pv.")
    attaques: list[AttaqueConnue] = Field(min_length=1, max_length=NB_ATTAQUES_MAX)

    @model_validator(mode="after")
    def _pv_au_plus_pv_max(self) -> PokemonEquipe:
        if self.pv > self.stats.pv:
            raise ValueError(f"pv ({self.pv}) > stats.pv ({self.stats.pv})")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ko(self) -> bool:
        """A knocked-out Pokémon can neither attack nor be sent into battle."""
        return self.pv == 0


class EntreeJournal(Modele):
    """One line of the battle log shown to the player."""

    texte: str


class CombatEnCours(Modele):
    """The battle being fought, if the run is in ``combat`` mode."""

    genre: Literal["sauvage", "dresseur", "tour"]
    adversaires: list[PokemonEquipe] = Field(min_length=1, max_length=TAILLE_EQUIPE_MAX)
    actif: int = Field(0, ge=0, description="Index of the player's Pokémon in battle (in partie.equipe).")
    actif_adverse: int = Field(0, ge=0, description="Index of the opponent's Pokémon in battle.")
    dresseur: str | None = Field(None, description="Trainer key 'carte/nom', None for a wild Pokémon.")
    numero_tour: int = Field(1, ge=1)

    @model_validator(mode="after")
    def _adversaire_actif_existe(self) -> CombatEnCours:
        if self.actif_adverse >= len(self.adversaires):
            raise ValueError(f"actif_adverse ({self.actif_adverse}) is outside the opposing team")
        return self


class ProgressionTour(Modele):
    """Progress of the current Battle Tower attempt."""

    victoires: int = Field(0, ge=0, le=NB_COMBATS_TOUR)


TypeEvenement = Literal[
    "deplace",
    "bloque",
    "changement_carte",
    "rencontre",
    "dialogue",
    "objet_obtenu",
    "coffre_vide",
    "soin",
    "combat",
    "rien",
]


class Evenement(Modele):
    """What happened during an action. A game failure (wall, empty chest) is an event, not an HTTP error."""

    type: TypeEvenement
    carte: str | None = Field(None, description="Destination map of a 'changement_carte'.")
    texte: str | None = Field(None, description="Text to show in the dialogue box.")
    objet: str | None = Field(None, description="Item received with 'objet_obtenu'.")


class Partie(Modele):
    """A run, kept in memory by the server."""

    id: str
    mode: Mode
    graine: int = Field(description="Seed of every random draw of the run, so it can be replayed.")
    tirages: int = Field(0, ge=0, description="Actions that drew random numbers so far (see moteur.aleatoire).")
    position: Position
    equipe: list[PokemonEquipe] = Field(default_factory=list, max_length=TAILLE_EQUIPE_MAX)
    sac: dict[str, int] = Field(default_factory=dict, description="Item name -> quantity.")
    coffres_ouverts: set[str] = Field(default_factory=set, description="Keys 'carte/nom' of opened chests.")
    dresseurs_battus: set[str] = Field(default_factory=set, description="Keys 'carte/nom' of beaten trainers.")
    dernier_soin: Position | None = Field(None, description="Where a defeat sends the player back.")
    combat: CombatEnCours | None = None
    tour: ProgressionTour | None = Field(None, description="None when no Tower attempt is in progress.")

    @model_validator(mode="after")
    def _pokemon_actif_existe(self) -> Partie:
        if self.combat is not None and self.combat.actif >= len(self.equipe):
            raise ValueError(f"combat.actif ({self.combat.actif}) is outside the team")
        return self
