import { useEffect, useRef } from 'react'
import type { Direction } from '../types'

// Flèches + ZQSD (AZERTY) + WASD (QWERTY)
const TOUCHES: Record<string, Direction> = {
  ArrowUp: 'up',
  ArrowDown: 'down',
  ArrowLeft: 'left',
  ArrowRight: 'right',
  z: 'up',
  w: 'up',
  s: 'down',
  q: 'left',
  a: 'left',
  d: 'right',
}

/** Appelle `surDirection` à chaque appui (touche maintenue = répétition du navigateur). */
export function useClavier(surDirection: (d: Direction) => void, actif: boolean) {
  const rappel = useRef(surDirection)
  useEffect(() => {
    rappel.current = surDirection
  })

  useEffect(() => {
    if (!actif) return
    const ecoute = (e: KeyboardEvent) => {
      const direction = TOUCHES[e.key.length === 1 ? e.key.toLowerCase() : e.key]
      if (!direction) return
      e.preventDefault()
      rappel.current(direction)
    }
    window.addEventListener('keydown', ecoute)
    return () => window.removeEventListener('keydown', ecoute)
  }, [actif])
}
