import { useEffect, useState } from 'react'
import { Link, NavLink, Navigate, Outlet, useNavigate } from 'react-router-dom'
import {
  Bell,
  Clapperboard,
  Compass,
  LayoutDashboard,
  ListVideo,
  Moon,
  Search,
  Settings,
  Sparkles,
  Sun,
  UserRound,
  Users,
} from 'lucide-react'
import { useAuth } from '../lib/auth'
import { useTheme } from '../lib/theme'
import { api } from '../lib/api'
import { connectNotifications } from '../lib/socket'
import type { NotificationItem } from '../lib/types'

const links = [
  { to: '/', label: 'Home', icon: Clapperboard },
  { to: '/recommendations', label: 'For you', icon: Sparkles },
  { to: '/search', label: 'Discover', icon: Compass },
  { to: '/watchlists', label: 'Watchlists', icon: ListVideo },
  { to: '/reviews', label: 'Reviews', icon: Users },
  { to: '/community', label: 'Community', icon: Users },
  { to: '/analytics', label: 'Analytics', icon: LayoutDashboard, roles: ['admin', 'media', 'streaming'] },
  { to: '/profile', label: 'Profile', icon: UserRound },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export function Protected({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="cp-page">Loading CinePulse…</div>
  if (!user) return <Navigate to="/login" replace />
  if (!user.onboarding_complete) return <Navigate to="/onboarding" replace />
  return <>{children}</>
}

export function AppLayout() {
  const { user, logout } = useAuth()
  const { theme, toggle } = useTheme()
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [toast, setToast] = useState<NotificationItem | null>(null)
  const [unread, setUnread] = useState(0)

  useEffect(() => {
    api<{ unread: number; results: NotificationItem[] }>('/api/notifications/').then((data) => {
      setUnread(data.unread)
    })
    return connectNotifications((item) => {
      setToast(item)
      setUnread((count) => count + 1)
    })
  }, [])

  return (
    <div className="cp-app">
      <aside className="cp-sidebar">
        <Link to="/" className="cp-brand">
          <div className="cp-mark">C</div>
          <div>
            <h1>CinePulse</h1>
            <p>Taste, in real time</p>
          </div>
        </Link>
        <nav className="cp-nav">
          {links
            .filter((link) => !link.roles || (user && link.roles.includes(user.role)))
            .map((link) => (
              <NavLink key={link.to} to={link.to} end={link.to === '/'}>
                <link.icon size={18} />
                {link.label}
              </NavLink>
            ))}
        </nav>
        <nav className="cp-nav" style={{ marginTop: 'auto' }}>
          <button className="nav" onClick={toggle} type="button">
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
            {theme === 'dark' ? 'Light theme' : 'Dark theme'}
          </button>
          <button className="nav" onClick={logout} type="button">
            Sign out
          </button>
        </nav>
      </aside>
      <div className="cp-main">
        <header className="cp-top">
          <form
            className="cp-search"
            onSubmit={(event) => {
              event.preventDefault()
              navigate(`/search?q=${encodeURIComponent(query)}`)
            }}
          >
            <Search size={16} />
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search titles, cast, directors" />
          </form>
          <Link to="/notifications" className="cp-chip">
            <Bell size={16} /> {unread} new
          </Link>
        </header>
        <div className="cp-page">
          <Outlet />
        </div>
      </div>
      {toast ? (
        <div className="cp-toast">
          <b>{toast.title}</b>
          <p className="cp-muted">{toast.body}</p>
        </div>
      ) : null}
    </div>
  )
}
