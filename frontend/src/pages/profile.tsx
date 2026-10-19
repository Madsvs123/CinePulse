import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Button, Panel } from '../components/ui'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import type { Taste, User } from '../lib/types'

export function ProfilePage() {
  const { username } = useParams()
  const { user } = useAuth()
  const slug = username || user?.username
  const [profile, setProfile] = useState<(User & { taste?: Taste; is_following?: boolean }) | null>(null)

  useEffect(() => {
    if (!slug) return
    api<User & { taste?: Taste; is_following?: boolean }>(`/api/auth/users/${slug}/`).then(setProfile)
  }, [slug])

  if (!profile) return <p>Loading profile…</p>
  const taste = profile.taste

  return (
    <div className="cp-split">
      <div>
        <h1 className="cp-display">{profile.display_name}</h1>
        <p className="cp-muted">
          @{profile.username} · {profile.role}
        </p>
        {username && user && username !== user.username ? (
          <Button
            kind="gold"
            onClick={async () => {
              const path = profile.is_following ? 'unfollow' : 'follow'
              await api(`/api/auth/users/${profile.username}/${path}/`, { method: path === 'follow' ? 'POST' : 'DELETE' })
              setProfile({ ...profile, is_following: !profile.is_following })
            }}
          >
            {profile.is_following ? 'Unfollow' : 'Follow'}
          </Button>
        ) : null}
        <Panel>
          <p>{profile.profile?.bio || 'This viewer has not written a bio yet.'}</p>
          <p className="cp-muted">{profile.profile?.favorite_quote}</p>
        </Panel>
        <Panel>
          <h3 className="cp-display">Taste profile</h3>
          <p>{taste?.summary}</p>
          <div className="cp-stats">
            {taste
              ? Object.entries(taste.genres)
                  .slice(0, 4)
                  .map(([name, score]) => (
                    <div className="cp-card cp-stat" key={name}>
                      <b>{score.toFixed(1)}</b>
                      {name}
                    </div>
                  ))
              : null}
          </div>
        </Panel>
      </div>
      <aside>
        <Panel>
          <h3>Actors</h3>
          {taste
            ? Object.keys(taste.actors).map((name) => (
                <p key={name}>{name}</p>
              ))
            : null}
          <h3>Directors</h3>
          {taste
            ? Object.keys(taste.directors).map((name) => (
                <p key={name}>{name}</p>
              ))
            : null}
          <h3>Decades</h3>
          {taste
            ? Object.keys(taste.decades).map((name) => (
                <p key={name}>{name}</p>
              ))
            : null}
        </Panel>
      </aside>
    </div>
  )
}
