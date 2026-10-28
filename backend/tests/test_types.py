"""Type chart and effectiveness multiplier (task 11)."""

import pytest

from moteur import donnees
from moteur.types import calculer_multiplicateur

MULTIPLICATEURS_VALIDES = {0, 0.5, 1, 2}


def test_la_table_couvre_les_18_types_dans_les_deux_sens():
    table = donnees.table_des_types()
    assert len(table) == 18
    for type_attaque, ligne in table.items():
        assert set(ligne) == set(table), type_attaque
        assert set(ligne.values()) <= MULTIPLICATEURS_VALIDES, type_attaque


def test_les_types_des_starters_sont_dans_la_table():
    table = donnees.table_des_types()
    for starter in donnees.starters().values():
        assert set(starter.types) <= set(table), starter.nom


def test_eau_contre_feu():
    assert calculer_multiplicateur("water", ["fire"]) == 2


def test_feu_contre_eau():
    assert calculer_multiplicateur("fire", ["water"]) == 0.5


def test_normal_contre_spectre():
    assert calculer_multiplicateur("normal", ["ghost"]) == 0


def test_double_type():
    assert calculer_multiplicateur("electric", ["water", "flying"]) == 4


def test_type_attaque_inconnu():
    with pytest.raises(ValueError):
        calculer_multiplicateur("unknown", ["fire"])


def test_type_adversaire_inconnu():
    with pytest.raises(ValueError):
        calculer_multiplicateur("fire", ["unknown"])


def test_zero_type():
    with pytest.raises(ValueError):
        calculer_multiplicateur("fire", [])


def test_trois_types():
    with pytest.raises(ValueError):
        calculer_multiplicateur("fire", ["water", "grass", "steel"])


@pytest.mark.parametrize("type_mal_ecrit", ["Fire", " fire", "feu"])
def test_un_type_mal_ecrit_est_refuse(type_mal_ecrit):
    """Types are not normalised: a typo in the imported data must not go unnoticed."""
    with pytest.raises(ValueError):
        calculer_multiplicateur(type_mal_ecrit, ["water"])
    with pytest.raises(ValueError):
        calculer_multiplicateur("water", [type_mal_ecrit])
