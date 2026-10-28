"""Random draws of a run, reproducible from its seed.

A run lives across many HTTP requests, so the generator cannot simply be
``random.Random(partie.graine)``: rebuilt on each request, it would give the
same draw every time (always an encounter, or never). Each action instead gets
its own generator, seeded with ``(graine, tirages)``, and bumps the counter.
The same seed and the same actions therefore always replay the same run.
"""

from __future__ import annotations

import random

from .modeles import Partie


def generateur(partie: Partie) -> random.Random:
    """The generator for one action: call it once per action, then draw from it as often as needed."""
    rng = random.Random(f"{partie.graine}/{partie.tirages}")
    partie.tirages += 1
    return rng
