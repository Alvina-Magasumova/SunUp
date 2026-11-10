from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
        Пользователь сервиса SunUp.
        Наследуется от AbstractUser — сохраняет все стандартные поля
        (username, password, email, first_name, last_name, is_staff...),
        добавляет свои: город, часовой пояс, время отправки, темы.
    """
    email = models.EmailField(unique=True, verbose_name='Почта')
    is_email_verified = models.BooleanField(default=False, verbose_name='Email подтверждён')
    city_name = models.CharField(max_length=100, blank=True, verbose_name='Город')
    # координаты заполняются автоматически через Open-Meteo Geocoding API при сохранении города
    city_latitude = models.FloatField(null=True, blank=True, verbose_name='Широта')
    city_longitude = models.FloatField(null=True, blank=True, verbose_name='Долгота')
    timezone = models.CharField(max_length=50, default='Europe/Moscow', verbose_name='Часовой пояс')
    morning_time = models.TimeField(default='08:00', verbose_name='Время отправки')
    is_digest_enabled = models.BooleanField(default=True, verbose_name='Подписка активна')
    topics = models.ManyToManyField(
        'Topic',
        blank=True,
        related_name='users',
        verbose_name='Интересующие темы'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.username} ({"активен" if self.is_digest_enabled else "пауза"})'


class Topic(models.Model):
    """Справочник тем новостей"""
    slug = models.SlugField(unique=True, verbose_name='Идентификатор', help_text='Например: technology')
    name = models.CharField(max_length=100, verbose_name='Название')
    rss_url = models.URLField(blank=True, verbose_name='RSS-лента')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Порядок сортировки темы')

    class Meta:
        verbose_name = 'Тема новостей'
        verbose_name_plural = 'Темы новостей'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
