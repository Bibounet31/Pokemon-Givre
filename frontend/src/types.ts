// Types du contrat d'API v1 (miroir de backend/api/schemas.py)

export type Mode = 'choix_starter' | 'exploration' | 'combat' | 'fin'
export type Direction = 'up' | 'down' | 'left' | 'right'

export interface Starter {
  id: number
  nom: string
  nom_fr: string
  types: string[]
  niveau: number
}

export interface PokemonEquipe {
  id: number
  nom: string
  nom_fr: string
  niveau: number
}

export interface Position {
  carte: string
  x: number
  y: number
  orientation: Direction
}

export interface Partie {
  id: string
  mode: Mode
  graine: number
  position: Position
  equipe: PokemonEquipe[]
}

export interface Evenement {
  type: 'deplace' | 'bloque' | 'changement_carte'
  carte: string | null
}

export interface ReponseDeplacement {
  partie: Partie
  evenement: Evenement
  dans_les_herbes: boolean
}

export interface ObjetCarte {
  nom: string
  type: string
  x: number
  y: number
  largeur: number
  hauteur: number
  proprietes: Record<string, string | number | boolean>
}

export interface Carte {
  id: string
  titre: string
  largeur: number
  hauteur: number
  taille_tuile: number
  calques: Record<'sol' | 'decor' | 'toits', number[]>
  objets: ObjetCarte[]
}
