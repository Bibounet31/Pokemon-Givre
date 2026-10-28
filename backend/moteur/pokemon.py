"""Creation of team Pokémon from species data.

Stats use the main-series formula with no IVs or EVs, so a species at a given
level always has the same stats (reproducible and easy to check by hand).
"""

from __future__ import annotations

from .modeles import AttaqueConnue, Espece, PokemonEquipe, Statistiques


def calculer_stat(base: int, niveau: int) -> int:
    """Attack, Defense, Sp. Atk, Sp. Def or Speed at ``niveau``."""
    return 2 * base * niveau // 100 + 5


def calculer_pv(base: int, niveau: int) -> int:
    """Maximum HP at ``niveau``."""
    return 2 * base * niveau // 100 + niveau + 10


def calculer_stats(base: Statistiques, niveau: int) -> Statistiques:
    return Statistiques(
        pv=calculer_pv(base.pv, niveau),
        attaque=calculer_stat(base.attaque, niveau),
        defense=calculer_stat(base.defense, niveau),
        attaque_spe=calculer_stat(base.attaque_spe, niveau),
        defense_spe=calculer_stat(base.defense_spe, niveau),
        vitesse=calculer_stat(base.vitesse, niveau),
    )


def creer_pokemon(espece: Espece, niveau: int) -> PokemonEquipe:
    """A fresh Pokémon: full HP and full PP."""
    stats = calculer_stats(espece.stats_base, niveau)
    return PokemonEquipe(
        id=espece.id,
        nom=espece.nom,
        nom_fr=espece.nom_fr,
        types=list(espece.types),
        niveau=niveau,
        stats=stats,
        pv=stats.pv,
        attaques=[AttaqueConnue(id=a.id, pp=a.pp, pp_max=a.pp) for a in espece.attaques],
    )
