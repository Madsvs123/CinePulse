import type { Movie, RecoItem } from '../lib/types'
import { MovieCard, RecoCard } from './movie-card'

export function MovieRow({ title, movies }: { title: string; movies: Movie[] }) {
  if (!movies.length) return null
  return (
    <section className="cp-section">
      <h2>{title}</h2>
      <div className="cp-row">
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} />
        ))}
      </div>
    </section>
  )
}

export function RecoRow({ title, items }: { title: string; items: RecoItem[] }) {
  if (!items.length) return null
  return (
    <section className="cp-section">
      <h2>{title}</h2>
      <div className="cp-row">
        {items.map((item) => (
          <RecoCard key={item.movie.id} item={item} />
        ))}
      </div>
    </section>
  )
}
