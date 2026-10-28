"""Chargement des cartes Tiled (export JSON) depuis assets/maps/.

Les cartes sont lues une seule fois au démarrage et gardées en mémoire.
Une case = position en pixels // 16.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

TAILLE_TUILE = 16
DOSSIER_CARTES = Path(__file__).resolve().parents[2] / "assets" / "maps"
CALQUES_AFFICHES = ("sol", "decor", "toits")


@dataclass
class ObjetCarte:
    nom: str
    type: str
    x: int
    y: int
    largeur: int
    hauteur: int
    proprietes: dict[str, Any] = field(default_factory=dict)

    def cases(self) -> list[tuple[int, int]]:
        return [(self.x + dx, self.y + dy) for dy in range(self.hauteur) for dx in range(self.largeur)]


@dataclass
class Carte:
    id: str
    titre: str
    largeur: int
    hauteur: int
    calques: dict[str, list[int]]
    collisions: set[tuple[int, int]]
    herbes: set[tuple[int, int]]
    objets: list[ObjetCarte]

    def dans_la_carte(self, x: int, y: int) -> bool:
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def bloquee(self, x: int, y: int) -> bool:
        return not self.dans_la_carte(x, y) or (x, y) in self.collisions

    def sortie_en(self, x: int, y: int) -> ObjetCarte | None:
        for o in self.objets:
            if o.type == "sortie" and (x, y) in o.cases():
                return o
        return None

    def objet_de_type(self, type_: str) -> ObjetCarte | None:
        return next((o for o in self.objets if o.type == type_), None)


def _cases_non_vides(data: list[int], largeur: int) -> set[tuple[int, int]]:
    return {(i % largeur, i // largeur) for i, g in enumerate(data) if g}


def lire_carte(chemin: Path) -> Carte:
    brut = json.loads(chemin.read_text(encoding="utf-8"))
    largeur, hauteur = brut["width"], brut["height"]
    calques = {c["name"]: c for c in brut["layers"]}
    proprietes = {p["name"]: p["value"] for p in brut.get("properties", [])}

    objets = []
    for o in calques.get("objets", {}).get("objects", []):
        objets.append(ObjetCarte(
            nom=o.get("name", ""),
            type=o.get("type") or o.get("class", ""),
            x=int(o["x"]) // TAILLE_TUILE,
            y=int(o["y"]) // TAILLE_TUILE,
            largeur=max(1, int(o["width"]) // TAILLE_TUILE),
            hauteur=max(1, int(o["height"]) // TAILLE_TUILE),
            proprietes={p["name"]: p["value"] for p in o.get("properties", [])},
        ))

    return Carte(
        id=chemin.stem,
        titre=proprietes.get("titre", chemin.stem),
        largeur=largeur,
        hauteur=hauteur,
        calques={n: calques[n]["data"] for n in CALQUES_AFFICHES if n in calques},
        collisions=_cases_non_vides(calques["collisions"]["data"], largeur) if "collisions" in calques else set(),
        herbes=_cases_non_vides(calques["herbes"]["data"], largeur) if "herbes" in calques else set(),
        objets=objets,
    )


def charger_cartes(dossier: Path = DOSSIER_CARTES) -> dict[str, Carte]:
    cartes = {p.stem: lire_carte(p) for p in sorted(dossier.glob("*.json"))}
    if not cartes:
        raise RuntimeError(f"Aucune carte trouvée dans {dossier}")
    return cartes
