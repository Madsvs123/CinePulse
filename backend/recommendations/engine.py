from collections import Counter, defaultdict
from datetime import timedelta

import numpy as np
from django.conf import settings
from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from movies.models import Movie, MovieReaction, Rating, WatchHistory
from recommendations.models import MovieSimilarity, RecommendationHistory, RecommendationWeight, TasteProfile


def active_weights():
    row = RecommendationWeight.objects.filter(is_active=True).first()
    if row:
        return row.as_dict()
    return dict(settings.RECOMMENDATION_WEIGHTS)


def _cosine(a, b):
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _feature_vector(movie, vocab):
    tokens = set()
    tokens.update(f"g:{g.slug}" for g in movie.genres.all())
    tokens.update(f"k:{k.slug}" for k in movie.keywords.all())
    tokens.update(f"d:{d.slug}" for d in movie.directors.all())
    tokens.update(f"c:{c.person.slug}" for c in movie.cast_credits.all()[:8])
    tokens.update(f"l:{lang.code}" for lang in movie.languages.all())
    vec = np.zeros(len(vocab), dtype=float)
    for i, token in enumerate(vocab):
        if token in tokens:
            vec[i] = 1.0
    return vec


def build_similarity_graph(limit_neighbors=12):
    movies = list(
        Movie.objects.prefetch_related("genres", "keywords", "directors", "cast_credits__person", "languages")
    )
    if len(movies) < 2:
        return 0
    vocab = []
    seen = set()
    for movie in movies:
        for token in (
            [f"g:{g.slug}" for g in movie.genres.all()]
            + [f"k:{k.slug}" for k in movie.keywords.all()]
            + [f"d:{d.slug}" for d in movie.directors.all()]
            + [f"c:{c.person.slug}" for c in movie.cast_credits.all()[:8]]
        ):
            if token not in seen:
                seen.add(token)
                vocab.append(token)
    vectors = {movie.id: _feature_vector(movie, vocab) for movie in movies}
    MovieSimilarity.objects.all().delete()
    rows = []
    for source in movies:
        scored = []
        for target in movies:
            if source.id == target.id:
                continue
            score = _cosine(vectors[source.id], vectors[target.id])
            if score <= 0:
                continue
            shared = sorted(
                set(f"g:{g.slug}" for g in source.genres.all()) & set(f"g:{g.slug}" for g in target.genres.all())
            )
            scored.append((target, score, shared))
        scored.sort(key=lambda item: item[1], reverse=True)
        for target, score, shared in scored[:limit_neighbors]:
            rows.append(MovieSimilarity(source=source, target=target, score=score, shared_signals=shared))
    MovieSimilarity.objects.bulk_create(rows, batch_size=500)
    return len(rows)


def collaborative_scores(user):
    user_ratings = dict(Rating.objects.filter(user=user).values_list("movie_id", "score"))
    if len(user_ratings) < 2:
        likes = MovieReaction.objects.filter(user=user, kind="like").values_list("movie_id", flat=True)
        return {mid: 0.7 for mid in likes}

    others = (
        Rating.objects.exclude(user=user)
        .filter(movie_id__in=user_ratings.keys())
        .values("user_id", "movie_id", "score")
    )
    by_user = defaultdict(dict)
    for row in others:
        by_user[row["user_id"]][row["movie_id"]] = float(row["score"])

    neighbor_weights = {}
    for other_id, ratings in by_user.items():
        shared = [mid for mid in ratings if mid in user_ratings]
        if len(shared) < 2:
            continue
        a = np.array([float(user_ratings[mid]) for mid in shared])
        b = np.array([ratings[mid] for mid in shared])
        sim = _cosine(a - a.mean(), b - b.mean())
        if sim > 0.05:
            neighbor_weights[other_id] = sim

    scores = defaultdict(float)
    norms = defaultdict(float)
    neighbor_ratings = Rating.objects.filter(user_id__in=neighbor_weights.keys()).values("user_id", "movie_id", "score")
    for row in neighbor_ratings:
        if row["movie_id"] in user_ratings:
            continue
        weight = neighbor_weights[row["user_id"]]
        scores[row["movie_id"]] += weight * float(row["score"])
        norms[row["movie_id"]] += abs(weight)
    return {mid: (scores[mid] / norms[mid]) / 10.0 for mid in scores if norms[mid]}


