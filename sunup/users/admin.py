from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Topic
from django import forms
from django.contrib.auth.forms import UserChangeForm

class CustomUserChangeForm(UserChangeForm):
    """Кастомная форма, чтобы применить красивый виджет только к topics"""
    class Meta(UserChangeForm.Meta):
        model = User
        widgets = {
            'topics': admin.widgets.FilteredSelectMultiple(
                verbose_name='Интересующие темы', is_stacked=False
            ),
        }

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    list_display = (
        'username', 'email', 'city_name',
        'timezone', 'morning_time', 'is_digest_enabled', 'is_email_verified',
    )
    list_filter = ('is_digest_enabled', 'is_email_verified', 'is_staff', 'is_active')

    # Добавляем наши блоки к стандартным
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Город и погода', {
            'fields': ('city_name', 'city_latitude', 'city_longitude'),
        }),
        ('Настройки дайджеста', {
            'fields': ('timezone', 'morning_time', 'is_digest_enabled', 'topics', 'is_email_verified'),
        }),
    )

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """Настройка отображения тем в админке"""
    list_display = ('name', 'slug', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}


