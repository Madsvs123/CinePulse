from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import FavoriteGenre, Follow, PreferredLanguage, PrivacySettings, Profile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "display_name", "role", "email_verified", "onboarding_complete")
    list_filter = ("role", "email_verified", "onboarding_complete")
    search_fields = ("email", "username", "display_name")
    ordering = ("email",)
    fieldsets = BaseUserAdmin.fieldsets + (("CinePulse", {"fields": ("display_name", "role", "email_verified", "onboarding_complete")}),)


admin.site.register(Profile)
admin.site.register(PrivacySettings)
admin.site.register(FavoriteGenre)
admin.site.register(PreferredLanguage)
admin.site.register(Follow)
