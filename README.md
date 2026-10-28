# Yboost-B2: a Pokémon web game (RPG + roguelite)

YBOOST B2 project. Explore a top-down world, beat the trainers and the two gym leaders, then finish the game
by winning the 5 hard battles of the Battle Tower (roguelite).

- **Backend**: Python 3.12+, FastAPI, Pydantic. Every game rule runs on the server; runs are kept in memory.
- **Frontend**: Vite, React and strict TypeScript, "Pixel rétro" art direction.
- **Maps**: made with Tiled (`assets/maps/`), Kenney tilesets (CC0).
- **Pokémon data**: imported **once** from PokéAPI into `backend/data/`. The API never calls PokéAPI while playing.

The team's reference (rules, state graph, backlog) is the Notion design doc.

## Architecture

```
backend/
  moteur/                 game rules: pure Python, no FastAPI (tested without a server)
    regles.py             design constants: team size 3, 11 % encounters, 5 Tower battles…
    modeles.py            Pydantic models of the game state (Partie, PokemonEquipe, CombatEnCours…)
    cartes.py             Tiled map loading, O(1) tile lookups
    donnees.py            reference data read once and cached (maps, starters)
    pokemon.py            stats formula, creation of team Pokémon
    exploration.py        moving and changing maps
  api/                    HTTP layer only
    main.py               create_app(): CORS + routers
    routes/               one router per domain: catalogue, parties, exploration, combat
    schemas.py            request/response bodies (contract v2)
    dependances.py        PartieDep / PartieEnExploration…: 404 and 409 checks in one place
    depot.py              in-memory store of the runs
  scripts/
    exporter_openapi.py   writes backend/openapi.json (source of the front-end types)
  data/                   game data as JSON (starters are provisional until the PokéAPI import)
  tests/                  pytest, one file per domain + the mode x route matrix
  openapi.json            generated API contract, committed
frontend/src/
  api/                    client.ts (one function per route), types.ts (aliases of the generated types)
  hooks/                  usePartie (run state and actions), useClavier (keyboard)
  components/             one screen per mode: ChoixStarter, VueCarte + BoiteDialogue, EcranCombat, EcranFin
  sprites.ts              Kenney sprite sheets and Pokémon sprite URLs
assets/
  maps/                   13 maps (.tmx = Tiled work file, .json = export read by the API), see README_cartes.md
  kenney_*/               tilesets
```

Dependencies only go one way: `api` → `moteur`. A rule never imports FastAPI, and a route never contains a rule.

## Running the project

Two terminals: the API on port 8000 and the front-end on port 5173.

### 1. API (Python 3.12 or later)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
uvicorn api.main:app --reload
```

Interactive docs: http://localhost:8000/docs

### 2. Front-end (Node 20 or later)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. Port 5173 is required: it is the only origin allowed by the API's CORS.
To change the API URL, copy `.env.example` to `.env`.

## Checks before every pull request

```bash
cd backend && pytest && ruff check . && ruff format --check .
cd frontend && npm run build && npm run lint
```

`ruff format .` formats the Python code; `ruff check --fix .` fixes most lint errors.

The same checks run on GitHub Actions (`.github/workflows/ci.yml`) for every pull request and push to `dev`
and `main`. A pull request is only merged when the CI is green.

## API types (one contract, two languages)

The TypeScript types are **generated** from the Pydantic models, never written by hand:

1. change a model or a route in `backend/`;
2. `python -m scripts.exporter_openapi` (from `backend/`) rewrites `backend/openapi.json`.
   A test fails as long as this file is out of date;
3. `npm run gen:api` (run automatically by `npm run dev` and `npm run build`) regenerates
   `frontend/src/api/schema.d.ts` (git-ignored). TypeScript then shows every place to update.

## API contract v2

| Route | Required mode | Response |
| --- | --- | --- |
| `GET /starters` | none | the 3 starters with base stats and moves |
| `GET /maps/{map_id}` | none | `sol`/`decor`/`toits` layers and visible objects. 404 if unknown |
| `POST /runs` `{"graine"?}` | none | 201, new run in `choix_starter` mode |
| `GET /runs/{id}` | any | full state of the run. 404 if unknown |
| `POST /runs/{id}/starter` `{"pokemon_id"}` | `choix_starter` | moves to `exploration`. 422 if not a starter |
| `POST /runs/{id}/move` `{"direction"}` | `exploration` | `evenement`: `deplace`, `bloque` or `changement_carte` |
| `POST /runs/{id}/interact` | `exploration` | `evenement` for the tile in front of the player. **501 until task 64** |
| `POST /runs/{id}/battle/actions` `{"type": "attack" \| "switch" \| "item" \| "capture" \| "flee", …}` | `combat` | `partie` + `journal`. **501 until task 20** |

- A route called in the wrong mode returns **409** and changes nothing. Malformed input returns **422**.
  An unknown run or map returns **404**. Every error body is `{"detail": "..."}`.
- A game failure (wall, empty chest, lost battle, failed escape) **is not an HTTP error**: it is a 200 with an `evenement`.
- Every random draw uses the run's `graine` (seed), so a run can be replayed in the tests.

## Game rules decided by the team

They live in `backend/moteur/regles.py`:

- team of **3** Pokémon; **11 %** chance of a wild encounter per step in tall grass;
- wild Pokémon are drawn at random from the imported Pokédex; only the level range depends on the area;
- a Pokémon Center restores HP but **not PP**: use **Ether** / **Max Ether** (Huile / Huile Max);
- speed ties are decided at random;
- the opponent AI gets better as the game goes on: random moves, then the most damaging move, then a Negamax
  search from the [easyAI](https://github.com/Zulko/easyAI) library for the gym leaders and the Tower;
- the game ends (`fin` mode) after the **5th** Battle Tower win.

## Workflow

- `main`: stable version, updated at the end of a milestone only (tag `v0.x`). `dev`: integration branch.
- One branch per Notion task, **created from an up-to-date `dev`**: `feat/…`, `fix/…`, `chore/…`.
- Conventional commits in French: `feat(api): …`, `fix(front): …`, `test(moteur): …`, `chore: …`.
- Pull request to `dev` with the Notion task number, what changes and how to test; reviewed by a teammate
  other than the author. Never push to `dev` or `main` directly, never rewrite their history.
- Every new rule comes with its tests: invariants, mode x route matrix, 404/409/422 cases.
