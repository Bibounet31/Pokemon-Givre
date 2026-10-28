"""Invariants of the game state, enforced by the models even when the engine changes a run."""

import pytest
from pydantic import ValidationError

from moteur import donnees
from moteur.modeles import CombatEnCours, Partie, Position
from moteur.pokemon import creer_pokemon


def _partie(graine: int = 1) -> Partie:
    return Partie(id="t", mode="exploration", graine=graine, position=Position(carte="village", x=0, y=0))


def _pokemon():
    return creer_pokemon(donnees.starters()[4], 5)


# ---------- HP and PP ----------


def test_pv_negatifs_refuses():
    pokemon = _pokemon()
    with pytest.raises(ValidationError):
        pokemon.pv = -3


def test_pv_au_dessus_du_max_refuses():
    pokemon = _pokemon()
    with pytest.raises(ValidationError):
        pokemon.pv = pokemon.stats.pv + 1


def test_pp_au_dessus_du_max_refuses():
    attaque = _pokemon().attaques[0]
    with pytest.raises(ValidationError):
        attaque.pp = attaque.pp_max + 1


# ---------- battle indexes ----------


def test_adversaire_actif_doit_exister():
    with pytest.raises(ValidationError):
        CombatEnCours(genre="sauvage", adversaires=[_pokemon()], actif_adverse=1)


def test_pokemon_actif_doit_etre_dans_l_equipe():
    partie = _partie()
    partie.equipe = [_pokemon()]
    with pytest.raises(ValidationError):
        partie.combat = CombatEnCours(genre="sauvage", adversaires=[_pokemon()], actif=1)
    partie.combat = CombatEnCours(genre="sauvage", adversaires=[_pokemon()], actif=0)
