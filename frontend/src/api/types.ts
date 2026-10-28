/**
 * API types, generated from the backend's OpenAPI schema (`backend/openapi.json`).
 *
 * Never write them by hand: change the Pydantic model, export the schema
 * (`python -m scripts.exporter_openapi` in backend/), then `npm run gen:api`
 * (also run automatically before `npm run dev` and `npm run build`).
 */
import type { components } from './schema'

type Schemas = components['schemas']

export type Mode = Schemas['Mode']
export type Partie = Schemas['Partie']
export type Position = Schemas['Position']
export type Direction = Position['orientation']
export type Starter = Schemas['Starter']
export type PokemonEquipe = Schemas['PokemonEquipe']
export type Carte = Schemas['CarteReponse']
export type ObjetCarte = Schemas['ObjetVisible']
export type Evenement = Schemas['Evenement']
export type ReponseDeplacement = Schemas['ReponseDeplacement']
export type ReponseInteraction = Schemas['ReponseInteraction']
export type ReponseCombat = Schemas['ReponseCombat']
export type EntreeJournal = Schemas['EntreeJournal']
export type ActionCombat =
  | Schemas['ActionAttaquer']
  | Schemas['ActionChanger']
  | Schemas['ActionObjet']
  | Schemas['ActionCapturer']
  | Schemas['ActionFuir']
