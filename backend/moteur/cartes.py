"""Loading of the Tiled maps (JSON export) stored in ``assets/maps/``.

Maps are read once at start-up and kept in memory. Every lookup the game
needs while playing (collision, grass, object on a tile) is an O(1) set or
dict access, prepared here at load time.

A tile coordinate is ``pixel position // 16``. See ``assets/maps/README_cartes.md``
for the layer and object conventions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

TAILLE_TUILE = 16
DOSSIER_CARTES = Path(__file__).resolve().parents[2] / "assets" / "maps"
CALQUES_AFFICHES = ("sol", "decor", "toits")

Case = tuple[int, int]


@dataclass(frozen=True, slots=True)
class ObjetCarte:
    """An object of the ``objets`` layer (NPC, chest, exit…), in tile units."""

    nom: str
    type: str
    x: int
    y: int
    largeur: int
    hauteur: int
    proprietes: dict[str, Any] = field(default_factory=dict)

    def cases(self) -> list[Case]:
        """Every tile covered by the object (a chest is 2 tiles wide)."""
        return [(self.x + dx, self.y + dy) for dy in range(self.hauteur) for dx in range(self.largeur)]


@dataclass(slots=True)
class Carte:
    """A playable map with its collision and grass tiles pre-computed."""

    id: str
    titre: str
    largeur: int
    hauteur: int
    calques: dict[str, list[int]]
    collisions: frozenset[Case]
    herbes: frozenset[Case]
    objets: list[ObjetCarte]
    _objets_par_case: dict[Case, ObjetCarte] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._objets_par_case = {case: o for o in self.objets for case in o.cases()}

    def dans_la_carte(self, x: int, y: int) -> bool:
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def bloquee(self, x: int, y: int) -> bool:
        """True if the player cannot stand on this tile (wall, NPC or outside the map)."""
        return not self.dans_la_carte(x, y) or (x, y) in self.collisions

    def objet_en(self, x: int, y: int) -> ObjetCarte | None:
        """The object covering this tile, if any."""
        return self._objets_par_case.get((x, y))

    def sortie_en(self, x: int, y: int) -> ObjetCarte | None:
        """The exit (door, map edge) covering this tile, if any."""
        objet = self.objet_en(x, y)
        return objet if objet is not None and objet.type == "sortie" else None

    def objet_de_type(self, type_: str) -> ObjetCarte | None:
        """The first object of the given class (e.g. the ``depart`` spawn point)."""
        return next((o for o in self.objets if o.type == type_), None)


def _cases_non_vides(data: list[int], largeur: int) -> frozenset[Case]:
    return frozenset((i % largeur, i // largeur) for i, gid in enumerate(data) if gid)


def _lire_objet(brut: dict[str, Any]) -> ObjetCarte:
    return ObjetCarte(
        nom=brut.get("name", ""),
        type=brut.get("type") or brut.get("class", ""),
        x=int(brut["x"]) // TAILLE_TUILE,
        y=int(brut["y"]) // TAILLE_TUILE,
        largeur=max(1, int(brut["width"]) // TAILLE_TUILE),
        hauteur=max(1, int(brut["height"]) // TAILLE_TUILE),
        proprietes={p["name"]: p["value"] for p in brut.get("properties", [])},
    )


def lire_carte(chemin: Path) -> Carte:
    """Parse one Tiled JSON export."""
    brut = json.loads(chemin.read_text(encoding="utf-8"))
    largeur = brut["width"]
    calques = {c["name"]: c for c in brut["layers"]}
    proprietes = {p["name"]: p["value"] for p in brut.get("properties", [])}

    def tuiles(nom: str) -> frozenset[Case]:
        return _cases_non_vides(calques[nom]["data"], largeur) if nom in calques else frozenset()

    return Carte(
        id=chemin.stem,
        titre=proprietes.get("titre", chemin.stem),
        largeur=largeur,
        hauteur=brut["height"],
        calques={n: calques[n]["data"] for n in CALQUES_AFFICHES if n in calques},
        collisions=tuiles("collisions"),
        herbes=tuiles("herbes"),
        objets=[_lire_objet(o) for o in calques.get("objets", {}).get("objects", [])],
    )


def charger_cartes(dossier: Path = DOSSIER_CARTES) -> dict[str, Carte]:
    """Load every ``*.json`` map of the folder, keyed by file name (``village``, ``route1``…)."""
    cartes = {p.stem: lire_carte(p) for p in sorted(dossier.glob("*.json"))}
    if not cartes:
        raise RuntimeError(f"No map found in {dossier}")
    return cartes
