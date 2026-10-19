from django.contrib import admin

from .models import Comment, Discussion, Review, UserList

admin.site.register(Review)
admin.site.register(Discussion)
admin.site.register(Comment)
admin.site.register(UserList)
