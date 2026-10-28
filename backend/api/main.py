"""Point d'entrée FastAPI.

Lancer depuis backend/ :  uvicorn api.main:app --reload
Documentation interactive : http://localhost:8000/docs
"""
from __future__ import annotations

import json
import random
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .cartes import TAILLE_TUILE, Carte, charger_cartes
from .schemas import (
    CarteReponse,
    ChoixStarter,
    Deplacement,
    Evenement,
    Mode,
    NouvellePartie,
    ObjetVisible,
    Partie,
    PokemonEquipe,
    Position,
    ReponseDeplacement,
    Starter,
)

DOSSIER_DONNEES = Path(__file__).resolve().parents[1] / "data"
CARTE_DE_DEPART = "village"
# Objets que le front affiche ; les sorties, coffres et le départ restent côté serveur.
TYPES_VISIBLES = {"pnj", "dresseur", "soin", "tour_accueil", "tour_adversaire", "coffre"}
PAS = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}

app = FastAPI(title="Yboost Pokémon API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

CARTES: dict[str, Carte] = charger_cartes()
STARTERS: list[Starter] = [
    Starter(**s) for s in json.loads((DOSSIER_DONNEES / "starters.json").read_text(encoding="utf-8"))
]
# Parties en mémoire : un redémarrage du serveur les efface (voulu pour le projet).
PARTIES: dict[str, Partie] = {}


# ---------- utilitaires ----------

def _partie(run_id: str) -> Partie:
    partie = PARTIES.get(run_id)
    if partie is None:
        raise HTTPException(status_code=404, detail="Partie introuvable")
    return partie


def _exiger_mode(partie: Partie, mode: Mode) -> None:
    if partie.mode != mode:
        raise HTTPException(
            status_code=409,
            detail=f"Action impossible en mode {partie.mode.value} (attendu : {mode.value})",
        )


def _position_de_depart() -> Position:
    depart = CARTES[CARTE_DE_DEPART].objet_de_type("depart")
    if depart is None:
        raise RuntimeError(f"La carte {CARTE_DE_DEPART} n'a pas d'objet 'depart'")
    return Position(carte=CARTE_DE_DEPART, x=depart.x, y=depart.y)


# ---------- routes ----------

@app.get("/starters", response_model=list[Starter])
def lister_starters() -> list[Starter]:
    return STARTERS


@app.get("/maps/{map_id}", response_model=CarteReponse)
def lire_carte(map_id: str) -> CarteReponse:
    carte = CARTES.get(map_id)
    if carte is None:
        raise HTTPException(status_code=404, detail="Carte introuvable")
    return CarteReponse(
        id=carte.id,
        titre=carte.titre,
        largeur=carte.largeur,
        hauteur=carte.hauteur,
        taille_tuile=TAILLE_TUILE,
        calques=carte.calques,
        objets=[
            ObjetVisible(**o.__dict__) for o in carte.objets if o.type in TYPES_VISIBLES
        ],
    )


@app.post("/runs", response_model=Partie, status_code=201)
def creer_partie(demande: NouvellePartie | None = None) -> Partie:
    graine = demande.graine if demande and demande.graine is not None else random.randrange(2**31)
    partie = Partie(
        id=uuid.uuid4().hex,
        mode=Mode.choix_starter,
        graine=graine,
        position=_position_de_depart(),
    )
    PARTIES[partie.id] = partie
    return partie


@app.get("/runs/{run_id}", response_model=Partie)
def lire_partie(run_id: str) -> Partie:
    return _partie(run_id)


@app.post("/runs/{run_id}/starter", response_model=Partie)
def choisir_starter(run_id: str, choix: ChoixStarter) -> Partie:
    partie = _partie(run_id)
    _exiger_mode(partie, Mode.choix_starter)
    starter = next((s for s in STARTERS if s.id == choix.pokemon_id), None)
    if starter is None:
        raise HTTPException(status_code=422, detail="Ce Pokémon ne fait pas partie des starters")
    partie.equipe = [PokemonEquipe(id=starter.id, nom=starter.nom, nom_fr=starter.nom_fr, niveau=starter.niveau)]
    partie.mode = Mode.exploration
    return partie


@app.post("/runs/{run_id}/move", response_model=ReponseDeplacement)
def deplacer(run_id: str, deplacement: Deplacement) -> ReponseDeplacement:
    partie = _partie(run_id)
    _exiger_mode(partie, Mode.exploration)
    pos = partie.position
    pos.orientation = deplacement.direction
    carte = CARTES[pos.carte]

    dx, dy = PAS[deplacement.direction]
    nx, ny = pos.x + dx, pos.y + dy
    if carte.bloquee(nx, ny):
        return ReponseDeplacement(partie=partie, evenement=Evenement(type="bloque"))

    sortie = carte.sortie_en(nx, ny)
    if sortie is not None:
        destination = sortie.proprietes["vers_carte"]
        pos.carte = destination
        pos.x = int(sortie.proprietes["vers_x"])
        pos.y = int(sortie.proprietes["vers_y"])
        return ReponseDeplacement(
            partie=partie, evenement=Evenement(type="changement_carte", carte=destination)
        )

    pos.x, pos.y = nx, ny
    # Les rencontres sauvages (passage en mode combat) viendront avec le moteur de combat.
    return ReponseDeplacement(
        partie=partie,
        evenement=Evenement(type="deplace"),
        dans_les_herbes=(nx, ny) in carte.herbes,
    )
