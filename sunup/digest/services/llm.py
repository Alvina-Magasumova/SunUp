import asyncio
import json
from typing import Optional
from django.conf import settings
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole


def generate_mood(weather: dict) -> Optional[dict]:
    """Сгенерировать оценку и текст настроения по погоде через GigaChat"""
    credentials = getattr(settings, 'GIGACHAT_CREDENTIALS', None)
    if not credentials:
        print("ОШИБКА: GIGACHAT_CREDENTIALS не задан в settings.py")
        return None

    temp = weather.get('temperature', 'неизвестно')
    wind = weather.get('wind_speed', 'неизвестно')

    prompt = f"""
Ты — дружелюбный ассистент, который пишет короткое утреннее сообщение.

Данные о погоде:
Температура: {temp}°C
Ветер: {wind} м/с

Правила:
- Оцени "настроение по погоде" по шкале от 1 до 10.
- Напиши 2 предложения: короткое описание + практичный совет по одежде.
- Тон: тёплый, ненавязчивый.
- Верни строго JSON: {{"score": int, "text": str}}
"""

    try:
        # Создаём новый цикл событий для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        with GigaChat(credentials=credentials, verify_ssl_certs=False) as giga:
            response = giga.chat(
                Chat(
                    messages=[Messages(role=MessagesRole.USER, content=prompt)],
                    model=settings.GIGACHAT_MODEL,
                    temperature=0.7,
                )
            )

        loop.close()
    except Exception as e:
        print(f"ОШИБКА ЗАПРОСА К GigaChat: {type(e).__name__}: {e}")
        return None

    content = response.choices[0].message.content

    # GigaChat может обернуть JSON в markdown-блок, чистим
    if content.startswith("```json"):
        content = content[7:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        print(f"НЕВАЛИДНЫЙ JSON ОТ GigaChat: {content}")
        return None

    score = parsed.get("score")
    text = parsed.get("text", "")

    # GigaChat может вернуть текст списком строк — склеиваем
    if isinstance(text, list):
        text = " ".join(str(t) for t in text)

    if not isinstance(score, int):
        print(f"НЕКОРРЕКТНЫЙ SCORE: {score}")
        return None

    return {"score": max(1, min(10, score)), "text": text[:500]}
