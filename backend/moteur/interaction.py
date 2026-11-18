"""Interaction rules (Notion task 64): talk, open a chest or heal the team.

Pure functions, like ``exploration``: they read and update a :class:`Partie` but know
nothing about HTTP. The object to act on is the one on the tile in front of the player.
"""

from __future__ import annotations

from collections.abc import Mapping

from .cartes import Carte, ObjetCarte
from .exploration import case_devant
from .modeles import Evenement, Partie


class InteractionNonDisponible(Exception):
    """The object needs a rule that is not written yet (trainer and Tower battles)."""


def cle_objet(carte: Carte, objet: ObjetCarte) -> str:
    """Key ``'carte/nom'`` used in ``coffres_ouverts`` and ``dresseurs_battus``."""
    return f"{carte.id}/{objet.nom}"


def interagir(partie: Partie, cartes: Mapping[str, Carte]) -> Evenement:
    """Act on the object in front of the player.

    Nothing to act on (empty tile, exit) is not an error: the event is ``rien``.
    Raises :class:`InteractionNonDisponible` for the objects that start a battle.
    """
    carte = cartes[partie.position.carte]
    objet = carte.objet_en(*case_devant(partie))
    if objet is None:
        return Evenement(type="rien")

    match objet.type:
        case "pnj":
            return _dialogue(objet)
        case "coffre":
            return _ouvrir_coffre(partie, carte, objet)
        case "soin":
            return _soigner(partie)
        case "dresseur":
            if cle_objet(carte, objet) in partie.dresseurs_battus:
                return _dialogue(objet)
            raise InteractionNonDisponible("Le combat contre un dresseur dépend du moteur de combat")
        case "tour_accueil" | "tour_adversaire":
            raise InteractionNonDisponible("Le mode Tour dépend du moteur de combat")
        case _: 
            return Evenement(type="rien")


def _dialogue(objet: ObjetCarte) -> Evenement:
    return Evenement(type="dialogue", texte=str(objet.proprietes.get("dialogue", "")) or None)


def _ouvrir_coffre(partie: Partie, carte: Carte, objet: ObjetCarte) -> Evenement:
    """Give the item once. Calling again (or from the other tile of the chest) gives nothing."""
    cle = cle_objet(carte, objet)
    if cle in partie.coffres_ouverts:
        return Evenement(type="coffre_vide")

    nom = str(objet.proprietes["objet"])
    # Reassign instead of changing in place: only assignment is validated (see ``Modele``).
    partie.sac = {**partie.sac, nom: partie.sac.get(nom, 0) + 1}
    partie.coffres_ouverts = partie.coffres_ouverts | {cle}
    return Evenement(type="objet_obtenu", objet=nom)


def _soigner(partie: Partie) -> Evenement:
    """Restore the HP of the whole team (PP are not restored, see ``regles.OBJETS_PP``)."""
    for pokemon in partie.equipe:
        pokemon.pv = pokemon.stats.pv
    partie.dernier_soin = partie.position.model_copy()
    return Evenement(type="soin")
