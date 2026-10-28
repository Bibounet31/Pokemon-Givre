"""Two requests on the same run must never interleave (see api/dependances.py)."""

import inspect

from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from api.routes import ROUTEURS


def _fonctions(dependant: Dependant):
    yield dependant.call
    for sous_dependance in dependant.dependencies:
        yield from _fonctions(sous_dependance)


def test_les_routes_d_une_partie_tournent_sur_la_boucle_d_evenements():
    """A ``def`` route or dependency would run in a thread pool, next to another request on the same run."""
    routes = [r for routeur in ROUTEURS for r in routeur.routes if isinstance(r, APIRoute) and "{run_id}" in r.path]
    assert routes
    for route in routes:
        for fonction in _fonctions(route.dependant):
            assert inspect.iscoroutinefunction(fonction), f"{route.path}: {fonction.__name__} doit être async def"
