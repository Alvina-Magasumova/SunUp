def build_digest_message(
    city_name: str,
    weather: dict,
    mood: dict,
    news_by_topic: dict,
) -> str:
    """Собрать итоговое сообщение для отправки пользователю"""
    temp = weather.get('temperature', '—')
    wind = weather.get('wind_speed', '—')
    mood_score = mood.get('score', '—')
    mood_text = mood.get('text', '')

    lines = [
        f"☀️ Доброе утро!",
        f"",
        f"📍 {city_name}",
        f"🌡 Температура: {temp}°C, ветер {wind} м/с",
        f"",
        f"🌤 Настроение по погоде: {mood_score}/10",
        f"«{mood_text}»",
        f"",
    ]

    if news_by_topic:
        lines.append("📰 Главное за ночь:")
        for topic_name, articles in news_by_topic.items():
            lines.append(f"")
            lines.append(f"▫️ {topic_name}:")
            for item in articles:
                # Выводим заголовок и ссылку на следующей строке
                lines.append(f"  • {item['title']}")
                if item.get('link'):
                    lines.append(f"    {item['link']}")
    else:
        lines.append("📰 Новостей пока нет.")

    return "\n".join(lines)