// Slicing of the Kenney sprite sheets (16 px tiles, 1 px spacing) and Pokémon sprite URLs.
import urlDecor from '../../assets/kenney_roguelike-rpg-pack/Spritesheet/roguelikeSheet_transparent.png'
import urlPersos from '../../assets/kenney_roguelike-characters/Spritesheet/roguelikeChar_transparent.png'

export const TUILE = 16
const PAS = 17 // 16 px + 1 px spacing
const COLONNES_DECOR = 57
const COLONNES_PERSOS = 54

/** Player sprite in roguelikeChar (see assets/maps/README_cartes.md). */
export const SPRITE_JOUEUR = 487

function chargerImage(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(img)
    img.onerror = () => reject(new Error(`Image introuvable : ${url}`))
    img.src = url
  })
}

export interface Feuilles {
  decor: HTMLImageElement
  persos: HTMLImageElement
}

let cache: Promise<Feuilles> | null = null

/** Load both sprite sheets once; later calls reuse the same promise. */
export function chargerFeuilles(): Promise<Feuilles> {
  cache ??= Promise.all([chargerImage(urlDecor), chargerImage(urlPersos)]).then(([decor, persos]) => ({
    decor,
    persos,
  }))
  return cache
}

/** Tiled gid (1-based, 0 = empty) → top-left corner in roguelikeSheet. */
export function sourceDecor(gid: number): [number, number] {
  const i = gid - 1
  return [(i % COLONNES_DECOR) * PAS, Math.floor(i / COLONNES_DECOR) * PAS]
}

/** Sprite index (0-based) → top-left corner in roguelikeChar. */
export function sourcePerso(index: number): [number, number] {
  return [(index % COLONNES_PERSOS) * PAS, Math.floor(index / COLONNES_PERSOS) * PAS]
}

const SPRITES_POKEMON = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon'

/** Front (or back, for the player's side in battle) sprite of a Pokémon. Local once task 10 downloads them. */
export function urlSpritePokemon(id: number, dos = false): string {
  return `${SPRITES_POKEMON}/${dos ? 'back/' : ''}${id}.png`
}
