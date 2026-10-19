from django.contrib import admin

from .models import (
    Bookmark,
    CastCredit,
    Genre,
    Movie,
    Person,
    Rating,
    StreamingAvailability,
    StreamingProvider,
    WatchHistory,
    Watchlist,
)


class CastInline(admin.TabularInline):
    model = CastCredit
    extra = 0


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "release_date", "vote_average", "popularity", "is_hidden_gem")
    list_filter = ("is_hidden_gem", "age_rating", "genres")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [CastInline]
    filter_horizontal = ("genres", "languages", "countries", "keywords", "companies", "directors")


admin.site.register(Genre)
admin.site.register(Person)
admin.site.register(StreamingProvider)
admin.site.register(StreamingAvailability)
admin.site.register(Rating)
admin.site.register(WatchHistory)
admin.site.register(Bookmark)
admin.site.register(Watchlist)