def content_scores(user):
    seeds = list(
        WatchHistory.objects.filter(user=user)
        .select_related("movie")
        .order_by("-watched_at")
        .values_list("movie_id", flat=True)[:12]
    )
    rated = list(Rating.objects.filter(user=user, score__gte=7).values_list("movie_id", flat=True)[:12])
    seed_ids = list(dict.fromkeys(seeds + rated))
    if not seed_ids:
        return {}
    similar = MovieSimilarity.objects.filter(source_id__in=seed_ids).values("target_id", "score")
    scores = defaultdict(float)
    for row in similar:
        scores[row["target_id"]] = max(scores[row["target_id"]], float(row["score"]))
    return scores


def preference_scores(user):
    genre_ids = list(user.favorite_genres.values_list("genre_id", flat=True))
    language_ids = list(user.preferred_languages.values_list("language_id", flat=True))
    if not genre_ids and not language_ids:
        return {}
    query = Q()
    if genre_ids:
        query |= Q(genres__id__in=genre_ids)
    if language_ids:
        query |= Q(languages__id__in=language_ids)
    movies = Movie.objects.filter(query).distinct().values("id", "vote_average")
    return {row["id"]: min(1.0, (row["vote_average"] or 0) / 10 + 0.3) for row in movies}


def behavior_scores(user):
    recent = WatchHistory.objects.filter(user=user, watched_at__gte=timezone.now() - timedelta(days=90))
    genre_counter = Counter()
    director_counter = Counter()
    for item in recent.select_related("movie").prefetch_related("movie__genres", "movie__directors"):
        weight = 1.2 if item.completed else 0.6
        for genre in item.movie.genres.all():
            genre_counter[genre.id] += weight
        for director in item.movie.directors.all():
            director_counter[director.id] += weight
    if not genre_counter:
        return {}
    top_genres = [gid for gid, _ in genre_counter.most_common(5)]
    movies = Movie.objects.filter(genres__id__in=top_genres).distinct().values("id")
    return {row["id"]: 0.55 + min(0.4, genre_counter.most_common(1)[0][1] / 20) for row in movies}


def rating_popularity_recency_maps():
    movies = Movie.objects.values("id", "vote_average", "popularity", "release_date", "is_hidden_gem")
    now = timezone.now().date()
    rating_map, pop_map, recency_map = {}, {}, {}
    for row in movies:
        rating_map[row["id"]] = min(1.0, (row["vote_average"] or 0) / 10)
        pop_map[row["id"]] = min(1.0, (row["popularity"] or 0) / 100)
        days = 800
        if row["release_date"]:
            days = max(1, (now - row["release_date"]).days)
        recency_map[row["id"]] = max(0.05, 1.0 / (1 + days / 180))
    return rating_map, pop_map, recency_map


def seen_movie_ids(user):
    watched = set(WatchHistory.objects.filter(user=user, completed=True).values_list("movie_id", flat=True))
    disliked = set(MovieReaction.objects.filter(user=user, kind="dislike").values_list("movie_id", flat=True))
    return watched | disliked


def explain(movie, user, parts):
    reasons = []
    if parts.get("preferences", 0) > 0.2:
        fav = list(user.favorite_genres.select_related("genre").values_list("genre__name", flat=True)[:2])
        if fav:
            reasons.append(f"Matches your taste for {', '.join(fav)}")
    if parts.get("behavior", 0) > 0.2:
        reasons.append("Fits your recent viewing pattern")
    if parts.get("content", 0) > 0.25:
        last = WatchHistory.objects.filter(user=user).select_related("movie").order_by("-watched_at").first()
        if last:
            reasons.append(f"Similar to {last.movie.title}")
        else:
            reasons.append("Shares themes with titles you enjoyed")
    if parts.get("collaborative", 0) > 0.2:
        reasons.append("Viewers like you rated this highly")
    if movie.is_hidden_gem:
        reasons.append("A hidden gem with strong word of mouth")
    if parts.get("recency", 0) > 0.35:
        reasons.append("A recent release gaining attention")
    if parts.get("popularity", 0) > 0.4:
        reasons.append("Currently popular on CinePulse")
    if not reasons:
        reasons.append("Balanced match from ratings, popularity, and catalog fit")
    return reasons[:3]


