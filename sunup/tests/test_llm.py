from unittest.mock import patch, MagicMock
from digest.services.llm import generate_mood


@patch("digest.services.llm.GigaChat")
def test_generate_mood_success(mock_gigachat):
    """Проверяем, что настроение парсится из ответа GigaChat"""
    mock_instance = MagicMock()
    mock_instance.__enter__.return_value = mock_instance
    mock_instance.chat.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content='{"score": 7, "text": "Хорошая погода"}'))]
    )
    mock_gigachat.return_value = mock_instance

    weather = {"temperature": 11, "wind_speed": 3.6}
    result = generate_mood(weather)

    assert result is not None
    assert result["score"] == 7
    assert result["text"] == "Хорошая погода"


@patch("digest.services.llm.GigaChat")
def test_generate_mood_invalid_json(mock_gigachat):
    """Если GigaChat вернул невалидный JSON — возвращается None"""
    mock_instance = MagicMock()
    mock_instance.__enter__.return_value = mock_instance
    mock_instance.chat.return_value = MagicMock(
        choices=[MagicMock(message=MagicMock(content="это не json"))]
    )
    mock_gigachat.return_value = mock_instance

    weather = {"temperature": 11, "wind_speed": 3.6}
    result = generate_mood(weather)
    assert result is None