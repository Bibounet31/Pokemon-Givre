"""One router per domain, so each teammate works in their own file."""

from . import catalogue, combat, exploration, parties

ROUTEURS = (catalogue.router, parties.router, exploration.router, combat.router)
