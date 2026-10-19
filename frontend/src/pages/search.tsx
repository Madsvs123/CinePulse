import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { MovieCard } from '../components/movie-card'
import { Chip, Field, Panel } from '../components/ui'
import { api, unwrap } from '../lib/api'
import type { Genre, Movie, Paginated } from '../lib/types'

export function SearchPage() {
  const [params, setParams] = useSearchParams()
  const [movies, setMovies] = useState<Movie[]>([])
  const [genres, setGenres] = useState<Genre[]>([])
  const [q, setQ] = useState(params.get('q') || '')
  const [genre, setGenre] = useState(params.get('genre') || '')
  const [yearMin, setYearMin] = useState(params.get('year_min') || '1970')
  const [yearMax, setYearMax] = useState(params.get('year_max') || '2026')
  const [ratingMin, setRatingMin] = useState(params.get('rating_min') || '0')
  const [cast, setCast] = useState(params.get('cast') || '')
  const [director, setDirector] = useState(params.get('director') || '')
  const [ordering, setOrdering] = useState(params.get('ordering') || '-popularity')

  const run = (overrides: Partial<Record<'q' | 'genre', string>> = {}) => {
    const query = new URLSearchParams({
      q,
      genre,
      year_min: yearMin,
      year_max: yearMax,
      rating_min: ratingMin,
      cast,
      director,
      ordering,
      ...overrides,
    })
    setParams(query)
    api<Paginated<Movie>>(`/api/movies/catalog/search/?${query.toString()}`).then((data) => setMovies(unwrap(data)))
  }

  useEffect(() => {
    api<{ genres: Genre[] }>('/api/movies/facets/').then((data) => setGenres(data.genres))
    run()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Keep results in sync when the top bar navigates to /search?q=... while already on this page.
  useEffect(() => {
    const next = params.get('q') || ''
    if (next !== q) {
      setQ(next)
      run({ q: next })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params])

  return (
    <div className="cp-split">
      <div>
        <h1 className="cp-display">Discover</h1>
        <div className="cp-grid">
          {movies.map((movie) => (
            <MovieCard key={movie.id} movie={movie} />
          ))}
        </div>
      </div>
      <aside>
        <Panel>
          <h3 className="cp-display">Filters</h3>
          <form
            className="cp-form"
            onSubmit={(event) => {
              event.preventDefault()
              run()
            }}
          >
            <Field label="Search">
              <input className="cp-input" value={q} onChange={(e) => setQ(e.target.value)} />
            </Field>
            <Field label="Cast">
              <input className="cp-input" value={cast} onChange={(e) => setCast(e.target.value)} />
            </Field>
            <Field label="Director">
              <input className="cp-input" value={director} onChange={(e) => setDirector(e.target.value)} />
            </Field>
            <Field label="Year range">
              <div style={{ display: 'flex', gap: 8 }}>
                <input className="cp-input" value={yearMin} onChange={(e) => setYearMin(e.target.value)} />
                <input className="cp-input" value={yearMax} onChange={(e) => setYearMax(e.target.value)} />
              </div>
            </Field>
            <Field label="Minimum rating">
              <input className="cp-input" value={ratingMin} onChange={(e) => setRatingMin(e.target.value)} />
            </Field>
            <Field label="Sort">
              <select className="cp-select" value={ordering} onChange={(e) => setOrdering(e.target.value)}>
                <option value="-popularity">Popularity</option>
                <option value="-vote_average">Rating</option>
                <option value="-release_date">Newest</option>
                <option value="title">Title</option>
              </select>
            </Field>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {genres.map((item) => (
                <Chip key={item.slug} label={item.name} active={genre === item.slug} onClick={() => setGenre(genre === item.slug ? '' : item.slug)} />
              ))}
            </div>
            <button className="cp-btn gold" type="submit">
              Apply
            </button>
          </form>
        </Panel>
      </aside>
    </div>
  )
}
