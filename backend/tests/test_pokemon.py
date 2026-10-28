"""Stats of team Pokémon, checked against values computed by hand."""

from moteur import donnees
from moteur.pokemon import calculer_pv, calculer_stat, creer_pokemon


def test_formules_calculees_a_la_main():
    # Bulbasaur, level 5: HP = 2*45*5//100 + 5 + 10 = 19 ; Attack = 2*49*5//100 + 5 = 9
    assert calculer_pv(45, 5) == 19
    assert calculer_stat(49, 5) == 9
    # Level 50, base 100: HP = 100 + 50 + 10 ; other stat = 100 + 5
    assert calculer_pv(100, 50) == 160
    assert calculer_stat(100, 50) == 105


def test_creer_pokemon_plein_de_pv_et_de_pp():
    salameche = creer_pokemon(donnees.starters()[4], 5)
    # Charmander, base HP 39, level 5: 2*39*5//100 + 5 + 10 = 18
    assert salameche.pv == salameche.stats.pv == 18
    assert salameche.stats.vitesse == 2 * 65 * 5 // 100 + 5
    assert all(a.pp == a.pp_max for a in salameche.attaques)
    assert not salameche.ko


def test_un_pokemon_a_0_pv_est_ko():
    pokemon = creer_pokemon(donnees.starters()[1], 5)
    pokemon.pv = 0
    assert pokemon.ko
