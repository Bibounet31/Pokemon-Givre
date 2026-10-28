"""Game design constants, decided by the team (Notion design doc, section 14).

Change a rule here, never as a magic number in the code.
"""

CARTE_DE_DEPART = "village"

TAILLE_EQUIPE_MAX = 3
"""Maximum number of Pokémon in the player's team (3 for now)."""

NB_ATTAQUES_MAX = 4
"""A Pokémon knows at most 4 moves."""

TAUX_RENCONTRE = 0.11
"""Chance of a wild encounter on each step in tall grass, drawn with the run's seed."""

NB_COMBATS_TOUR = 5
"""Hard battles to win in the Battle Tower; winning the last one ends the game (mode ``fin``)."""

OBJETS_PP = frozenset({"ether", "max-ether"})
"""Items that restore PP (Huile, Huile Max). Healing at a Pokémon Center restores HP only."""
