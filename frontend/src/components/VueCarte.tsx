import { useEffect, useRef, useState } from 'react'
import { chargerFeuilles, sourceDecor, sourcePerso, SPRITE_JOUEUR, TUILE, type Feuilles } from '../sprites'
import type { Carte, Position } from '../types'

// Fenêtre de vue façon Game Boy : 15 × 11 cases, agrandies ×3.
const VUE_L = 15
const VUE_H = 11
const ECHELLE = 3

interface Props {
  carte: Carte
  joueur: Position
}

export function VueCarte({ carte, joueur }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [feuilles, setFeuilles] = useState<Feuilles | null>(null)
  const [erreur, setErreur] = useState<string | null>(null)

  useEffect(() => {
    chargerFeuilles().then(setFeuilles, (e: Error) => setErreur(e.message))
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx || !feuilles) return
    ctx.imageSmoothingEnabled = false
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.fillStyle = '#0F380F'
    ctx.fillRect(0, 0, canvas.width, canvas.height)

    // Caméra centrée sur le joueur, bloquée aux bords ; carte centrée si plus petite que la vue.
    const camera = (pos: number, taille: number, vue: number) =>
      taille <= vue ? -(vue - taille) / 2 : Math.min(Math.max(pos - Math.floor(vue / 2), 0), taille - vue)
    const cx = camera(joueur.x, carte.largeur, VUE_L)
    const cy = camera(joueur.y, carte.hauteur, VUE_H)
    ctx.setTransform(ECHELLE, 0, 0, ECHELLE, -cx * TUILE * ECHELLE, -cy * TUILE * ECHELLE)

    const dessinerCalque = (data: number[]) => {
      data.forEach((gid, i) => {
        if (!gid) return
        const [sx, sy] = sourceDecor(gid)
        const x = (i % carte.largeur) * TUILE
        const y = Math.floor(i / carte.largeur) * TUILE
        ctx.drawImage(feuilles.decor, sx, sy, TUILE, TUILE, x, y, TUILE, TUILE)
      })
    }
    const dessinerPerso = (sprite: number, x: number, y: number) => {
      const [sx, sy] = sourcePerso(sprite)
      ctx.drawImage(feuilles.persos, sx, sy, TUILE, TUILE, x * TUILE, y * TUILE, TUILE, TUILE)
    }

    dessinerCalque(carte.calques.sol)
    dessinerCalque(carte.calques.decor)
    for (const o of carte.objets) {
      if (typeof o.proprietes.sprite === 'number') dessinerPerso(o.proprietes.sprite, o.x, o.y)
    }
    dessinerPerso(SPRITE_JOUEUR, joueur.x, joueur.y)
    dessinerCalque(carte.calques.toits) // les toits passent par-dessus le joueur
  }, [carte, joueur, feuilles])

  if (erreur) return <p className="erreur">{erreur}</p>
  return (
    <canvas
      ref={canvasRef}
      className="ecran-jeu"
      width={VUE_L * TUILE * ECHELLE}
      height={VUE_H * TUILE * ECHELLE}
      aria-label={`Carte : ${carte.titre}`}
    />
  )
}
