import { useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom'
import { Button, Field, Panel } from '../components/ui'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'

export function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('jordan@cinepulse.club')
  const [password, setPassword] = useState('cinepulse')
  const [error, setError] = useState('')

  if (user) return <Navigate to={user.onboarding_complete ? '/' : '/onboarding'} replace />

  return (
    <div className="cp-auth">
      <Panel className="cp-auth-card">
        <p className="cp-kicker">CinePulse</p>
        <h2 className="cp-display">Welcome back to the screening room</h2>
        <p className="cp-muted">Personalized discovery for viewers, streamers, and film communities.</p>
        <form
          className="cp-form"
          onSubmit={async (event) => {
            event.preventDefault()
            setError('')
            try {
              await login(email, password)
              navigate('/')
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Unable to sign in')
            }
          }}
        >
          <Field label="Email">
            <input className="cp-input" value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <Field label="Password">
            <input className="cp-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </Field>
          {error ? <div className="cp-notice">{error}</div> : null}
          <Button type="submit" kind="gold">
            Enter CinePulse
          </Button>
        </form>
        <p className="cp-muted">
          New here? <Link to="/register">Create an account</Link>
          <br />
          <Link to="/forgot-password">Forgot password</Link>
        </p>
      </Panel>
    </div>
  )
}

export function RegisterPage() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    email: '',
    username: '',
    display_name: '',
    password: '',
    role: 'viewer',
  })
  const [error, setError] = useState('')
  if (user) return <Navigate to="/onboarding" replace />

  return (
    <div className="cp-auth">
      <Panel className="cp-auth-card">
        <h2 className="cp-display">Join the pulse</h2>
        <form
          className="cp-form"
          onSubmit={async (event) => {
            event.preventDefault()
            try {
              await register(form)
              navigate('/onboarding')
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Unable to register')
            }
          }}
        >
          {(['email', 'username', 'display_name', 'password'] as const).map((field) => (
            <Field key={field} label={field.replace('_', ' ')}>
              <input
                className="cp-input"
                type={field === 'password' ? 'password' : 'text'}
                value={form[field]}
                onChange={(e) => setForm({ ...form, [field]: e.target.value })}
              />
            </Field>
          ))}
          <Field label="I am joining as">
            <select className="cp-select" value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })}>
              <option value="viewer">Viewer</option>
              <option value="streaming">Streaming service</option>
              <option value="media">Media company</option>
              <option value="community">Community organizer</option>
            </select>
          </Field>
          {error ? <div className="cp-notice">{error}</div> : null}
          <Button type="submit" kind="gold">
            Create account
          </Button>
        </form>
      </Panel>
    </div>
  )
}

export function VerifyEmailPage() {
  const [params] = useSearchParams()
  const [message, setMessage] = useState('Confirming your email…')
  useEffect(() => {
    const token = params.get('token')
    if (!token) {
      setMessage('Missing verification token.')
      return
    }
    api('/api/auth/verify-email/', { method: 'POST', body: JSON.stringify({ token }) })
      .then(() => setMessage('Email verified. You can return to CinePulse.'))
      .catch((err) => setMessage(err.message))
  }, [params])
  return (
    <div className="cp-auth">
      <Panel className="cp-auth-card">
        <h2 className="cp-display">Email verification</h2>
        <p>{message}</p>
        <Link to="/login">Back to sign in</Link>
      </Panel>
    </div>
  )
}

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  return (
    <div className="cp-auth">
      <Panel className="cp-auth-card">
        <h2 className="cp-display">Reset password</h2>
        <form
          className="cp-form"
          onSubmit={async (event) => {
            event.preventDefault()
            await api('/api/auth/forgot-password/', { method: 'POST', body: JSON.stringify({ email }) })
            setMessage('If that account exists, a reset email is on the way.')
          }}
        >
          <Field label="Email">
            <input className="cp-input" value={email} onChange={(e) => setEmail(e.target.value)} />
          </Field>
          <Button type="submit">Send reset link</Button>
        </form>
        {message ? <p>{message}</p> : null}
      </Panel>
    </div>
  )
}

export function ResetPasswordPage() {
  const [params] = useSearchParams()
  const [password, setPassword] = useState('')
  const [message, setMessage] = useState('')
  return (
    <div className="cp-auth">
      <Panel className="cp-auth-card">
        <h2 className="cp-display">Choose a new password</h2>
        <form
          className="cp-form"
          onSubmit={async (event) => {
            event.preventDefault()
            await api('/api/auth/reset-password/', {
              method: 'POST',
              body: JSON.stringify({ token: params.get('token'), password }),
            })
            setMessage('Password updated. You can sign in now.')
          }}
        >
          <Field label="New password">
            <input className="cp-input" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </Field>
          <Button type="submit">Update password</Button>
        </form>
        {message ? <p>{message}</p> : <Link to="/login">Back to sign in</Link>}
      </Panel>
    </div>
  )
}
