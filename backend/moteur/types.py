from .donnees import types


def calculer_multiplicateur(
    type_attaque: str,
    types_adversaire: list[str],
) -> float:
    """Calculate an attack's type effectiveness against a Pokémon.


    Args:
        type_attaque: Type of the attacking move.
        types_adversaire: One or two defending Pokémon types.

    Returns:
        The combined effectiveness multiplier.

    Raises:
        ValueError: If the attack or defender type is unknown,
            or the number of defending types is invalid.
    """
    table = types()
    type_attaque = type_attaque.lower().strip()

    if type_attaque not in table:
        raise ValueError(f"Unknown attack type: {type_attaque}")

    if not 1 <= len(types_adversaire) <= 2:
        raise ValueError("A Pokémon must have one or two types")

    multiplicateur = 1.0

    for type_adverse in types_adversaire:
        type_adverse = type_adverse.lower().strip()

        if type_adverse not in table[type_attaque]:
            raise ValueError(f"Unknown defender type: {type_adverse}")

        multiplicateur *= table[type_attaque][type_adverse]

    return multiplicateur
