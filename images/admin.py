from django.contrib import admin
from django.contrib.auth.models import Permission
from .models import ExpiringLink, Image

admin.site.register(Permission)


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("user", "original_file", "uploaded_at")
    list_filter = ("user", "uploaded_at")
    search_fields = ("user__username",)


@admin.register(ExpiringLink)
class ExpiringLinkAdmin(admin.ModelAdmin):
    readonly_fields = ("image", "created_at", "expires_in", "is_expired")
    list_display = ("alias", "image", "created_at", "expires_in", "is_expired")
    list_filter = ("created_at",)
    search_fields = ("image__user__username",)
