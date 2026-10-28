import { useCallback, useEffect, useRef, useState } from 'react'
import { api, ErreurApi } from './api'
import { ChoixStarter } from './components/ChoixStarter'
import { VueCarte } from './components/VueCarte'
import { useClavier } from './hooks/useClavier'
import type { Carte, Direction, Partie, Starter } from './types'

const CLE_PARTIE = 'yboost.partie'

function lireIdSauvegarde(): string | null {
  try {
    return localStorage.getItem(CLE_PARTIE)
  } catch {
    return null
  }
}
function sauverId(id: string | null) {
  try {
    if (id) localStorage.setItem(CLE_PARTIE, id)
    else localStorage.removeItem(CLE_PARTIE)
  } catch {
    /* stockage indisponible : on ne reprendra pas la partie, ce n'est pas grave */
  }
}

export default function App() {
  const [partie, setPartie] = useState<Partie | null>(null)
  const [starters, setStarters] = useState<Starter[]>([])
  const [carte, setCarte] = useState<Carte | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [erreur, setErreur] = useState<string | null>(null)
  const enCours = useRef(false)

  const signaler = (e: unknown) => setErreur(e instanceof Error ? e.message : String(e))

  // Reprise d'une partie existante (le serveur garde les parties en mémoire tant qu'il tourne).
  useEffect(() => {
    const id = lireIdSauvegarde()
    if (!id) return
    api.lirePartie(id).then(setPartie, (e) => {
      if (e instanceof ErreurApi && e.statut === 404) sauverId(null)
      else signaler(e)
    })
  }, [])

  useEffect(() => {
    if (partie?.mode === 'choix_starter' && starters.length === 0) api.starters().then(setStarters, signaler)
  }, [partie?.mode, starters.length])

  const idCarte = partie?.position.carte
  useEffect(() => {
    if (!idCarte) return
    api.carte(idCarte).then(setCarte, signaler)
  }, [idCarte])

  const nouvellePartie = async () => {
    setErreur(null)
    try {
      const p = await api.creerPartie()
      sauverId(p.id)
      setCarte(null)
      setPartie(p)
    } catch (e) {
      signaler(e)
    }
  }

  const choisir = async (pokemonId: number) => {
    if (!partie) return
    try {
      const p = await api.choisirStarter(partie.id, pokemonId)
      setPartie(p)
      setMessage(`${p.equipe[0].nom_fr} rejoint ton équipe !`)
    } catch (e) {
      signaler(e)
    }
  }

  const deplacer = useCallback(
    async (direction: Direction) => {
      if (!partie || enCours.current) return // un seul déplacement à la fois
      enCours.current = true
      try {
        const r = await api.deplacer(partie.id, direction)
        setPartie(r.partie)
        if (r.evenement.type === 'changement_carte') setMessage(null)
        else if (r.dans_les_herbes) setMessage('Les herbes bruissent…')
        else setMessage(null)
      } catch (e) {
        signaler(e)
      } finally {
        enCours.current = false
      }
    },
    [partie],
  )

  useClavier(deplacer, partie?.mode === 'exploration')

  return (
    <main className="jeu">
      <header>
        <h1>Yboost Pokémon</h1>
        {partie && (
          <button className="bouton petit" onClick={nouvellePartie}>
            Nouvelle partie
          </button>
        )}
      </header>

      {erreur && (
        <p className="erreur" role="alert">
          {erreur}
        </p>
      )}

      {!partie && (
        <section className="boite titre">
          <p>Une aventure en mode Pixel rétro.</p>
          <button className="bouton" onClick={nouvellePartie}>
            Nouvelle partie
          </button>
        </section>
      )}

      {partie?.mode === 'choix_starter' && <ChoixStarter starters={starters} onChoix={choisir} />}

      {partie?.mode === 'exploration' && carte && carte.id === partie.position.carte && (
        <>
          <div className="cadre-ecran">
            <div className="nom-zone">{carte.titre}</div>
            <VueCarte carte={carte} joueur={partie.position} />
          </div>
          <div className="boite dialogue">
            {message ?? 'Flèches ou ZQSD pour te déplacer.'}
          </div>
        </>
      )}
    </main>
  )
}
