import type { Starter } from '../types'

interface Props {
  starters: Starter[]
  onChoix: (id: number) => void
}

const URL_SPRITE = (id: number) =>
  `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`

export function ChoixStarter({ starters, onChoix }: Props) {
  return (
    <section className="boite">
      <h2>Choisis ton partenaire</h2>
      <div className="starters">
        {starters.map((s) => (
          <button key={s.id} className="carte-starter" onClick={() => onChoix(s.id)}>
            <img src={URL_SPRITE(s.id)} alt="" width={96} height={96} />
            <span className="nom">{s.nom_fr}</span>
            <span className="types">{s.types.join(' / ')}</span>
          </button>
        ))}
      </div>
    </section>
  )
}
