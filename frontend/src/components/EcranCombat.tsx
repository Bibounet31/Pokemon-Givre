import type { ActionCombat, EntreeJournal, Partie, PokemonEquipe } from '../api/types'
import { urlSpritePokemon } from '../sprites'

interface Props {
  partie: Partie
  journal: EntreeJournal[]
  onAction: (action: ActionCombat) => void
}

function BoitePokemon({ pokemon, dos = false }: { pokemon: PokemonEquipe; dos?: boolean }) {
  const pvMax = pokemon.stats.pv
  return (
    <div className="boite boite-pokemon">
      <img src={urlSpritePokemon(pokemon.id, dos)} alt="" width={96} height={96} />
      <div>
        <p className="nom">
          {pokemon.nom_fr} <span>N.{pokemon.niveau}</span>
        </p>
        <meter className="barre-pv" min={0} max={pvMax} low={pvMax / 4} high={pvMax / 2} optimum={pvMax} value={pokemon.pv}>
          {pokemon.pv} / {pvMax} PV
        </meter>
        <p className="pv">
          PV {pokemon.pv} / {pvMax}
        </p>
      </div>
    </div>
  )
}

/**
 * Battle screen skeleton (mode `combat`): HP boxes, 2×2 move grid and battle log.
 * Every rule is resolved by the server; this screen only sends the chosen action.
 * Finished by Notion tasks 63 and 36.
 */
export function EcranCombat({ partie, journal, onAction }: Props) {
  const combat = partie.combat
  if (!combat) return null
  const joueur = partie.equipe[combat.actif]
  const adversaire = combat.adversaires[combat.actif_adverse]

  return (
    <section className="combat">
      <BoitePokemon pokemon={adversaire} />
      <BoitePokemon pokemon={joueur} dos />

      <div className="boite">
        <div className="attaques">
          {joueur.attaques.map((a) => (
            <button
              key={a.id}
              className="bouton"
              disabled={a.pp === 0 || joueur.ko}
              onClick={() => onAction({ type: 'attack', move_id: a.id })}
            >
              {a.id} <small>{a.pp}/{a.pp_max}</small>
            </button>
          ))}
        </div>
        {combat.genre === 'sauvage' && (
          <button className="bouton petit" onClick={() => onAction({ type: 'flee' })}>
            Fuir
          </button>
        )}
      </div>

      <ol className="boite journal" aria-live="polite">
        {journal.length === 0 ? <li>Que doit faire {joueur.nom_fr} ?</li> : journal.map((e, i) => <li key={i}>{e.texte}</li>)}
      </ol>
    </section>
  )
}
