from django.contrib import admin
from .models import DailyDigest


@admin.register(DailyDigest)
class DailyDigestAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'status', 'mood_score', 'sent_at')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'sent_at')
    date_hierarchy = 'date'
