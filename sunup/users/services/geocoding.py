import httpx
from typing import Optional

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


async def fetch_city_coordinates(city_name: str) -> Optional[dict]:
    """
    Получить координаты города по названию через Open-Meteo Geocoding API.
    Возвращает dict с полями name, latitude, longitude, country или None, если город не найден.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(
                GEOCODING_URL,
                params={
                    "name": city_name,
                    "count": 1,
                    "language": "ru",
                    "format": "json",
                },
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.RequestError, httpx.HTTPStatusError):
            return None

    results = data.get("results")
    if not results:
        return None

    first = results[0]
    return {
        "name": first["name"],
        "latitude": first["latitude"],
        "longitude": first["longitude"],
        "country": first.get("country", ""),
    }