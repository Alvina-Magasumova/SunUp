import pytest
import respx
from httpx import Response
from digest.services.weather import fetch_weather


@pytest.mark.asyncio
@respx.mock
async def test_fetch_weather_success():
    """Проверяем, что погода парсится правильно"""
    respx.post("https://api.weather.yandex.ru/graphql/query").mock(
        return_value=Response(
            200,
            json={
                "data": {
                    "weatherByPoint": {
                        "now": {"temperature": 11, "windSpeed": 3.6}
                    }
                }
            },
        )
    )
    result = await fetch_weather(55.75, 37.62)
    assert result is not None
    assert result["temperature"] == 11
    assert result["wind_speed"] == 3.6


@pytest.mark.asyncio
@respx.mock
async def test_fetch_weather_error():
    """Проверяем, что при ошибке API возвращается None"""
    respx.post("https://api.weather.yandex.ru/graphql/query").mock(
        return_value=Response(500)
    )
    result = await fetch_weather(55.75, 37.62)
    assert result is None