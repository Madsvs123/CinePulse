import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button, Chip, Field, Panel } from '../components/ui'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import type { Genre } from '../lib/types'

export function OnboardingPage() {
  const { refresh } = useAuth()
  const navigate = useNavigate()
  const [genres, setGenres] = useState<Genre[]>([])
  const [languages, setLanguages] = useState<{ id: string; name: string }[]>([])
  const [pickedGenres, setPicked] = useState<string[]>([])
  const [pickedLangs, setLangs] = useState<string[]>([])
  const [displayName, setDisplayName] = useState('')
  const [country, setCountry] = useState('')

  useEffect(() => {
    api<{ genres: Genre[]; languages: { id: string; name: string }[] }>('/api/movies/facets/').then((data) => {
      setGenres(data.genres)
      setLanguages(data.languages)
    })
  }, [])

  const toggle = (list: string[], id: string, setter: (v: string[]) => void) => {
    setter(list.includes(id) ? list.filter((item) => item !== id) : [...list, id])
  }

  return (
    <div className="cp-auth">
      <Panel className="cp-auth-card">
        <p className="cp-kicker">Onboarding</p>
        <h2 className="cp-display">Tune the recommendation engine to you</h2>
        <form
          className="cp-form"
          onSubmit={async (event) => {
            event.preventDefault()
            await api('/api/auth/onboarding/', {
              method: 'POST',
              body: JSON.stringify({
                display_name: displayName,
                country,
                genre_ids: pickedGenres,
                language_ids: pickedLangs,
              }),
            })
            await refresh()
            navigate('/')
          }}
        >
          <Field label="Display name">
            <input className="cp-input" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
          </Field>
          <Field label="Country">
            <input className="cp-input" value={country} onChange={(e) => setCountry(e.target.value)} />
          </Field>
          <div>
            <p>Favorite genres</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {genres.map((genre) => (
                <Chip
                  key={genre.id}
                  label={genre.name}
                  active={pickedGenres.includes(genre.id)}
                  onClick={() => toggle(pickedGenres, genre.id, setPicked)}
                />
              ))}
            </div>
          </div>
          <div>
            <p>Preferred languages</p>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {languages.map((language) => (
                <Chip
                  key={language.id}
                  label={language.name}
                  active={pickedLangs.includes(language.id)}
                  onClick={() => toggle(pickedLangs, language.id, setLangs)}
                />
              ))}
            </div>
          </div>
          <Button type="submit" kind="gold">
            Build my taste profile
          </Button>
        </form>
      </Panel>
    </div>
  )
}
