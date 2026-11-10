import httpx
from typing import Optional
from django.conf import settings

YANDEX_URL = "https://api.weather.yandex.ru/graphql/query"


async def fetch_weather(latitude: float, longitude: float) -> Optional[dict]:
    """
    Получить текущую погоду по координатам через API Яндекс Погоды (SmartHome)
    На бесплатном тарифе доступны только базовые поля (temperature, windSpeed)
    Возвращает dict с данными или None при ошибке
    """
    api_key = getattr(settings, 'YANDEX_WEATHER_API_KEY', None)
    if not api_key:
        print("ОШИБКА: YANDEX_WEATHER_API_KEY не задан в settings.py")
        return None

    # Запрашиваем только temperature и windSpeed — они должны быть доступны
    query = """
    {
      weatherByPoint(request: { lat: %s, lon: %s }) {
        now {
          temperature
          windSpeed
        }
      }
    }
    """ % (latitude, longitude)

    headers = {"X-Yandex-Weather-Key": api_key}

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(YANDEX_URL, headers=headers, json={"query": query})
            response.raise_for_status()
            data = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            print(f"ОШИБКА ЗАПРОСА ПОГОДЫ (Яндекс): {type(e).__name__}: {e}")
            return None

    # Проверяем, не вернул ли Яндекс ошибки доступа
    if data.get("errors"):
        print(f"ОШИБКА ЯНДЕКСА (ограничение тарифа): {data['errors']}")
        # Возвращаем хотя бы температуру, если она есть, иначе None
        pass

    try:
        now = data["data"]["weatherByPoint"]["now"]
    except (KeyError, TypeError):
        print(f"НЕОЖИДАННЫЙ ОТВЕТ ОТ ЯНДЕКСА: {data}")
        return None

    # Собираем результат только из тех полей, что реально пришли
    result = {
        "temperature": now.get("temperature"),
        "wind_speed": now.get("windSpeed"),
        "description": "нет данных",  # заглушка, так как cloudiness закрыта
        "precipitation": "нет данных", # заглушка, так как precType закрыта
    }

    # Если температура None — что-то пошло не так, но мы хотя бы не упадём
    if result["temperature"] is None:
        print(f"ВНИМАНИЕ: Яндекс не вернул температуру. Ответ: {data}")
        return None

    return result