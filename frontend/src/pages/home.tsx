import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { MovieRow, RecoRow } from '../components/movie-row'
import { Button } from '../components/ui'
import { api } from '../lib/api'
import type { HomeFeed } from '../lib/types'

export function HomePage() {
  const [feed, setFeed] = useState<HomeFeed | null>(null)

  useEffect(() => {
    api<HomeFeed>('/api/recommendations/home/').then(setFeed)
  }, [])

  if (!feed) return <p>Loading your screening room…</p>
  const hero = feed.top_picks[0]?.movie || feed.trending[0]

  return (
    <div>
      {hero ? (
        <section className="cp-hero" style={{ backgroundImage: `url(${hero.backdrop_url || hero.poster_url})` }}>
          <div className="cp-hero-copy">
            <p className="cp-kicker">Tonight’s opening</p>
            <h2>{hero.title}</h2>
            <p>{hero.tagline || hero.description}</p>
            <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
              <Link to={`/movies/${hero.slug}`}>
                <Button kind="gold">Open details</Button>
              </Link>
              <Link to="/recommendations">
                <Button kind="ghost">See why we picked this</Button>
              </Link>
            </div>
          </div>
        </section>
      ) : null}

      <MovieRow title="Continue watching" movies={feed.continue_watching} />
      <RecoRow title="Top picks for you" items={feed.top_picks} />
      <RecoRow
        title={
          feed.because_you_watched.seed
            ? `Because you watched ${feed.because_you_watched.seed.title}`
            : 'Because you watched'
        }
        items={feed.because_you_watched.items}
      />
      <MovieRow title="Trending" movies={feed.trending} />
      <MovieRow title="New releases" movies={feed.new_releases} />
      <RecoRow title="Hidden gems" items={feed.hidden_gems} />
      {feed.genre_collections.map((row) => (
        <MovieRow key={row.genre.id} title={`${row.genre.name} collection`} movies={row.movies} />
      ))}
    </div>
  )
}
