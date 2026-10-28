import { BoiteDialogue } from './components/BoiteDialogue'
import { ChoixStarter } from './components/ChoixStarter'
import { EcranCombat } from './components/EcranCombat'
import { EcranFin } from './components/EcranFin'
import { VueCarte } from './components/VueCarte'
import { useClavier } from './hooks/useClavier'
import { usePartie } from './hooks/usePartie'

/** Layout of the game: one screen per run mode, chosen from the state sent by the server. */
export default function App() {
  const jeu = usePartie()
  const { partie, carte } = jeu

  useClavier({ surDirection: jeu.deplacer, surValider: jeu.interagir }, partie?.mode === 'exploration')

  const ecran = () => {
    if (!partie) {
      return (
        <section className="boite titre">
          <p>Une aventure en mode Pixel rétro.</p>
          <button className="bouton" onClick={jeu.nouvellePartie}>
            Nouvelle partie
          </button>
        </section>
      )
    }
    switch (partie.mode) {
      case 'choix_starter':
        return <ChoixStarter starters={jeu.starters} onChoix={jeu.choisirStarter} />
      case 'exploration':
        // Wait for the new map after a map change, so the player is never drawn on the old one.
        if (!carte || carte.id !== partie.position.carte) return null
        return (
          <>
            <div className="cadre-ecran">
              <div className="nom-zone">{carte.titre}</div>
              <VueCarte carte={carte} joueur={partie.position} />
            </div>
            <BoiteDialogue texte={jeu.message} />
          </>
        )
      case 'combat':
        return <EcranCombat partie={partie} journal={jeu.journal} onAction={jeu.agir} />
      case 'fin':
        return <EcranFin onRejouer={jeu.nouvellePartie} />
    }
  }

  return (
    <main className="jeu">
      <header>
        <h1>Yboost Pokémon</h1>
        {partie && (
          <button className="bouton petit" onClick={jeu.nouvellePartie}>
            Nouvelle partie
          </button>
        )}
      </header>

      {jeu.erreur && (
        <p className="erreur" role="alert">
          {jeu.erreur}
        </p>
      )}

      {ecran()}
    </main>
  )
}
