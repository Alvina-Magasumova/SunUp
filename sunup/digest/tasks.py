import asyncio
from datetime import date
from celery import shared_task
from django.utils import timezone

from users.models import User
from .models import DailyDigest
from .services.weather import fetch_weather
from .services.news import fetch_news
from .services.llm import generate_mood
from .services.builder import build_digest_message


@shared_task
def generate_digest_for_user(user_id: int, digest_date: str):
    """Сгенерировать дайджест для одного пользователя"""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        print(f"Пользователь {user_id} не найден")
        return

    # Проверяем, нет ли уже дайджеста за этот день
    digest_date_obj = date.fromisoformat(digest_date)
    if DailyDigest.objects.filter(user=user, date=digest_date_obj).exists():
        print(f"Дайджест для {user.username} за {digest_date} уже есть")
        return

    # Проверяем, что у пользователя есть город и координаты
    if not user.city_latitude or not user.city_longitude:
        print(f"У пользователя {user.username} не указан город")
        return

    # 1. Погода
    weather = asyncio.run(fetch_weather(user.city_latitude, user.city_longitude))
    if not weather:
        print(f"Не удалось получить погоду для {user.username}")
        return

    # 2. Новости
    user_topics = user.topics.filter(is_active=True)
    news_by_topic = fetch_news(user_topics, max_per_topic=3) or {}

    # 3. Настроение от GigaChat
    mood = generate_mood(weather)
    if not mood:
        print(f"Не удалось сгенерировать настроение для {user.username}")
        return

    # 4. Собираем сообщение
    message = build_digest_message(
        city_name=user.city_name or "Ваш город",
        weather=weather,
        mood=mood,
        news_by_topic=news_by_topic,
    )

    # 5. Сохраняем в БД
    digest = DailyDigest.objects.create(
        user=user,
        date=digest_date_obj,
        weather_data=weather,
        news_data=news_by_topic,
        mood_score=mood["score"],
        mood_text=mood["text"],
        full_message=message,
        status=DailyDigest.STATUS_PENDING,
    )
    print(f"Дайджест для {user.username} создан (id={digest.id})")

    # 6. Отправляем email
    from .channels import CHANNELS
    channel = CHANNELS.get('email')
    if channel and channel.send(user, message):
        digest.status = DailyDigest.STATUS_SENT
        digest.sent_at = timezone.now()
        digest.save(update_fields=['status', 'sent_at'])
        print(f"Дайджест для {user.username} отправлен на {user.email}")
    else:
        digest.status = DailyDigest.STATUS_FAILED
        digest.error_message = 'Не удалось отправить email'
        digest.save(update_fields=['status', 'error_message'])
        print(f"Не удалось отправить дайджест для {user.username}")

    return digest.id


@shared_task
def check_morning_users():
    """Запускается каждую минуту. Ищет, кому пора отправить дайджест"""
    now_utc = timezone.now()

    users = User.objects.filter(
        is_digest_enabled=True,
        is_email_verified=True,
        city_latitude__isnull=False,
        city_longitude__isnull=False,
    )

    for user in users:
        try:
            from zoneinfo import ZoneInfo
            user_tz = ZoneInfo(user.timezone)
        except Exception:
            user_tz = ZoneInfo("Europe/Moscow")

        local_now = now_utc.astimezone(user_tz)

        if (local_now.hour == user.morning_time.hour
                and local_now.minute == user.morning_time.minute):
            digest_date = local_now.date().isoformat()
            generate_digest_for_user.delay(user.id, digest_date)
            print(f"Запущена генерация для {user.username} на {digest_date}")