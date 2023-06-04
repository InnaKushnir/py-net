from django.contrib import admin

from .models import (
    Post,
    PostLike,
)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "created_time"]
    list_filter = ["title", "owner", "created_time"]
    search_fields = ["title"]


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ["author", "post", "created_time"]
    list_filter = ["author", "post", "created_time"]