def score_catalog(user, exclude=None, limit=40):
    weights = active_weights()
    exclude = exclude or seen_movie_ids(user)
    collab = collaborative_scores(user)
    content = content_scores(user)
    prefs = preference_scores(user)
    behavior = behavior_scores(user)
    rating_map, pop_map, recency_map = rating_popularity_recency_maps()

    movie_ids = set(rating_map) | set(collab) | set(content) | set(prefs) | set(behavior)
    ranked = []
    movies = {m.id: m for m in Movie.objects.filter(id__in=movie_ids)}
    for mid in movie_ids:
        if mid in exclude:
            continue
        movie = movies.get(mid)
        if not movie:
            continue
        parts = {
            "collaborative": collab.get(mid, 0.0),
            "content": content.get(mid, 0.0),
            "preferences": prefs.get(mid, 0.0),
            "behavior": behavior.get(mid, 0.0),
            "ratings": rating_map.get(mid, 0.0),
            "popularity": pop_map.get(mid, 0.0),
            "recency": recency_map.get(mid, 0.0),
        }
        score = sum(parts[key] * weights.get(key, 0) for key in parts)
        ranked.append((movie, score, parts))
    ranked.sort(key=lambda item: item[1], reverse=True)
    return ranked[:limit]


def serialize_reco(movie, score, parts, user):
    return {
        "movie": movie_card(movie, user),
        "score": round(float(score), 4),
        "reasons": explain(movie, user, parts),
        "signals": {k: round(float(v), 3) for k, v in parts.items()},
    }


def movie_card(movie, user=None):
    reaction = None
    rating = None
    bookmarked = False
    progress = 0
    if user and user.is_authenticated:
        reaction = MovieReaction.objects.filter(user=user, movie=movie).values_list("kind", flat=True).first()
        rating_obj = Rating.objects.filter(user=user, movie=movie).first()
        rating = float(rating_obj.score) if rating_obj else None
        bookmarked = movie.bookmarks.filter(user=user).exists()
        history = WatchHistory.objects.filter(user=user, movie=movie).first()
        progress = history.progress_seconds if history else 0
    return {
        "id": str(movie.id),
        "title": movie.title,
        "slug": movie.slug,
        "tagline": movie.tagline,
        "description": movie.description,
        "release_date": movie.release_date,
        "year": movie.year,
        "runtime": movie.runtime,
        "age_rating": movie.age_rating,
        "poster_url": movie.poster_url,
        "backdrop_url": movie.backdrop_url,
        "trailer_url": movie.trailer_url,
        "vote_average": movie.vote_average,
        "vote_count": movie.vote_count,
        "popularity": movie.popularity,
        "trending_score": movie.trending_score,
        "is_hidden_gem": movie.is_hidden_gem,
        "genres": [{"id": str(g.id), "name": g.name, "slug": g.slug} for g in movie.genres.all()],
        "user_reaction": reaction,
        "user_rating": rating,
        "bookmarked": bookmarked,
        "progress_seconds": progress,
    }


