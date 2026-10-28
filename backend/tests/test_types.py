import pytest

from moteur.types import calculer_multiplicateur


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
