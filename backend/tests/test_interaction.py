"""Talking, opening chests and healing (Notion task 64), through the API and the engine."""

from __future__ import annotations

import pytest

from moteur import donnees
from moteur.interaction import InteractionNonDisponible, interagir

from .conftest import etat


def _se_placer_devant(run_id: str, carte_id: str, nom: str, tuile: int = 0) -> None:
    """Put the player on a free tile facing tile number ``tuile`` of object ``nom`` (setup, no walking)."""
    carte = donnees.cartes()[carte_id]
    objet = next(o for o in carte.objets if o.nom == nom)
    cible_x, cible_y = objet.cases()[tuile]
    position = etat(run_id).position
    for orientation, (dx, dy) in {"down": (0, -1), "up": (0, 1), "right": (-1, 0), "left": (1, 0)}.items():
        x, y = cible_x + dx, cible_y + dy
        if carte.dans_la_carte(x, y) and not carte.bloquee(x, y) and carte.objet_en(x, y) is None:
            position.carte, position.x, position.y, position.orientation = carte_id, x, y, orientation
            return
    pytest.fail(f"no free tile next to {nom}")


def _interagir(client, run_id: str) -> dict:
    r = client.post(f"/runs/{run_id}/interact")
    assert r.status_code == 200
    return r.json()


def test_rien_devant_soi(client, partie_exploration):
    run_id = partie_exploration["id"]
    carte = donnees.cartes()["village"]
    depart = carte.objet_de_type("depart")
    position = etat(run_id).position
    position.x, position.y, position.orientation = depart.x, depart.y, "down"
    assert carte.objet_en(depart.x, depart.y + 1) is None

    assert _interagir(client, run_id)["evenement"]["type"] == "rien"


def test_pnj_renvoie_son_dialogue(client, partie_exploration):
    run_id = partie_exploration["id"]
    _se_placer_devant(run_id, "village", "voisin")
    evenement = _interagir(client, run_id)["evenement"]
    assert evenement["type"] == "dialogue"
    assert evenement["texte"] == "Le professeur t'attend dans son labo, à gauche."


def test_coffre_donne_son_objet_une_seule_fois(client, partie_exploration):
    run_id = partie_exploration["id"]
    _se_placer_devant(run_id, "village", "village-coffre-1")

    premier = _interagir(client, run_id)
    assert premier["evenement"] == {"type": "objet_obtenu", "carte": None, "texte": None, "objet": "potion"}
    assert premier["partie"]["sac"] == {"potion": 1}
    assert premier["partie"]["coffres_ouverts"] == ["village/village-coffre-1"]

    for _ in range(3):
        suivant = _interagir(client, run_id)
        assert suivant["evenement"]["type"] == "coffre_vide"
        assert suivant["partie"]["sac"] == {"potion": 1}


def test_coffre_ouvert_ne_se_rouvre_pas_par_l_autre_case(client, partie_exploration):
    """A chest is 2 tiles wide: both tiles are the same chest."""
    run_id = partie_exploration["id"]
    _se_placer_devant(run_id, "village", "village-coffre-1", tuile=0)
    assert _interagir(client, run_id)["evenement"]["type"] == "objet_obtenu"

    _se_placer_devant(run_id, "village", "village-coffre-1", tuile=1)
    r = _interagir(client, run_id)
    assert r["evenement"]["type"] == "coffre_vide"
    assert r["partie"]["sac"] == {"potion": 1}


def test_deux_coffres_differents_s_accumulent_dans_le_sac(client, partie_exploration):
    run_id = partie_exploration["id"]
    _se_placer_devant(run_id, "route1", "route1-coffre-1")
    _interagir(client, run_id)
    _se_placer_devant(run_id, "route1", "route1-coffre-2")
    _interagir(client, run_id)
    assert etat(run_id).sac == {"potion": 1, "pokeball": 1}


def test_infirmiere_soigne_toute_l_equipe(client, partie_exploration):
    run_id = partie_exploration["id"]
    partie = etat(run_id)
    pokemon = partie.equipe[0]
    pokemon.pv = 1
    pokemon.attaques[0].pp = 0
    _se_placer_devant(run_id, "centre_village", "infirmiere")

    r = _interagir(client, run_id)

    assert r["evenement"]["type"] == "soin"
    assert partie.equipe[0].pv == partie.equipe[0].stats.pv
    assert partie.equipe[0].attaques[0].pp == 0  # HP only, PP need an ether
    assert partie.dernier_soin == partie.position


def test_dresseur_pas_encore_battu_501(client, partie_exploration):
    run_id = partie_exploration["id"]
    _se_placer_devant(run_id, "route1", "gamin-paul")
    r = client.post(f"/runs/{run_id}/interact")
    assert r.status_code == 501
    assert etat(run_id).mode == "exploration"


def test_dresseur_battu_ne_relance_plus_le_combat(client, partie_exploration):
    run_id = partie_exploration["id"]
    etat(run_id).dresseurs_battus = {"route1/gamin-paul"}
    _se_placer_devant(run_id, "route1", "gamin-paul")
    r = _interagir(client, run_id)
    assert r["evenement"]["type"] == "dialogue"
    assert r["partie"]["mode"] == "exploration"


def test_tour_leve_interaction_non_disponible():
    from moteur.modeles import Partie, Position

    carte = donnees.cartes()["tour_hall"]
    hotesse = next(o for o in carte.objets if o.type == "tour_accueil")
    partie = Partie(
        id="t",
        mode="exploration",
        graine=1,
        position=Position(carte="tour_hall", x=hotesse.x, y=hotesse.y + 1, orientation="up"),
    )
    with pytest.raises(InteractionNonDisponible):
        interagir(partie, donnees.cartes())
