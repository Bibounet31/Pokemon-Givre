from fastapi.testclient import TestClient

from api.main import CARTES, app

client = TestClient(app)


def nouvelle_partie(graine: int = 42) -> dict:
    r = client.post("/runs", json={"graine": graine})
    assert r.status_code == 201
    return r.json()


def partie_en_exploration() -> dict:
    partie = nouvelle_partie()
    r = client.post(f"/runs/{partie['id']}/starter", json={"pokemon_id": 4})
    assert r.status_code == 200
    return r.json()


# ---------- cartes ----------

def test_les_13_cartes_sont_chargees():
    assert len(CARTES) == 13
    assert "village" in CARTES


def test_chaque_sortie_mene_a_une_case_libre_d_une_carte_existante():
    for carte in CARTES.values():
        for o in carte.objets:
            if o.type != "sortie":
                continue
            dest = CARTES[o.proprietes["vers_carte"]]
            x, y = o.proprietes["vers_x"], o.proprietes["vers_y"]
            assert not dest.bloquee(x, y), f"{carte.id}/{o.nom} -> case bloquée"
            assert dest.sortie_en(x, y) is None, f"{carte.id}/{o.nom} -> arrive sur une sortie"


def test_get_map():
    r = client.get("/maps/village")
    assert r.status_code == 200
    data = r.json()
    assert data["largeur"] == 20 and data["hauteur"] == 15
    assert set(data["calques"]) == {"sol", "decor", "toits"}
    assert len(data["calques"]["sol"]) == 20 * 15
    assert all(o["type"] != "sortie" for o in data["objets"])


def test_get_map_inconnue_404():
    assert client.get("/maps/atlantide").status_code == 404


# ---------- starters et parties ----------

def test_starters():
    r = client.get("/starters")
    assert r.status_code == 200
    assert len(r.json()) == 3


def test_creer_puis_lire_partie():
    partie = nouvelle_partie()
    assert partie["mode"] == "choix_starter"
    assert partie["position"]["carte"] == "village"
    assert client.get(f"/runs/{partie['id']}").json() == partie


def test_partie_inconnue_404():
    assert client.get("/runs/nope").status_code == 404


def test_choisir_starter_passe_en_exploration():
    partie = partie_en_exploration()
    assert partie["mode"] == "exploration"
    assert partie["equipe"][0]["nom"] == "charmander"


def test_starter_invalide_422():
    partie = nouvelle_partie()
    assert client.post(f"/runs/{partie['id']}/starter", json={"pokemon_id": 150}).status_code == 422
    assert client.post(f"/runs/{partie['id']}/starter", json={}).status_code == 422


def test_choisir_starter_deux_fois_409():
    partie = partie_en_exploration()
    assert client.post(f"/runs/{partie['id']}/starter", json={"pokemon_id": 1}).status_code == 409


# ---------- déplacement ----------

def test_move_avant_starter_409():
    partie = nouvelle_partie()
    assert client.post(f"/runs/{partie['id']}/move", json={"direction": "up"}).status_code == 409


def test_direction_invalide_422():
    partie = partie_en_exploration()
    assert client.post(f"/runs/{partie['id']}/move", json={"direction": "nord"}).status_code == 422


def test_move_sur_case_libre():
    partie = partie_en_exploration()
    x, y = partie["position"]["x"], partie["position"]["y"]
    r = client.post(f"/runs/{partie['id']}/move", json={"direction": "down"}).json()
    assert r["evenement"]["type"] == "deplace"
    assert (r["partie"]["position"]["x"], r["partie"]["position"]["y"]) == (x, y + 1)
    assert r["partie"]["position"]["orientation"] == "down"


def test_mur_renvoie_200_et_ne_bouge_pas():
    partie = partie_en_exploration()
    pid = partie["id"]
    # On marche vers la gauche jusqu'à buter (la bordure de sapins arrête forcément).
    for _ in range(25):
        r = client.post(f"/runs/{pid}/move", json={"direction": "left"})
        assert r.status_code == 200
        if r.json()["evenement"]["type"] == "bloque":
            break
    else:
        raise AssertionError("jamais bloqué")
    avant = r.json()["partie"]["position"]
    apres = client.post(f"/runs/{pid}/move", json={"direction": "left"}).json()["partie"]["position"]
    assert avant == apres


def test_sortie_change_de_carte():
    partie = partie_en_exploration()
    pid = partie["id"]
    # On place le joueur juste sous une sortie du village puis on monte.
    sortie = next(o for o in CARTES["village"].objets if o.type == "sortie" and o.nom == "porte-labo")
    from api.main import PARTIES
    PARTIES[pid].position.x, PARTIES[pid].position.y = sortie.x, sortie.y + 1
    r = client.post(f"/runs/{pid}/move", json={"direction": "up"}).json()
    assert r["evenement"] == {"type": "changement_carte", "carte": "labo"}
    assert r["partie"]["position"]["carte"] == "labo"
    assert (r["partie"]["position"]["x"], r["partie"]["position"]["y"]) == (
        sortie.proprietes["vers_x"], sortie.proprietes["vers_y"])


# ---------- CORS ----------

def test_cors_autorise_seulement_le_front_vite():
    ok = client.get("/starters", headers={"Origin": "http://localhost:5173"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    ko = client.get("/starters", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in ko.headers
