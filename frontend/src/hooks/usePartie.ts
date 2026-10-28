import { useCallback, useEffect, useRef, useState } from 'react'
import { api, ErreurApi } from '../api/client'
import type { ActionCombat, Carte, Direction, EntreeJournal, Evenement, Partie, Starter } from '../api/types'

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
    /* storage unavailable: the run just won't be resumed after a reload */
  }
}

/** Text shown in the dialogue box after an exploration event (null = keep the help text). */
function texteEvenement(evenement: Evenement, dansLesHerbes = false): string | null {
  if (evenement.texte) return evenement.texte
  switch (evenement.type) {
    case 'deplace':
      return dansLesHerbes ? 'Les herbes bruissent…' : null
    case 'objet_obtenu':
      return `Tu obtiens : ${evenement.objet ?? 'un objet'} !`
    case 'coffre_vide':
      return 'Le coffre est vide.'
    case 'soin':
      return 'Ton équipe est en pleine forme !'
    default:
      return null
  }
}

/**
 * State of the current run and every action the player can send.
 * Only one request is in flight at a time: holding a key does not queue moves.
 */
export function usePartie() {
  const [partie, setPartie] = useState<Partie | null>(null)
  const [starters, setStarters] = useState<Starter[]>([])
  const [carte, setCarte] = useState<Carte | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [journal, setJournal] = useState<EntreeJournal[]>([])
  const [erreur, setErreur] = useState<string | null>(null)
  const enCours = useRef(false)

  const signaler = useCallback((e: unknown) => {
    // 501 = route of the contract not implemented yet: not a bug, just tell the player.
    if (e instanceof ErreurApi && e.statut === 501) setMessage(e.message)
    else setErreur(e instanceof Error ? e.message : String(e))
  }, [])

  /** Send one request, ignoring the call if another one is still running. */
  const executer = useCallback(
    async <T>(requete: () => Promise<T>, apres: (resultat: T) => void) => {
      if (enCours.current) return
      enCours.current = true
      try {
        apres(await requete())
      } catch (e) {
        signaler(e)
      } finally {
        enCours.current = false
      }
    },
    [signaler],
  )

  // Resume the saved run (the server keeps runs in memory while it is running).
  useEffect(() => {
    const id = lireIdSauvegarde()
    if (!id) return
    api.lirePartie(id).then(setPartie, (e: unknown) => {
      if (e instanceof ErreurApi && e.statut === 404) sauverId(null)
      else signaler(e)
    })
  }, [signaler])

  const mode = partie?.mode
  useEffect(() => {
    if (mode === 'choix_starter' && starters.length === 0) api.starters().then(setStarters, signaler)
  }, [mode, starters.length, signaler])

  const idCarte = partie?.position.carte
  useEffect(() => {
    if (idCarte) api.carte(idCarte).then(setCarte, signaler)
  }, [idCarte, signaler])

  const id = partie?.id

  const nouvellePartie = useCallback(() => {
    setErreur(null)
    void executer(api.creerPartie, (p) => {
      sauverId(p.id)
      setCarte(null)
      setMessage(null)
      setJournal([])
      setPartie(p)
    })
  }, [executer])

  const choisirStarter = useCallback(
    (pokemonId: number) => {
      if (!id) return
      void executer(
        () => api.choisirStarter(id, pokemonId),
        (p) => {
          setPartie(p)
          setMessage(`${p.equipe[0].nom_fr} rejoint ton équipe !`)
        },
      )
    },
    [id, executer],
  )

  const deplacer = useCallback(
    (direction: Direction) => {
      if (!id) return
      void executer(
        () => api.deplacer(id, direction),
        (r) => {
          setPartie(r.partie)
          setMessage(texteEvenement(r.evenement, r.dans_les_herbes))
        },
      )
    },
    [id, executer],
  )

  const interagir = useCallback(() => {
    if (!id) return
    void executer(
      () => api.interagir(id),
      (r) => {
        setPartie(r.partie)
        setMessage(texteEvenement(r.evenement))
        if (r.partie.mode === 'combat') setJournal([])
      },
    )
  }, [id, executer])

  const agir = useCallback(
    (action: ActionCombat) => {
      if (!id) return
      void executer(
        () => api.agir(id, action),
        (r) => {
          setPartie(r.partie)
          setJournal((avant) => [...avant, ...r.journal])
        },
      )
    },
    [id, executer],
  )

  return { partie, starters, carte, message, journal, erreur, nouvellePartie, choisirStarter, deplacer, interagir, agir }
}
