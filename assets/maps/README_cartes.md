# Cartes du jeu

13 cartes Tiled : 5 zones extérieures et 8 intérieurs. Chaque carte existe en deux fichiers :

- `nom.tmx` : le fichier de travail, à ouvrir et retoucher dans Tiled ;
- `nom.json` : l'export que l'API charge. **Après une retouche dans Tiled, refaire Fichier › Exporter (Ctrl+E).**

Les aperçus sont dans `apercus/`, et `apercus/_monde.png` montre tout le monde d'un coup.

## Le monde

```
Bourg Départ ──nord──> Route 1 ──nord──> Désert de Sable ──nord──> Tour de Combat
   │                     │                    │                        │
   ├ labo                └ est : Forêt        ├ centre_desert          └ tour_hall ──porte du fond──> tour_salle
   ├ maison_joueur                            ├ maison_desert
   └ centre_village                           └ arene (2 champions)
```

| Carte | Titre | Taille | Rôle |
| --- | --- | --- | --- |
| `village` | Bourg Départ | 20×15 | Point de départ (`depart`), 3 maisons avec intérieur |
| `route1` | Route 1 | 20×30 | **Tutoriel** : 3 zones d'herbes, 2 dresseurs, 2 coffres, un guide |
| `foret` | Forêt Murmure | 20×15 | Zone « intérieure » de la Route 1 : herbes, 1 dresseur, coffre caché |
| `desert` | Désert de Sable | 24×20 | Autre biome : herbes sèches, 3 dresseurs, oasis, arène |
| `arene` | Arène des Sables | 13×15 | 1 apprenti + **2 champions** (les jumeaux Dune et Roc) |
| `tour` | Tour de Combat | 20×15 | Esplanade de la Tour, mode roguelite |
| `tour_hall` | Hall de la Tour | 13×10 | Hôtesse (lance le roguelite) + infirmière |
| `tour_salle` | Salle de combat | 11×9 | Salle réutilisée à chaque étage |
| `labo`, `maison_joueur`, `centre_village`, `centre_desert`, `maison_desert` | | | Intérieurs |

## Calques (identiques sur toutes les cartes)

| Calque | Rôle | Affiché par le front ? |
| --- | --- | --- |
| `sol` | Herbe, sable, eau, sols intérieurs | Oui |
| `decor` | Chemins, arbres, murs, meubles, tapis | Oui |
| `toits` | Toits, portes, fenêtres, objets muraux (par-dessus `decor`) | Oui |
| `collisions` | Toute tuile ≠ 0 = case bloquée | Non (masqué) |
| `herbes` | Toute tuile ≠ 0 = rencontres sauvages possibles | Non (masqué) |
| `objets` | Calque d'objets (voir ci-dessous) | Non : le front dessine les PNJ |

Ordre d'affichage : `sol`, puis `decor`, puis `toits`.

## Objets

Tous les objets sont des rectangles de 16×16 px (32×16 pour un coffre). **Case = position en pixels ÷ 16.**
Dans le JSON, la classe de l'objet est dans le champ `type`.

| Classe | Propriétés | Ce que fait le serveur |
| --- | --- | --- |
| `depart` | | Position de départ d'une nouvelle partie (dans `village`) |
| `sortie` | `vers_carte`, `vers_x`, `vers_y` | Marcher sur la case téléporte vers une autre carte (portes, bords de carte) |
| `pnj` | `sprite`, `dialogue` | Parler (interact) renvoie le dialogue. Case bloquée |
| `dresseur` | `sprite`, `dialogue`, `equipe`, `champion` (bool, facultatif) | Parler lance un combat ; une fois battu, il ne relance plus. Battre les 2 champions = arène gagnée |
| `coffre` | `objet` | Donne l'objet **une seule fois** |
| `soin` | `sprite`, `dialogue` | Soigne toute l'équipe |
| `tour_accueil` | `sprite`, `dialogue` | Démarre une tentative du mode roguelite |
| `tour_adversaire` | `sprite`, `dialogue` | Adversaire de l'étage en cours (équipe générée par le serveur) |

- `equipe` : liste `espece:niveau` séparée par des virgules, avec les noms anglais de PokéAPI. Exemple : `rattata:3,pidgey:3`.
- Les panneaux sont des `pnj` (leur `dialogue` est le texte du panneau).
- Les cases des `pnj`, `dresseur`, `soin`, `tour_accueil` et `tour_adversaire` sont déjà marquées dans `collisions`.

## Sprites des personnages

`sprite` = numéro de tuile dans `kenney_roguelike-characters/Spritesheet/roguelikeChar_transparent.png`
(54 colonnes, tuiles de 16 px, 1 px d'espacement) :

```
colonne = sprite % 54     ligne = sprite // 54
x = colonne * 17          y = ligne * 17
```

| Sprite | Utilisé pour |
| --- | --- |
| 271 | Professeure, chercheuse, vieille sage |
| 270 | Maman, marchande, hôtesse |
| 486 | Infirmières |
| 378 | Gamin Paul, gamin de l'étang, fan de la Tour |
| 379 | Fillette Léa, dresseuse Inès, reporter |
| 325 | Guide de la Route 1, scout Hugo, vétéran |
| 324 | Randonneur, campeur Léo |
| 433 | Pêcheur, voisin, ermite, assistant, arbitre |
| 432 | Visiteur, apprenti de l'arène |
| 541 | Voyageur, randonneur Max |
| 540 | Championne Dune |
| 595 | Champion Roc |
| 594 | Ex-champion, adversaire de la Tour |
| **487** | **Libre : conseillé pour le joueur** |

## Tilesets

- Décors : `kenney_roguelike-rpg-pack` (Kenney, licence CC0)
- Personnages : `kenney_roguelike-characters` (Kenney, licence CC0)
- Le chemin de l'image du tileset est relatif au dossier `maps/` : garder la même arborescence dans le dépôt.

## Vérifications faites à la génération

- Chaque sortie mène à une carte qui existe, sur une case libre qui n'est pas elle-même une sortie (pas de boucle).
- Chaque PNJ, dresseur, coffre et sortie est atteignable à pied depuis les entrées de sa carte.
