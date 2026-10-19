from django.contrib import admin

from .models import MovieSimilarity, RecommendationWeight, TasteProfile


@admin.register(RecommendationWeight)
class WeightAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "collaborative", "content", "preferences", "popularity")


admin.site.register(MovieSimilarity)
admin.site.register(TasteProfile)
