# Yboost-B2 : jeu Pokémon web (RPG + roguelite)

Projet YBOOST B2. On explore un monde en vue de dessus, on affronte des dresseurs et deux champions, puis on termine par la Tour de Combat en mode roguelite.

- **Backend** : Python, FastAPI, Pydantic. Les règles du jeu tournent côté serveur et les parties sont gardées en mémoire.
- **Frontend** : Vite, React et TypeScript, en direction artistique « Pixel rétro ».
- **Cartes** : faites avec Tiled (`assets/maps/`), tilesets Kenney (licence CC0).

## Arborescence

```
backend/
  api/          main.py (routes), cartes.py (lecture Tiled), schemas.py (contrat d'API)
  data/         données du jeu en JSON (starters provisoires)
  tests/        tests pytest
frontend/
  src/          App.tsx, api.ts, types.ts, sprites.ts, components/, hooks/
assets/
  maps/         13 cartes (.tmx = fichier de travail, .json = export lu par l'API), voir README_cartes.md
  kenney_*/     tilesets
```

## Lancer le projet

Il faut **deux terminaux** : l'API sur le port 8000 et le front sur le port 5173.

### 1. API (Python 3.11 ou plus récent)

```bash
cd backend
python -m venv .venv
# Windows : .venv\Scripts\activate    macOS/Linux : source .venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

La documentation interactive est sur http://localhost:8000/docs. Pour lancer les tests :

```bash
pytest
```

### 2. Front (Node 20 ou plus récent)

```bash
cd frontend
npm install
npm run dev
```

Ouvrir http://localhost:5173. Le port 5173 est imposé, car c'est la seule origine autorisée par le CORS de l'API.
Pour changer l'adresse de l'API, copier `.env.example` en `.env`.

## Contrat d'API v1 (état actuel)

| Route | Mode requis | Réponse |
| --- | --- | --- |
| `GET /starters` | aucun | les 3 starters |
| `GET /maps/{map_id}` | aucun | calques `sol`/`decor`/`toits` et objets visibles. 404 si la carte est inconnue |
| `POST /runs` | aucun | 201, nouvelle partie en mode `choix_starter` |
| `GET /runs/{id}` | aucun | état de la partie. 404 si elle est inconnue |
| `POST /runs/{id}/starter` `{"pokemon_id"}` | `choix_starter` | passe en `exploration`. 422 si l'id est invalide |
| `POST /runs/{id}/move` `{"direction": "up"\|"down"\|"left"\|"right"}` | `exploration` | `evenement` : `deplace`, `bloque` ou `changement_carte` |

- Appeler une route dans le mauvais mode renvoie **409**. Une entrée mal formée renvoie **422**.
- Un échec de jeu, par exemple foncer dans un mur, **n'est pas une erreur** : la réponse est 200 avec `evenement.type = "bloque"`.

À venir : `POST /runs/{id}/interact`, les rencontres dans les herbes, `POST /runs/{id}/battle/actions`.

## Méthode de travail

- `main` : version stable, mise à jour en fin de jalon uniquement.
- `dev` : branche d'intégration.
- `feat/…`, `fix/…`, `chore/…` : une branche par tâche du backlog Notion, **créée depuis `dev`**, avec une PR vers `dev` relue par un camarade.
- Messages de commit au format conventionnel : `feat(api): …`, `fix(front): …`, `chore: …`.
- Avant d'ouvrir une PR : `pytest` passe, ainsi que `npm run build` et `npm run lint`.
