import { useEffect, useState } from 'react'
import { MovieCard } from '../components/movie-card'
import { Button, Field, Panel, Spoiler } from '../components/ui'
import { api, unwrap } from '../lib/api'
import type { CommunityList, Discussion } from '../lib/types'

export function CommunityPage() {
  const [lists, setLists] = useState<CommunityList[]>([])
  const [discussions, setDiscussions] = useState<Discussion[]>([])
  const [title, setTitle] = useState('What should we screen next?')
  const [body, setBody] = useState('')

  const load = () => {
    api<{ results: CommunityList[] } | CommunityList[]>('/api/community/lists/').then((data) => setLists(unwrap(data)))
    api<{ results: Discussion[] } | Discussion[]>('/api/community/discussions/').then((data) => setDiscussions(unwrap(data)))
  }

  useEffect(load, [])

  return (
    <div className="cp-split">
      <div>
        <h1 className="cp-display">Community lists & discussions</h1>
        {lists.map((list) => (
          <section key={list.id} className="cp-section">
            <h2>{list.title}</h2>
            <p className="cp-muted">
              by {list.user.display_name} · {list.description}
            </p>
            <div className="cp-row">
              {list.items.map((item) => (
                <MovieCard key={item.movie.id} movie={item.movie} reasons={item.note ? [item.note] : undefined} />
              ))}
            </div>
          </section>
        ))}
      </div>
      <aside>
        <Panel>
          <h3 className="cp-display">Start a discussion</h3>
          <form
            className="cp-form"
            onSubmit={async (event) => {
              event.preventDefault()
              await api('/api/community/discussions/', { method: 'POST', body: JSON.stringify({ title, body }) })
              setBody('')
              load()
            }}
          >
            <Field label="Title">
              <input className="cp-input" value={title} onChange={(e) => setTitle(e.target.value)} />
            </Field>
            <textarea className="cp-input" rows={4} value={body} onChange={(e) => setBody(e.target.value)} />
            <Button type="submit">Post</Button>
          </form>
        </Panel>
        {discussions.map((item) => (
          <Panel key={item.id}>
            <h3>{item.title}</h3>
            <p className="cp-muted">{item.user.display_name}</p>
            <Spoiler text={item.body} flagged={item.contains_spoilers} />
          </Panel>
        ))}
      </aside>
    </div>
  )
}
