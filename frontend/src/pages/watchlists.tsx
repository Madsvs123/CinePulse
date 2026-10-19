import { useEffect, useState } from 'react'
import { MovieCard } from '../components/movie-card'
import { Button, Field, Panel } from '../components/ui'
import { api, unwrap } from '../lib/api'
import type { Movie } from '../lib/types'

interface Watchlist {
  id: string
  name: string
  description: string
  is_public: boolean
  items: { movie: Movie; note: string }[]
}

export function WatchlistsPage() {
  const [lists, setLists] = useState<Watchlist[]>([])
  const [library, setLibrary] = useState<{ bookmarks: Movie[]; history: { movie: Movie; completed: boolean }[] } | null>(null)
  const [name, setName] = useState('Late night queue')

  const load = () => {
    api<{ results: Watchlist[] } | Watchlist[]>('/api/movies/watchlists/').then((data) => setLists(unwrap(data)))
    api<{ bookmarks: Movie[]; history: { movie: Movie; completed: boolean }[] }>('/api/movies/library/').then(setLibrary)
  }

  useEffect(load, [])

  return (
    <div>
      <h1 className="cp-display">Watchlists & history</h1>
      <Panel>
        <form
          className="cp-form"
          onSubmit={async (event) => {
            event.preventDefault()
            await api('/api/movies/watchlists/', { method: 'POST', body: JSON.stringify({ name, is_public: false }) })
            setName('')
            load()
          }}
        >
          <Field label="New watchlist">
            <input className="cp-input" value={name} onChange={(e) => setName(e.target.value)} />
          </Field>
          <Button type="submit">Create</Button>
        </form>
      </Panel>
      {lists.map((list) => (
        <section key={list.id} className="cp-section">
          <h2>{list.name}</h2>
          <p className="cp-muted">{list.description || 'A private stack of titles to return to.'}</p>
          <div className="cp-row">
            {list.items.map((item) => (
              <MovieCard key={item.movie.id} movie={item.movie} />
            ))}
          </div>
        </section>
      ))}
      <section className="cp-section">
        <h2>Bookmarks</h2>
        <div className="cp-row">
          {library?.bookmarks.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      </section>
      <section className="cp-section">
        <h2>Watch history</h2>
        <div className="cp-row">
          {library?.history.map((row) => (
            <MovieCard key={row.movie.id} movie={row.movie} reasons={[row.completed ? 'Completed' : 'In progress']} />
          ))}
        </div>
      </section>
    </div>
  )
}
