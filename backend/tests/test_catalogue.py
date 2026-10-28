"""GET /starters and GET /maps/{map_id}."""


def test_starters(client):
    r = client.get("/starters")
    assert r.status_code == 200
    starters = r.json()
    assert [s["id"] for s in starters] == [1, 4, 7]
    assert all(s["stats_base"]["pv"] > 0 and s["attaques"] for s in starters)


def test_get_map(client):
    r = client.get("/maps/village")
    assert r.status_code == 200
    data = r.json()
    assert data["largeur"] == 20 and data["hauteur"] == 15
    assert set(data["calques"]) == {"sol", "decor", "toits"}
    assert len(data["calques"]["sol"]) == 20 * 15


def test_get_map_cache_les_sorties_et_le_depart(client):
    types = {o["type"] for o in client.get("/maps/village").json()["objets"]}
    assert types.isdisjoint({"sortie", "depart"})


def test_get_map_inconnue_404(client):
    r = client.get("/maps/atlantide")
    assert r.status_code == 404
    assert r.json() == {"detail": "Carte introuvable"}
