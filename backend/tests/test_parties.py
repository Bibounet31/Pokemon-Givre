"""Creating a run, reading it and choosing the starter."""

from moteur.regles import CARTE_DE_DEPART


def test_creer_puis_lire_partie(client, partie):
    assert partie["mode"] == "choix_starter"
    assert partie["graine"] == 42
    assert partie["position"]["carte"] == CARTE_DE_DEPART
    assert partie["equipe"] == []
    assert client.get(f"/runs/{partie['id']}").json() == partie


def test_creer_partie_sans_graine_en_tire_une(client):
    r = client.post("/runs")
    assert r.status_code == 201
    assert isinstance(r.json()["graine"], int)


def test_partie_inconnue_404(client):
    assert client.get("/runs/nope").status_code == 404


def test_choisir_starter_passe_en_exploration(partie_exploration):
    assert partie_exploration["mode"] == "exploration"
    (pokemon,) = partie_exploration["equipe"]
    assert pokemon["nom"] == "charmander"


def test_le_starter_part_avec_tous_ses_pv_et_pp(partie_exploration):
    pokemon = partie_exploration["equipe"][0]
    assert pokemon["pv"] == pokemon["stats"]["pv"]
    assert not pokemon["ko"]
    assert all(a["pp"] == a["pp_max"] for a in pokemon["attaques"])


def test_starter_invalide_422(client, partie):
    url = f"/runs/{partie['id']}/starter"
    assert client.post(url, json={"pokemon_id": 150}).status_code == 422
    assert client.post(url, json={}).status_code == 422


def test_choisir_starter_deux_fois_409(client, partie_exploration):
    r = client.post(f"/runs/{partie_exploration['id']}/starter", json={"pokemon_id": 1})
    assert r.status_code == 409
