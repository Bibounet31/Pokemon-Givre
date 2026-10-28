import type { Carte, Direction, Partie, ReponseDeplacement, Starter } from './types'

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export class ErreurApi extends Error {
  statut: number
  constructor(statut: number, message: string) {
    super(message)
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
    const corps = await reponse.json().catch(() => ({}))
    const detail = typeof corps.detail === 'string' ? corps.detail : reponse.statusText
    throw new ErreurApi(reponse.status, detail)
  }
  return reponse.json() as Promise<T>
}

const post = <T>(chemin: string, corps?: unknown) =>
  requete<T>(chemin, { method: 'POST', body: corps === undefined ? undefined : JSON.stringify(corps) })

export const api = {
  starters: () => requete<Starter[]>('/starters'),
  carte: (id: string) => requete<Carte>(`/maps/${encodeURIComponent(id)}`),
  creerPartie: () => post<Partie>('/runs', {}),
  lirePartie: (id: string) => requete<Partie>(`/runs/${id}`),
  choisirStarter: (id: string, pokemonId: number) =>
    post<Partie>(`/runs/${id}/starter`, { pokemon_id: pokemonId }),
  deplacer: (id: string, direction: Direction) =>
    post<ReponseDeplacement>(`/runs/${id}/move`, { direction }),
}
