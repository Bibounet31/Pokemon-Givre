"""Loading the Tiled maps and the consistency of the world."""

from moteur import donnees
from moteur.cartes import CALQUES_AFFICHES


def test_les_13_cartes_sont_chargees():
    cartes = donnees.cartes()
    assert len(cartes) == 13
    assert "village" in cartes


def test_chaque_carte_a_les_calques_affiches():
    for carte in donnees.cartes().values():
        for nom in CALQUES_AFFICHES:
            assert len(carte.calques[nom]) == carte.largeur * carte.hauteur, f"{carte.id}/{nom}"


def test_chaque_sortie_mene_a_une_case_libre_d_une_carte_existante():
    cartes = donnees.cartes()
    for carte in cartes.values():
        for o in carte.objets:
            if o.type != "sortie":
                continue
            dest = cartes[o.proprietes["vers_carte"]]
            x, y = o.proprietes["vers_x"], o.proprietes["vers_y"]
            assert not dest.bloquee(x, y), f"{carte.id}/{o.nom} -> case bloquée"
            assert dest.sortie_en(x, y) is None, f"{carte.id}/{o.nom} -> arrive sur une sortie"


def test_un_coffre_occupe_ses_deux_cases():
    route1 = donnees.cartes()["route1"]
    coffre = next(o for o in route1.objets if o.type == "coffre" and o.largeur == 2)
    assert route1.objet_en(coffre.x, coffre.y) is coffre
    assert route1.objet_en(coffre.x + 1, coffre.y) is coffre


def test_hors_de_la_carte_est_bloque():
    village = donnees.cartes()["village"]
    assert village.bloquee(-1, 0)
    assert village.bloquee(village.largeur, 0)
