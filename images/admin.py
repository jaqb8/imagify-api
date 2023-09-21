from django.contrib import admin
from django.utils.html import format_html
from .models import ExpiringLink, Image


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("user", "original_file", "uploaded_at")
    list_filter = ("user", "uploaded_at")
    search_fields = ("user__username",)


@admin.register(ExpiringLink)
class ExpiringLinkAdmin(admin.ModelAdmin):
    readonly_fields = ("link", "image", "created_at", "expires_in", "is_expired")
    list_display = ("alias", "image", "created_at", "expires_in", "is_expired")
    list_filter = ("created_at",)
    search_fields = ("image__user__username",)

    def link(self, obj):
        return format_html(f'<a href="{obj}">{obj}</a>')
