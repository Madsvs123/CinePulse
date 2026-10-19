import { useEffect, useState } from 'react'
import { RecoRow } from '../components/movie-row'
import { Panel } from '../components/ui'
import { api } from '../lib/api'
import type { HomeFeed, RecoItem, Taste } from '../lib/types'

export function RecommendationsPage() {
  const [feed, setFeed] = useState<HomeFeed | null>(null)
  const [picks, setPicks] = useState<RecoItem[]>([])
  const [taste, setTaste] = useState<Taste | null>(null)
  const [history, setHistory] = useState<{ title: string; reasons: string[]; created_at: string }[]>([])

  useEffect(() => {
    api<HomeFeed>('/api/recommendations/home/').then(setFeed)
    api<RecoItem[]>('/api/recommendations/top-picks/').then(setPicks)
    api<Taste>('/api/recommendations/taste/').then(setTaste)
    api<{ title: string; reasons: string[]; created_at: string }[]>('/api/recommendations/history/').then(setHistory)
  }, [])

  return (
    <div className="cp-split">
      <div>
        <h1 className="cp-display">Recommendations with reasons</h1>
        <p className="cp-muted">Collaborative filtering, catalog similarity, your preferences, and viewing behavior.</p>
        <RecoRow title="Top picks" items={picks} />
        {feed ? (
          <>
            <RecoRow title="Hidden gems" items={feed.hidden_gems} />
            <RecoRow
              title={feed.because_you_watched.seed ? `Because you watched ${feed.because_you_watched.seed.title}` : 'Because you watched'}
              items={feed.because_you_watched.items}
            />
          </>
        ) : null}
      </div>
      <aside>
        <Panel>
          <h3 className="cp-display">Taste snapshot</h3>
          <p>{taste?.summary}</p>
          {taste
            ? Object.entries(taste.genres)
                .slice(0, 6)
                .map(([name, score]) => (
                  <p key={name}>
                    {name} · {score.toFixed(1)}
                  </p>
                ))
            : null}
        </Panel>
        <Panel>
          <h3 className="cp-display">Engine weights</h3>
          {feed
            ? Object.entries(feed.weights).map(([key, value]) => (
                <p key={key}>
                  {key} · {(value * 100).toFixed(0)}%
                </p>
              ))
            : null}
        </Panel>
        <Panel>
          <h3 className="cp-display">Recommendation history</h3>
          {history.slice(0, 8).map((row, index) => (
            <p key={index}>
              {row.title}
              <br />
              <span className="cp-muted">{row.reasons?.[0]}</span>
            </p>
          ))}
        </Panel>
      </aside>
    </div>
  )
}
