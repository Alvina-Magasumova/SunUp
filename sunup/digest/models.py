from django.conf import settings
from django.db import models

class DailyDigest(models.Model):
    """
        История утренних дайджестов пользователя.
        Одна запись = одно утреннее сообщение за конкретный день.
        Хранит снапшот данных на момент генерации —
        чтобы не зависеть от изменения города/тем в профиле пользователя.
    """
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [(STATUS_PENDING, 'В очереди'), (STATUS_SENT, 'Отправлен'), (STATUS_FAILED, 'Ошибка')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='digests', verbose_name='Пользователь')
    date = models.DateField(verbose_name='Дата дайджеста')
    # --- Снапшот данных на момент генерации ---
    weather_data = models.JSONField(default=dict, blank=True, verbose_name='Данные о погоде')
    news_data = models.JSONField(default=dict, blank=True, verbose_name='Данные о новостях')
    # --- Настроение дня от LLM ---
    mood_score = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Оценка настроения', help_text='От 1 до 10')
    mood_text = models.TextField(blank=True, verbose_name='Текст настроения')
    full_message = models.TextField(blank=True, verbose_name='Итоговое сообщение')
    # --- Статус доставки ---
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, verbose_name='Статус')
    error_message = models.TextField(blank=True, verbose_name='Ошибка')
    # --- Временные метки ---
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата отправки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Дайджест'
        verbose_name_plural = 'Дайджесты'
        ordering = ['-date']
        unique_together = ('user', 'date')
        indexes = [ models.Index(fields=['user', '-date']),]

    def __str__(self):
        return f'{self.user.username} — {self.date}'
