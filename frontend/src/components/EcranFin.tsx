interface Props {
  onRejouer: () => void
}

/** End screen (mode `fin`): shown after the 5th Battle Tower win. Finished by Notion task 38. */
export function EcranFin({ onRejouer }: Props) {
  return (
    <section className="boite titre">
      <h2>Tour de Combat vaincue !</h2>
      <p>Tu as remporté les 5 combats de la Tour. Bravo, champion !</p>
      <button className="bouton" onClick={onRejouer}>
        Rejouer
      </button>
    </section>
  )
}
