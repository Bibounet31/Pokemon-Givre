"""Mode x route matrix (Notion design doc, table 4.3).

Every action route only works in one mode. In any other mode it answers 409
and the run is left unchanged. An unknown run is always a 404.
"""

import pytest

from moteur.modeles import Mode

from .conftest import forcer_mode

# (path, body, required mode)
ACTIONS = [
    ("/runs/{id}/starter", {"pokemon_id": 4}, Mode.choix_starter),
    ("/runs/{id}/move", {"direction": "down"}, Mode.exploration),
    ("/runs/{id}/interact", None, Mode.exploration),
    ("/runs/{id}/battle/actions", {"type": "flee"}, Mode.combat),
]


@pytest.mark.parametrize("mode", list(Mode))
@pytest.mark.parametrize(("chemin", "corps", "mode_requis"), ACTIONS)
def test_matrice_mode_route(client, partie, mode, chemin, corps, mode_requis):
    forcer_mode(partie["id"], mode)
    avant = client.get(f"/runs/{partie['id']}").json()

    r = client.post(chemin.format(id=partie["id"]), json=corps)

    if mode == mode_requis:
        assert r.status_code != 409
    else:
        assert r.status_code == 409
        assert client.get(f"/runs/{partie['id']}").json() == avant


@pytest.mark.parametrize(("chemin", "corps", "_mode"), ACTIONS)
def test_partie_inconnue_404(client, chemin, corps, _mode):
    assert client.post(chemin.format(id="inconnue"), json=corps).status_code == 404


def test_get_run_marche_dans_tous_les_modes(client, partie):
    for mode in Mode:
        forcer_mode(partie["id"], mode)
        assert client.get(f"/runs/{partie['id']}").status_code == 200


@pytest.mark.parametrize(
    ("chemin", "corps"),
    [("/runs/{id}/interact", None), ("/runs/{id}/battle/actions", {"type": "attack", "move_id": "scratch"})],
)
def test_routes_a_venir_501(client, partie_exploration, chemin, corps):
    """Contract v2 routes not implemented yet answer 501 in the right mode."""
    if "battle" in chemin:
        forcer_mode(partie_exploration["id"], Mode.combat)
    assert client.post(chemin.format(id=partie_exploration["id"]), json=corps).status_code == 501


def test_action_de_combat_inconnue_422(client, partie):
    forcer_mode(partie["id"], Mode.combat)
    r = client.post(f"/runs/{partie['id']}/battle/actions", json={"type": "dance"})
    assert r.status_code == 422
