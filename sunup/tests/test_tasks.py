import pytest
from datetime import date
from unittest.mock import patch
from django.contrib.auth import get_user_model
from digest.models import DailyDigest
from digest.tasks import generate_digest_for_user

User = get_user_model()


@pytest.mark.django_db
@patch("digest.tasks.fetch_news")
@patch("digest.tasks.fetch_weather")
@patch("digest.tasks.generate_mood")
def test_generate_digest_creates_record(mock_mood, mock_weather, mock_news):
    """Интеграционный тест: задача создаёт запись в БД"""
    # Создаем пользователя
    user = User.objects.create_user(
        username="testuser2",
        email="test2@example.com",
        password="StrongPass123!",
        city_name="Москва",
        city_latitude=55.75,
        city_longitude=37.62,
        is_email_verified=True,
    )

    # Мокаем внешние сервисы
    mock_weather.return_value = {"temperature": 10, "wind_speed": 2.0}
    mock_news.return_value = {"Наука": [{"title": "Новость", "link": "http://link"}]}
    mock_mood.return_value = {"score": 8, "text": "Отличный день"}

    today = date.today().isoformat()
    result = generate_digest_for_user(user.id, today)

    assert result is not None
    assert DailyDigest.objects.filter(user=user, date=date.today()).exists()


@pytest.mark.django_db
def test_generate_digest_no_duplicates():
    """Регрессионный тест: защита от дублей"""
    user = User.objects.create_user(
        username="testuser3",
        email="test3@example.com",
        password="StrongPass123!",
        city_name="Москва",
        city_latitude=55.75,
        city_longitude=37.62,
        is_email_verified=True,
    )
    today = date.today()
    # Создаем первый дайджест
    DailyDigest.objects.create(user=user, date=today, weather_data={}, news_data={}, mood_score=5, mood_text="",
                               full_message="")

    # Пытаемся запустить задачу второй раз
    result = generate_digest_for_user(user.id, today.isoformat())

    # Должно вернуться None (дайджест уже есть)
    assert result is None
    assert DailyDigest.objects.filter(user=user, date=today).count() == 1