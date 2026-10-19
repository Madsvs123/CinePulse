import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { RecoRow } from '../components/movie-row'
import { Button, Chip, Panel, Spoiler } from '../components/ui'
import { api } from '../lib/api'
import type { Movie, RecoItem, Review } from '../lib/types'

export function MoviePage() {
  const { slug } = useParams()
  const [movie, setMovie] = useState<Movie | null>(null)
  const [similar, setSimilar] = useState<RecoItem[]>([])
  const [reviews, setReviews] = useState<Review[]>([])
  const [score, setScore] = useState(8)
  const [review, setReview] = useState({ title: '', body: '', contains_spoilers: false })

  const load = () => {
    if (!slug) return
    api<Movie>(`/api/movies/catalog/${slug}/`).then(setMovie)
    api<RecoItem[]>(`/api/movies/catalog/${slug}/similar/`).then(setSimilar)
    api<{ results: Review[] }>(`/api/community/reviews/?movie__slug=${slug}`).then((data) => setReviews(data.results || []))
  }

  useEffect(load, [slug])
  if (!movie) return <p>Loading title…</p>

  const act = async (path: string, body?: unknown) => {
    await api(`/api/movies/catalog/${movie.slug}/${path}`, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
    load()
  }

  return (
    <div className="cp-split">
      <div>
        <section className="cp-hero" style={{ backgroundImage: `url(${movie.backdrop_url || movie.poster_url})` }}>
          <div className="cp-hero-copy">
            <p className="cp-kicker">{movie.genres.map((g) => g.name).join(' · ')}</p>
            <h2>{movie.title}</h2>
            <p>
              {movie.year} · {movie.runtime} min · {movie.age_rating} · {movie.vote_average.toFixed(1)}
            </p>
            <p>{movie.description}</p>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 12 }}>
              <Button kind="gold" onClick={() => act('watch/', { progress_seconds: 900, completed: false })}>
                Continue / log watch
              </Button>
              <Button kind="ghost" onClick={() => act('react/', { kind: 'like' })}>
                Like
              </Button>
              <Button kind="ghost" onClick={() => act('react/', { kind: 'dislike' })}>
                Dislike
              </Button>
              <Button kind="ghost" onClick={() => act('bookmark/')}>
                Bookmark
              </Button>
            </div>
          </div>
        </section>
        {movie.trailer_url ? (
          <Panel>
            <h3 className="cp-display">Trailer</h3>
            <iframe title="trailer" src={movie.trailer_url} width="100%" height="360" style={{ border: 0, borderRadius: 16 }} />
          </Panel>
        ) : null}
        <RecoRow title="Similar movies" items={similar} />
        <section className="cp-section">
          <h2>Reviews</h2>
          {reviews.map((item) => (
            <Panel key={item.id}>
              <b>{item.title}</b>
              <p className="cp-muted">
                {item.user.display_name} · {item.score}
              </p>
              <Spoiler text={item.body} flagged={item.contains_spoilers} />
            </Panel>
          ))}
          <Panel>
            <h3>Write a review</h3>
            <form
              className="cp-form"
              onSubmit={async (event) => {
                event.preventDefault()
                await api('/api/community/reviews/', {
                  method: 'POST',
                  body: JSON.stringify({ ...review, score, movie_id: movie.id }),
                })
                setReview({ title: '', body: '', contains_spoilers: false })
                load()
              }}
            >
              <input className="cp-input" placeholder="Title" value={review.title} onChange={(e) => setReview({ ...review, title: e.target.value })} />
              <textarea className="cp-input" rows={4} value={review.body} onChange={(e) => setReview({ ...review, body: e.target.value })} />
              <label>
                <input
                  type="checkbox"
                  checked={review.contains_spoilers}
                  onChange={(e) => setReview({ ...review, contains_spoilers: e.target.checked })}
                />{' '}
                Contains spoilers
              </label>
              <Button type="submit">Publish</Button>
            </form>
          </Panel>
        </section>
      </div>
      <aside>
        <Panel>
          <h3 className="cp-display">Your rating</h3>
          <input type="range" min={0.5} max={10} step={0.5} value={score} onChange={(e) => setScore(Number(e.target.value))} />
          <p>{score.toFixed(1)} / 10</p>
          <Button onClick={() => act('rate/', { score })}>Save rating</Button>
        </Panel>
        <Panel>
          <h3 className="cp-display">Credits</h3>
          <p>
            <b>Directors</b> {movie.directors?.map((d) => d.name).join(', ') || '—'}
          </p>
          <p>
            <b>Cast</b> {movie.cast?.map((c) => `${c.name} as ${c.character}`).join(', ') || '—'}
          </p>
          <p>
            <b>Languages</b> {movie.languages?.map((l) => l.name).join(', ')}
          </p>
          <p>
            <b>Companies</b> {movie.companies?.map((c) => c.name).join(', ')}
          </p>
        </Panel>
        <Panel>
          <h3 className="cp-display">Streaming</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {movie.availability?.length ? (
              movie.availability.map((row) => (
                <Chip key={row.provider.name} label={`${row.provider.name} · ${row.offer_type}`} />
              ))
            ) : (
              <p className="cp-muted">No offers yet</p>
            )}
          </div>
        </Panel>
      </aside>
    </div>
  )
}