def build_home_sections(user):
    ranked = score_catalog(user, limit=60)
    history = list(WatchHistory.objects.filter(user=user).select_related("movie").order_by("-watched_at")[:8])
    continue_watching = [
        movie_card(item.movie, user)
        for item in WatchHistory.objects.filter(user=user, completed=False)
        .select_related("movie")
        .prefetch_related("movie__genres")
        .order_by("-watched_at")[:12]
    ]
    last_watched = history[0].movie if history else None
    because = []
    if last_watched:
        neighbors = MovieSimilarity.objects.filter(source=last_watched).select_related("target").order_by("-score")[:12]
        because = [
            serialize_reco(row.target, row.score, {"content": row.score}, user)
            for row in neighbors
            if row.target_id not in seen_movie_ids(user)
        ]
    hidden = [
        serialize_reco(m, m.vote_average / 10, {"ratings": m.vote_average / 10}, user)
        for m in Movie.objects.filter(is_hidden_gem=True).prefetch_related("genres").order_by("-vote_average")[:12]
    ]
    trending = [
        movie_card(m, user)
        for m in Movie.objects.prefetch_related("genres").order_by("-trending_score", "-popularity")[:12]
    ]
    new_releases = [
        movie_card(m, user) for m in Movie.objects.prefetch_related("genres").order_by("-release_date")[:12]
    ]
    top_picks = [serialize_reco(movie, score, parts, user) for movie, score, parts in ranked[:12]]

    genre_rows = []
    favs = list(user.favorite_genres.select_related("genre")[:4])
    if not favs:
        from movies.models import Genre

        favs = [{"genre": g} for g in Genre.objects.all()[:4]]
    for item in favs:
        genre = item.genre if hasattr(item, "genre") else item["genre"]
        genre_rows.append(
            {
                "genre": {"id": str(genre.id), "name": genre.name, "slug": genre.slug},
                "movies": [
                    movie_card(m, user)
                    for m in Movie.objects.filter(genres=genre).prefetch_related("genres").order_by("-vote_average")[:12]
                ],
            }
        )

    RecommendationHistory.objects.bulk_create(
        [
            RecommendationHistory(
                user=user,
                movie=movie,
                section="top_picks",
                score=score,
                reasons=explain(movie, user, parts),
            )
            for movie, score, parts in ranked[:12]
        ]
    )

    return {
        "top_picks": top_picks,
        "because_you_watched": {
            "seed": movie_card(last_watched, user) if last_watched else None,
            "items": because,
        },
        "hidden_gems": hidden,
        "trending": trending,
        "new_releases": new_releases,
        "continue_watching": continue_watching,
        "genre_collections": genre_rows,
        "weights": active_weights(),
    }


def refresh_taste_profile(user):
    ratings = Rating.objects.filter(user=user).select_related("movie").prefetch_related(
        "movie__genres", "movie__directors", "movie__cast_credits__person", "movie__languages"
    )
    history = WatchHistory.objects.filter(user=user).select_related("movie").prefetch_related("movie__genres")
    genres, actors, directors, decades, languages = Counter(), Counter(), Counter(), Counter(), Counter()
    completed = history.filter(completed=True).count()
    in_progress = history.filter(completed=False).count()
    for rating in ratings:
        weight = float(rating.score) / 10
        for genre in rating.movie.genres.all():
            genres[genre.name] += weight
        for director in rating.movie.directors.all():
            directors[director.name] += weight
        for credit in rating.movie.cast_credits.all()[:5]:
            actors[credit.person.name] += weight
        if rating.movie.year:
            decades[f"{(rating.movie.year // 10) * 10}s"] += weight
        for language in rating.movie.languages.all():
            languages[language.name] += weight
    for item in history:
        for genre in item.movie.genres.all():
            genres[genre.name] += 0.35
    avg = ratings.aggregate(avg=Avg("score"), count=Count("id"))
    summary_bits = []
    if genres:
        summary_bits.append(f"leans {', '.join(name for name, _ in genres.most_common(2))}")
    if decades:
        summary_bits.append(f"often revisits the {decades.most_common(1)[0][0]}")
    if languages:
        summary_bits.append(f"watches in {languages.most_common(1)[0][0]}")
    profile, _ = TasteProfile.objects.update_or_create(
        user=user,
        defaults={
            "genres": dict(genres.most_common(12)),
            "actors": dict(actors.most_common(12)),
            "directors": dict(directors.most_common(10)),
            "decades": dict(decades.most_common(8)),
            "languages": dict(languages.most_common(8)),
            "viewing_patterns": {
                "completed": completed,
                "in_progress": in_progress,
                "average_rating": float(avg["avg"] or 0),
                "ratings_count": avg["count"],
            },
            "summary": "CinePulse taste profile " + ("; ".join(summary_bits) if summary_bits else "is still forming."),
            "computed_at": timezone.now(),
        },
    )
    return profile


def similar_movies(movie, user=None, limit=12):
    rows = MovieSimilarity.objects.filter(source=movie).select_related("target").order_by("-score")[:limit]
    items = []
    for row in rows:
        items.append(
            {
                "movie": movie_card(row.target, user),
                "score": row.score,
                "reasons": [f"Shares {signal.replace('g:', '')}" for signal in row.shared_signals[:3]]
                or ["Close catalog match"],
            }
        )
    if items:
        return items
    qs = Movie.objects.filter(genres__in=movie.genres.all()).exclude(id=movie.id).distinct().order_by("-vote_average")[:limit]
    return [{"movie": movie_card(m, user), "score": 0.4, "reasons": ["Overlapping genres"]} for m in qs]
