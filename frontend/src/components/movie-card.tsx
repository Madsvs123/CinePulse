import { Link } from 'react-router-dom'
import type { Movie, RecoItem } from '../lib/types'

export function MovieCard({ movie, reasons }: { movie: Movie; reasons?: string[] }) {
  return (
    <Link to={`/movies/${movie.slug}`} className="cp-movie">
      <div className="cp-poster">
        {movie.poster_url ? <img src={movie.poster_url} alt={movie.title} /> : null}
        <span className="badge">{movie.vote_average.toFixed(1)}</span>
      </div>
      <h3>{movie.title}</h3>
      <p>
        {movie.year || '—'} · {movie.genres?.[0]?.name || movie.age_rating}
      </p>
      {reasons?.length ? <p>{reasons[0]}</p> : null}
    </Link>
  )
}

export function RecoCard({ item }: { item: RecoItem }) {
  return <MovieCard movie={item.movie} reasons={item.reasons} />
}
