"""CORS and the committed OpenAPI contract."""

from scripts.exporter_openapi import CHEMIN, generer


def test_cors_autorise_seulement_le_front_vite(client):
    ok = client.get("/starters", headers={"Origin": "http://localhost:5173"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:5173"
    ko = client.get("/starters", headers={"Origin": "http://evil.example"})
    assert "access-control-allow-origin" not in ko.headers


def test_openapi_json_est_a_jour():
    """The front-end types are generated from this file: it must match the code."""
    assert CHEMIN.exists() and CHEMIN.read_text(encoding="utf-8") == generer(), (
        "openapi.json is out of date: run `python -m scripts.exporter_openapi` from backend/"
    )
