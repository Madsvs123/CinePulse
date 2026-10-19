import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button, Panel, Spoiler } from '../components/ui'
import { api, unwrap } from '../lib/api'
import type { Review } from '../lib/types'

export function ReviewsPage() {
  const [reviews, setReviews] = useState<Review[]>([])

  const load = () => {
    api<{ results: Review[] } | Review[]>('/api/community/reviews/').then((data) => setReviews(unwrap(data)))
  }

  useEffect(load, [])

  return (
    <div>
      <h1 className="cp-display">Community reviews</h1>
      <div className="cp-form">
        {reviews.map((review) => (
          <Panel key={review.id}>
            <p className="cp-kicker">{review.movie.title}</p>
            <h3>{review.title}</h3>
            <p className="cp-muted">
              {review.user.display_name} · {review.score} · {review.helpful_count} found this helpful
            </p>
            <Spoiler text={review.body} flagged={review.contains_spoilers} />
            <div style={{ display: 'flex', gap: 8 }}>
              <Button
                kind="ghost"
                onClick={async () => {
                  await api(`/api/community/reviews/${review.id}/react/`, { method: 'POST', body: JSON.stringify({ kind: 'helpful' }) })
                  load()
                }}
              >
                Helpful
              </Button>
              <Link to={`/movies/${review.movie.slug}`}>Open title</Link>
            </div>
          </Panel>
        ))}
      </div>
    </div>
  )
}
