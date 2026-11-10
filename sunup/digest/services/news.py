import feedparser


def fetch_news(topics: list, max_per_topic: int = 2) -> dict:
    """
    Получить новости по темам пользователя
    Принимает список объектов Topic (у каждого есть .name и .rss_url)
    Возвращает dict: {topic_name: [{"title": ..., "link": ...}, ...]}
    """
    result = {}

    for topic in topics:
        if not topic.rss_url:
            continue

        try:
            feed = feedparser.parse(topic.rss_url)
        except Exception as e:
            print(f"ОШИБКА ПАРСИНГА RSS ({topic.name}): {type(e).__name__}: {e}")
            continue

        if feed.bozo:
            print(f"ПРЕДУПРЕЖДЕНИЕ RSS ({topic.name}): {feed.bozo_exception}")

        articles = []
        for entry in feed.entries[:max_per_topic]:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
            })

        if articles:
            result[topic.name] = articles

    return result