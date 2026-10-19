import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout, Protected } from './components/layout'
import { AuthProvider, useAuth } from './lib/auth'
import { ThemeProvider } from './lib/theme'
import { AnalyticsPage } from './pages/analytics'
import { ForgotPasswordPage, LoginPage, RegisterPage, ResetPasswordPage, VerifyEmailPage } from './pages/auth'
import { CommunityPage } from './pages/community'
import { HomePage } from './pages/home'
import { MoviePage } from './pages/movie'
import { NotificationsPage } from './pages/notifications'
import { OnboardingPage } from './pages/onboarding'
import { ProfilePage } from './pages/profile'
import { RecommendationsPage } from './pages/recommendations'
import { ReviewsPage } from './pages/reviews'
import { SearchPage } from './pages/search'
import { SettingsPage } from './pages/settings'
import { WatchlistsPage } from './pages/watchlists'

function AuthedOnboarding() {
  const { user, loading } = useAuth()
  if (loading) return <div className="cp-page">Loading…</div>
  if (!user) return <Navigate to="/login" replace />
  if (user.onboarding_complete) return <Navigate to="/" replace />
  return <OnboardingPage />
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/onboarding" element={<AuthedOnboarding />} />
            <Route
              element={
                <Protected>
                  <AppLayout />
                </Protected>
              }
            >
              <Route path="/" element={<HomePage />} />
              <Route path="/movies/:slug" element={<MoviePage />} />
              <Route path="/recommendations" element={<RecommendationsPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/watchlists" element={<WatchlistsPage />} />
              <Route path="/reviews" element={<ReviewsPage />} />
              <Route path="/community" element={<CommunityPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/u/:username" element={<ProfilePage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/notifications" element={<NotificationsPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  )
}
