import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Panel } from '../components/ui'
import { api } from '../lib/api'
import type { AnalyticsOverview } from '../lib/types'

export function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api<AnalyticsOverview>('/api/analytics/overview/')
      .then(setData)
      .catch((err) => setError(err.message))
  }, [])

  if (error) return <Panel>{error}</Panel>
  if (!data) return <p>Loading studio analytics…</p>

  return (
    <div>
      <h1 className="cp-display">Studio analytics</h1>
      <div className="cp-stats">
        {Object.entries(data.kpis).map(([key, value]) => (
          <div className="cp-card cp-stat" key={key}>
            <b>{typeof value === 'number' ? Number(value).toLocaleString() : value}</b>
            {key.replaceAll('_', ' ')}
          </div>
        ))}
      </div>
      <div className="cp-split" style={{ marginTop: 20 }}>
        <Panel>
          <h3>Catalog activity</h3>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data.timeline}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="day" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="events" fill="#b8872b" />
            </BarChart>
          </ResponsiveContainer>
        </Panel>
        <Panel>
          <h3>Recommendation performance</h3>
          {Object.entries(data.recommendation_performance).map(([key, value]) => (
            <p key={key}>
              {key} · {value}
            </p>
          ))}
          <h3>Retention</h3>
          {Object.entries(data.retention).map(([key, value]) => (
            <p key={key}>
              {key} · {value}%
            </p>
          ))}
        </Panel>
      </div>
      <div className="cp-split" style={{ marginTop: 20 }}>
        <Panel>
          <h3>Popular movies</h3>
          {data.popular_movies.map((row) => (
            <p key={row.movie__slug}>
              {row.movie__title} · {row.plays} plays
            </p>
          ))}
        </Panel>
        <Panel>
          <h3>Search behavior</h3>
          {data.search_behavior.map((row) => (
            <p key={row.query}>
              {row.query || '(empty)'} · {row.n}
            </p>
          ))}
          <h3>Trending genres</h3>
          {data.trending_genres.map((row) => (
            <p key={row.name}>
              {row.name} · {row.score}
            </p>
          ))}
        </Panel>
      </div>
    </div>
  )
}
