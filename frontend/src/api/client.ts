/**
 * Typed client of the FastAPI backend. One function per route; the server
 * decides every game rule, the front-end only sends intentions.
 */
import type {
  ActionCombat,
  Carte,
  Direction,
  Partie,
  ReponseCombat,
  ReponseDeplacement,
  ReponseInteraction,
  Starter,
} from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

/** HTTP error returned by the API (`statut` 0 = server unreachable). */
export class ErreurApi extends Error {
  readonly statut: number
  constructor(statut: number, message: string) {
    super(message)
    this.name = 'ErreurApi'
    this.statut = statut
  }
}

async function requete<T>(chemin: string, options: RequestInit = {}): Promise<T> {
  let reponse: Response
  try {
    reponse = await fetch(`${API_URL}${chemin}`, {
      ...options,
      headers: { 'Content-Type': 'application/json', ...options.headers },
    })
  } catch {
    throw new ErreurApi(0, `API injoignable (${API_URL}). Le serveur FastAPI est-il lancé ?`)
  }
  if (!reponse.ok) {
    const corps: unknown = await reponse.json().catch(() => null)
    const detail =
      corps && typeof corps === 'object' && 'detail' in corps && typeof corps.detail === 'string'
        ? corps.detail
        : reponse.statusText
    throw new ErreurApi(reponse.status, detail)
  }
  return reponse.json() as Promise<T>
}

const post = <T>(chemin: string, corps?: unknown) =>
  requete<T>(chemin, { method: 'POST', body: corps === undefined ? undefined : JSON.stringify(corps) })

const run = (id: string) => `/runs/${encodeURIComponent(id)}`

export const api = {
  starters: () => requete<Starter[]>('/starters'),
  carte: (id: string) => requete<Carte>(`/maps/${encodeURIComponent(id)}`),
  creerPartie: () => post<Partie>('/runs', {}),
  lirePartie: (id: string) => requete<Partie>(run(id)),
  choisirStarter: (id: string, pokemonId: number) => post<Partie>(`${run(id)}/starter`, { pokemon_id: pokemonId }),
  deplacer: (id: string, direction: Direction) => post<ReponseDeplacement>(`${run(id)}/move`, { direction }),
  interagir: (id: string) => post<ReponseInteraction>(`${run(id)}/interact`),
  agir: (id: string, action: ActionCombat) => post<ReponseCombat>(`${run(id)}/battle/actions`, action),
}
