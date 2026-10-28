import { useEffect, useRef } from 'react'
import type { Direction } from '../api/types'

// Arrows + ZQSD (AZERTY) + WASD (QWERTY)
const DIRECTIONS: Record<string, Direction> = {
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
const TOUCHES_VALIDER = new Set([' ', 'Enter'])

interface Actions {
  surDirection: (direction: Direction) => void
  /** Space or Enter: talk / interact with the tile in front of the player. */
  surValider: () => void
}

/** Keyboard controls of the map. A held arrow key repeats (browser key repeat). */
export function useClavier(actions: Actions, actif: boolean) {
  const rappels = useRef(actions)
  useEffect(() => {
    rappels.current = actions
  })

  useEffect(() => {
    if (!actif) return
    const ecouter = (e: KeyboardEvent) => {
      if (TOUCHES_VALIDER.has(e.key)) {
        // Let Space/Enter activate a focused button normally.
        if (e.repeat || e.target instanceof HTMLButtonElement) return
        e.preventDefault()
        rappels.current.surValider()
        return
      }
      const direction = DIRECTIONS[e.key.length === 1 ? e.key.toLowerCase() : e.key]
      if (!direction) return
      e.preventDefault()
      rappels.current.surDirection(direction)
    }
    window.addEventListener('keydown', ecouter)
    return () => window.removeEventListener('keydown', ecouter)
  }, [actif])
}
