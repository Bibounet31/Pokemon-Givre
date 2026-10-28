// Découpage des feuilles de sprites Kenney (tuiles 16 px, 1 px d'espacement).
import urlDecor from '../../assets/kenney_roguelike-rpg-pack/Spritesheet/roguelikeSheet_transparent.png'
import urlPersos from '../../assets/kenney_roguelike-characters/Spritesheet/roguelikeChar_transparent.png'

export const TUILE = 16
const PAS = 17 // 16 px + 1 px d'espacement
const COLONNES_DECOR = 57
const COLONNES_PERSOS = 54

/** Sprite du joueur dans roguelikeChar (voir assets/maps/README_cartes.md). */
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
export function chargerFeuilles(): Promise<Feuilles> {
  cache ??= Promise.all([chargerImage(urlDecor), chargerImage(urlPersos)]).then(([decor, persos]) => ({
    decor,
    persos,
  }))
  return cache
}

/** gid Tiled (1-based, 0 = vide) → coin haut-gauche dans roguelikeSheet. */
export function sourceDecor(gid: number): [number, number] {
  const i = gid - 1
  return [(i % COLONNES_DECOR) * PAS, Math.floor(i / COLONNES_DECOR) * PAS]
}

/** index de sprite (0-based) → coin haut-gauche dans roguelikeChar. */
export function sourcePerso(index: number): [number, number] {
  return [(index % COLONNES_PERSOS) * PAS, Math.floor(index / COLONNES_PERSOS) * PAS]
}
