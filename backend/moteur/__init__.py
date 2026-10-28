"""Game rules engine: pure Python, no FastAPI import.

- ``regles``: design constants (team size, encounter rate…)
- ``modeles``: Pydantic models of the game state
- ``cartes``: Tiled map loading
- ``donnees``: reference data cached in memory
- ``pokemon``: stats and creation of team Pokémon
- ``types``: type effectiveness multiplier
- ``exploration``: moving on the map
- ``aleatoire``: reproducible random draws from the run's seed
"""
