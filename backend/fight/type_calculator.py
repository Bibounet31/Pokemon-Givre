
import json
from pathlib import Path

CHEMIN_JSON = Path(__file__).resolve().parent.parent / "data" / "types.json"

with open(CHEMIN_JSON, "r", encoding="utf-8") as fichier:
    TABLE_TYPES = json.load(fichier)


def calculer_multiplicateur(type_attaque: str, types_adversaire: list[str]) -> float:
    """
    Calcule l'efficacité d'une attaque contre un Pokémon.

    Fonction à appeler à chaque attaque pour calculer sont multiplicateur de dégats.

    type_attaque : type de l'attaque utilisée
    types_adversaire : liste des types du Pokémon adverse

    Retourne : 0, 0.25, 0.5, 1, 2 ou 4
    """

    type_attaque = type_attaque.lower().strip()
    multiplicateur = 1.0

    if type_attaque not in TABLE_TYPES:
        raise ValueError(f"Type d'attaque inconnu : {type_attaque}")

    if not 1 <= len(types_adversaire) <= 2:
        raise ValueError("Un Pokémon doit avoir 1 ou 2 types")

    for type_adverse in types_adversaire:
        type_adverse = type_adverse.lower().strip()

        if type_adverse not in TABLE_TYPES[type_attaque]:
            raise ValueError(f"Type adverse inconnu : {type_adverse}")

        multiplicateur *= TABLE_TYPES[type_attaque][type_adverse]

    return multiplicateur
