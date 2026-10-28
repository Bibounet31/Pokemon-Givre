import json
from pathlib import Path
from fight.type_calculator import calculer_multiplicateur


chemin = Path(__file__).parent.parent / "data" / "types.json"

with open(chemin, "r", encoding="utf-8") as fichier:
    types = json.load(fichier)

print("Feu contre Plante :", types["feu"]["plante"])
print("Eau contre Feu :", types["eau"]["feu"])
print("Normal contre Spectre :", types["normal"]["spectre"])

 
def test_super_efficace():
    assert calculer_multiplicateur("feu", ["plante"]) == 2


def test_double_type():
    assert calculer_multiplicateur("electrik", ["eau", "vol"]) == 4


def test_immunite():
    assert calculer_multiplicateur("normal", ["spectre"]) == 0


def test_resistance_double():
    assert calculer_multiplicateur("feu", ["eau", "dragon"]) == 0.25
