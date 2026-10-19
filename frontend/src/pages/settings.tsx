import { useEffect, useState } from 'react'
import { Button, Field, Panel } from '../components/ui'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'

export function SettingsPage() {
  const { user, refresh } = useAuth()
  const [profile, setProfile] = useState({
    display_name: user?.display_name || '',
    bio: user?.profile?.bio || '',
    country: user?.profile?.country || '',
    favorite_quote: user?.profile?.favorite_quote || '',
  })
  const [privacy, setPrivacy] = useState(user?.privacy || {})
  const [prefs, setPrefs] = useState(user?.notify_prefs || {})

  useEffect(() => {
    if (!user) return
    setProfile({
      display_name: user.display_name,
      bio: user.profile?.bio || '',
      country: user.profile?.country || '',
      favorite_quote: user.profile?.favorite_quote || '',
    })
    setPrivacy(user.privacy || {})
    setPrefs(user.notify_prefs || {})
  }, [user])

  return (
    <div className="cp-split">
      <div>
        <h1 className="cp-display">Settings</h1>
        <Panel>
          <h3>Profile</h3>
          <form
            className="cp-form"
            onSubmit={async (event) => {
              event.preventDefault()
              await api('/api/auth/me/', {
                method: 'PATCH',
                body: JSON.stringify({
                  display_name: profile.display_name,
                  profile: {
                    bio: profile.bio,
                    country: profile.country,
                    favorite_quote: profile.favorite_quote,
                  },
                }),
              })
              refresh()
            }}
          >
            <Field label="Display name">
              <input className="cp-input" value={profile.display_name} onChange={(e) => setProfile({ ...profile, display_name: e.target.value })} />
            </Field>
            <Field label="Bio">
              <textarea className="cp-input" value={profile.bio} onChange={(e) => setProfile({ ...profile, bio: e.target.value })} />
            </Field>
            <Field label="Country">
              <input className="cp-input" value={profile.country} onChange={(e) => setProfile({ ...profile, country: e.target.value })} />
            </Field>
            <Field label="Favorite quote">
              <input className="cp-input" value={profile.favorite_quote} onChange={(e) => setProfile({ ...profile, favorite_quote: e.target.value })} />
            </Field>
            <Button type="submit">Save profile</Button>
          </form>
        </Panel>
      </div>
      <aside>
        <Panel>
          <h3>Privacy</h3>
          {Object.entries(privacy).map(([key, value]) => (
            <label key={key} style={{ display: 'block', marginBottom: 8 }}>
              <input
                type="checkbox"
                checked={Boolean(value)}
                onChange={async (e) => {
                  const next = { ...privacy, [key]: e.target.checked }
                  setPrivacy(next)
                  await api('/api/auth/privacy/', { method: 'PATCH', body: JSON.stringify(next) })
                }}
              />{' '}
              {key.replaceAll('_', ' ')}
            </label>
          ))}
        </Panel>
        <Panel>
          <h3>Notifications</h3>
          {Object.entries(prefs).map(([key, value]) => (
            <label key={key} style={{ display: 'block', marginBottom: 8 }}>
              <input
                type="checkbox"
                checked={Boolean(value)}
                onChange={async (e) => {
                  const next = { ...prefs, [key]: e.target.checked }
                  setPrefs(next)
                  await api('/api/auth/notification-preferences/', { method: 'PATCH', body: JSON.stringify(next) })
                }}
              />{' '}
              {key.replaceAll('_', ' ')}
            </label>
          ))}
        </Panel>
      </aside>
    </div>
  )
}
