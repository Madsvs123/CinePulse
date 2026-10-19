from django.contrib import admin

from .models import DailyMetric, SearchQuery

admin.site.register(DailyMetric)
admin.site.register(SearchQuery)
