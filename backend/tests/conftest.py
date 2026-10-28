"""Shared fixtures: a test client, a clean store for each test and ready-made runs."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from api.depot import depot
from api.main import app
from moteur.modeles import Mode, Partie


@pytest.fixture(autouse=True)
def depot_vide() -> Iterator[None]:
    depot.vider()
    yield
    depot.vider()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def partie(client: TestClient) -> dict:
    """A new run, waiting for its starter."""
    r = client.post("/runs", json={"graine": 42})
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def partie_exploration(client: TestClient, partie: dict) -> dict:
    """A run in exploration mode, with Charmander."""
    r = client.post(f"/runs/{partie['id']}/starter", json={"pokemon_id": 4})
    assert r.status_code == 200
    return r.json()


def etat(run_id: str) -> Partie:
    """Direct access to a run's state, to set up a situation without playing it."""
    partie = depot.lire(run_id)
    assert partie is not None
    return partie


def forcer_mode(run_id: str, mode: Mode) -> None:
    etat(run_id).mode = mode
