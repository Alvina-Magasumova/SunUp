from unittest.mock import patch
from digest.services.news import fetch_news


@patch("digest.services.news.feedparser.parse")
def test_fetch_news_success(mock_parse):
    """Проверяем, что новости парсятся из RSS"""
    mock_parse.return_value = type(
        "Feed", (), {
            "bozo": False,
            "entries": [
                {"title": "Новость 1", "link": "https://rbc.ru/1"},
                {"title": "Новость 2", "link": "https://rbc.ru/2"},
            ]
        }
    )()

    # Создаем фейковый объект Topic
    class FakeTopic:
        name = "Наука"
        rss_url = "https://nplus1.ru/rss"

    result = fetch_news([FakeTopic()], max_per_topic=2)
    assert result is not None
    assert "Наука" in result
    assert len(result["Наука"]) == 2
    assert result["Наука"][0]["title"] == "Новость 1"


@patch("digest.services.news.feedparser.parse")
def test_fetch_news_empty(mock_parse):
    """Если лента пуста — темы не попадают в результат"""
    mock_parse.return_value = type("Feed", (), {"bozo": False, "entries": []})()

    class FakeTopic:
        name = "Наука"
        rss_url = "https://nplus1.ru/rss"

    result = fetch_news([FakeTopic()], max_per_topic=2)
    assert result == {}