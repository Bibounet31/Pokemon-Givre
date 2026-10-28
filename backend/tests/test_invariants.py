"""Invariants of the game state, enforced by the models even when the engine changes a run."""

import pytest
from pydantic import ValidationError

from moteur import donnees
from moteur.aleatoire import generateur
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


# ---------- seeded random draws ----------


def test_chaque_action_a_son_propre_tirage():
    partie = _partie()
    tirages = [generateur(partie).random() for _ in range(5)]
    assert len(set(tirages)) == 5
    assert partie.tirages == 5


def test_meme_graine_memes_tirages():
    a, b = _partie(graine=42), _partie(graine=42)
    assert [generateur(a).random() for _ in range(5)] == [generateur(b).random() for _ in range(5)]
    assert generateur(_partie(graine=1)).random() != generateur(_partie(graine=2)).random()
