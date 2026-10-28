interface Props {
  texte: string | null
  /** Shown when there is nothing to say. */
  aide?: string
}

/**
 * Dialogue box under the map. `aria-live` makes screen readers announce new lines.
 * Multi-line dialogues advanced with Enter come with Notion task 68.
 */
export function BoiteDialogue({ texte, aide = 'Flèches ou ZQSD pour te déplacer, Espace pour parler.' }: Props) {
  return (
    <div className="boite dialogue" aria-live="polite">
      {texte ?? aide}
    </div>
  )
}
