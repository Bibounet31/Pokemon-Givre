"""Moving on the map, through the API and directly through the engine."""

import pytest

from moteur import donnees
from moteur.exploration import case_devant, deplacer
from moteur.modeles import Partie, Position

from .conftest import etat


def test_move_sur_case_libre(client, partie_exploration):
    x, y = partie_exploration["position"]["x"], partie_exploration["position"]["y"]
    r = client.post(f"/runs/{partie_exploration['id']}/move", json={"direction": "down"}).json()
    assert r["evenement"]["type"] == "deplace"
    assert (r["partie"]["position"]["x"], r["partie"]["position"]["y"]) == (x, y + 1)
    assert r["partie"]["position"]["orientation"] == "down"


def test_direction_invalide_422(client, partie_exploration):
    r = client.post(f"/runs/{partie_exploration['id']}/move", json={"direction": "nord"})
    assert r.status_code == 422


def test_mur_renvoie_200_et_ne_bouge_pas(client, partie_exploration):
    url = f"/runs/{partie_exploration['id']}/move"
    # Walk left until blocked: the border of trees always stops the player.
    for _ in range(25):
        r = client.post(url, json={"direction": "left"})
        assert r.status_code == 200
        if r.json()["evenement"]["type"] == "bloque":
            break
    else:
        pytest.fail("never blocked")
    avant = r.json()["partie"]["position"]
    apres = client.post(url, json={"direction": "left"}).json()["partie"]["position"]
    assert avant == apres


def test_sortie_change_de_carte(client, partie_exploration):
    run_id = partie_exploration["id"]
    sortie = next(o for o in donnees.cartes()["village"].objets if o.type == "sortie" and o.nom == "porte-labo")
    position = etat(run_id).position
    position.x, position.y = sortie.x, sortie.y + 1

    r = client.post(f"/runs/{run_id}/move", json={"direction": "up"}).json()

    assert r["evenement"]["type"] == "changement_carte"
    assert r["evenement"]["carte"] == "labo"
    assert r["partie"]["position"] == {
        "carte": "labo",
        "x": sortie.proprietes["vers_x"],
        "y": sortie.proprietes["vers_y"],
        "orientation": "up",
    }


# ---------- engine, without HTTP ----------


def _partie_au_depart() -> Partie:
    depart = donnees.cartes()["village"].objet_de_type("depart")
    assert depart is not None
    return Partie(id="t", mode="exploration", graine=1, position=Position(carte="village", x=depart.x, y=depart.y))


def test_case_devant_suit_l_orientation():
    partie = _partie_au_depart()
    partie.position.orientation = "right"
    assert case_devant(partie) == (partie.position.x + 1, partie.position.y)


def test_invariant_le_joueur_reste_sur_une_case_praticable():
    partie = _partie_au_depart()
    cartes = donnees.cartes()
    for direction in ["left"] * 30 + ["up"] * 30 + ["right"] * 30 + ["down"] * 30:
        deplacer(partie, direction, cartes)
        p = partie.position
        assert not cartes[p.carte].bloquee(p.x, p.y)
