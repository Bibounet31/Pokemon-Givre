"""Type effectiveness: how much a move's type multiplies its damage against a Pokémon.

Type names are the PokéAPI ones (``fire``, ``water``…), as in the imported data.
They are not normalised: an unknown or misspelt type is a data bug and raises.
"""

from __future__ import annotations

from .donnees import table_des_types


def calculer_multiplicateur(type_attaque: str, types_adversaire: list[str]) -> float:
    """Product of the multipliers against each of the defender's one or two types (e.g. 4.0, 0.25 or 0).

    Raises ``ValueError`` for an unknown type or a defender with 0 or 3+ types.
    """
    table = table_des_types()
    if type_attaque not in table:
        raise ValueError(f"Unknown attack type: {type_attaque!r}")
    if not 1 <= len(types_adversaire) <= 2:
        raise ValueError(f"A Pokémon has one or two types, not {len(types_adversaire)}")

    multiplicateur = 1.0
    for type_adverse in types_adversaire:
        if type_adverse not in table[type_attaque]:
            raise ValueError(f"Unknown defender type: {type_adverse!r}")
        multiplicateur *= table[type_attaque][type_adverse]
    return multiplicateur
