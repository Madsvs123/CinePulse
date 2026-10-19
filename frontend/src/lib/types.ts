export type Role = 'viewer' | 'streaming' | 'media' | 'community' | 'admin'

export interface Genre {
  id: string
  name: string
  slug: string
}

export interface Movie {
  id: string
  title: string
  slug: string
  tagline?: string
  description: string
  release_date?: string
  year?: number
  runtime: number
  age_rating: string
  poster_url: string
  backdrop_url?: string
  trailer_url?: string
  vote_average: number
  vote_count?: number
  popularity?: number
  trending_score?: number
  is_hidden_gem?: boolean
  genres: Genre[]
  user_reaction?: 'like' | 'dislike' | null
  user_rating?: number | null
  bookmarked?: boolean
  progress_seconds?: number
  languages?: { name: string; code: string }[]
  countries?: { name: string; code: string }[]
  keywords?: { name: string; slug: string }[]
  companies?: { name: string }[]
  directors?: { id: string; name: string; slug: string }[]
  cast?: { id: string; name: string; character: string; slug: string }[]
  availability?: { provider: { name: string }; region: string; offer_type: string; available: boolean }[]
}

export interface RecoItem {
  movie: Movie
  score: number
  reasons: string[]
  signals?: Record<string, number>
}

export interface HomeFeed {
  top_picks: RecoItem[]
  because_you_watched: { seed: Movie | null; items: RecoItem[] }
  hidden_gems: RecoItem[]
  trending: Movie[]
  new_releases: Movie[]
  continue_watching: Movie[]
  genre_collections: { genre: Genre; movies: Movie[] }[]
  weights: Record<string, number>
}

export interface User {
  id: string
  email: string
  username: string
  display_name: string
  role: Role
  email_verified: boolean
  onboarding_complete: boolean
  profile?: {
    bio: string
    location: string
    country: string
    avatar_url: string
    favorite_quote: string
  }
  privacy?: Record<string, boolean>
  notify_prefs?: Record<string, boolean>
  favorite_genres?: { id: string; name: string; slug: string }[]
  preferred_languages?: { id: string; name: string; code: string }[]
}

export interface Taste {
  genres: Record<string, number>
  actors: Record<string, number>
  directors: Record<string, number>
  decades: Record<string, number>
  languages: Record<string, number>
  viewing_patterns: Record<string, number>
  summary: string
}

export interface Review {
  id: string
  title: string
  body: string
  score: number
  contains_spoilers: boolean
  helpful_count: number
  user: { username: string; display_name: string }
  movie: Movie
  reactions?: Record<string, number>
  created_at: string
}

export interface CommunityList {
  id: string
  slug: string
  title: string
  description: string
  is_public: boolean
  user: { username: string; display_name: string }
  items: { movie: Movie; note: string }[]
}

export interface Discussion {
  id: string
  title: string
  body: string
  contains_spoilers: boolean
  user: { username: string; display_name: string }
  comment_count: number
  comments?: { id: string; body: string; contains_spoilers: boolean; user: { display_name: string } }[]
}

export interface NotificationItem {
  id: string
  kind: string
  title: string
  body: string
  payload: Record<string, string>
  is_read: boolean
  created_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface AnalyticsOverview {
  kpis: Record<string, number>
  popular_movies: { movie__title: string; movie__slug: string; plays: number }[]
  search_behavior: { query: string; n: number }[]
  trending_genres: { name: string; score: number }[]
  recommendation_performance: Record<string, number>
  retention: Record<string, number>
  timeline: { day: string; events: number }[]
}
