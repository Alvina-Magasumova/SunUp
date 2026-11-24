markdown
# ☀️ SunUp — Утренний дайджест с AI

**SunUp** — это веб-сервис, который каждое утро присылает пользователю на электронную почту персональный дайджест: прогноз погоды в выбранном городе, свежие новости по интересующим темам и «настроение дня», сгенерированное искусственным интеллектом.

Проект разработан как демонстрация навыков промышленной бэкенд-разработки на Python/Django: от проектирования базы данных и работы с внешними API до настройки фоновых задач, контейнеризации и деплоя на реальный сервер.

---

## 🚀 Живая демонстрация
* **Рабочий сервис:** 👉 [https://sunup-app.site](https://sunup-app.site)
* **Документация API (Swagger):** 👉 [https://sunup-app.site/api/docs/](https://sunup-app.site/api/docs/)

---

## 🛠 Технологический стек

**Бэкенд:**
* **Python 3.9**
* **Django 4.2** + **Django REST Framework** (REST API)
* **PostgreSQL 15** (основная база данных)
* **Celery + Celery Beat + Redis** (асинхронные задачи и планировщик)
* **JWT** (`djangorestframework-simplejwt`) для аутентификации
* **drf-spectacular** (Swagger / OpenAPI документация)

**Фронтенд:**
* Django Templates
* Bootstrap 5
* Vanilla JavaScript (Fetch API для работы с REST API)

**Инфраструктура и деплой:**
* **Docker** и **Docker Compose** (контейнеризация всех сервисов)
* **Nginx** (reverse proxy)
* **Let's Encrypt (Certbot)** для HTTPS

**Внешние интеграции:**
* **Open-Meteo Geocoding API** — определение координат и часового пояса по названию города.
* **Яндекс Погода (SmartHome API)** — данные о текущей погоде.
* **RSS-ленты** (Хабр, N+1, РБК, Чемпионат) — парсинг свежих новостей (`feedparser`).
* **GigaChat (Сбер)** — генерация «настроения дня» и рекомендации через LLM.

---

## 📋 Основной функционал

1. **Регистрация и аутентификация:** регистрация с подтверждением email по токену и вход через JWT-токены.
2. **Личный кабинет:** пользователь указывает город (координаты и часовой пояс подтягиваются автоматически), выбирает интересующие темы новостей и настраивает время отправки дайджеста по местному времени.
3. **Пайплайн дайджеста (Celery Beat):** каждую минуту планировщик проверяет расписание пользователей с учётом их часового пояса и защиты от дублирующих отправок.
4. **Сбор данных:** фоновая задача получает погоду по координатам, парсит новости из RSS-лент и запрашивает оценку дня у GigaChat.
5. **Email-доставка:** готовый дайджест отправляется на почту пользователя через SMTP.
6. **Абстракция каналов:** реализован паттерн `NotificationChannel`, позволяющий легко масштабировать доставку на мессенджеры (Telegram / MAX) в будущем.


## 🧠 Архитектура проекта

Проект разделён на два основных Django-приложения:
* `users` — кастомная модель пользователя, темы, регистрация с подтверждением почты, JWT-авторизация, геокодинг и API профиля.
* `digest` — модели дайджестов, периодические задачи Celery, интеграции с Яндекс Погодой, RSS и GigaChat, каналы доставки.

**Схема работы:**
```text
Пользователь -> Django (API) -> PostgreSQL
                    |
Celery Beat (каждую минуту) -> Redis -> Celery Worker
                                          |
       -----------------------------------------------------

       |                    |                              |
  Яндекс Погода         RSS Новости                    GigaChat (LLM)

       |                    |                              |
       -----------------------------------------------------
                              |
                      Сборка сообщения
                              |
                     Email (SMTP Yandex)
```

---

## ⚙️ Как запустить проект локально

### Вариант 1. Запуск через Docker (рекомендуется)
Для запуска понадобятся **Docker** и **Docker Compose**.

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com
   cd SunUp
   ```

2. **Создайте файл `.env` в корне проекта** и заполните переменные окружения:
   ```env
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost

   DB_NAME=sunup
   DB_USER=postgres
   DB_PASSWORD=postgres
   DB_HOST=db
   DB_PORT=5432

   REDIS_URL=redis://redis:6379/0

   YANDEX_WEATHER_API_KEY=your-yandex-weather-key
   GIGACHAT_CREDENTIALS=your-gigachat-auth-key

   EMAIL_HOST=smtp.yandex.ru
   EMAIL_PORT=465
   EMAIL_USE_SSL=True
   EMAIL_HOST_USER=your-email@yandex.ru
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=SunUp <your-email@yandex.ru>
   ```

3. **Запустите контейнеры:**
   ```bash
   docker compose up -d --build
   ```

4. **Создайте суперпользователя** (миграции применяются автоматически при старте контейнера `web`):
   ```bash
   docker compose exec web python sunup/manage.py createsuperuser
   ```

5. **Откройте проект в браузере:**
   * Главная страница: `http://localhost:8000`
   * Swagger API: `http://localhost:8000/api/docs/`
   * Админ-панель: `http://localhost:8000/admin/`

### Вариант 2. Локальный запуск (без Docker)

1. **Создайте виртуальное окружение и установите зависимости:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Для Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Настройте `.env`** (см. выше) и убедитесь, что локально запущены PostgreSQL и Redis.

3. **Примените миграции и запустите сервер:**
   ```bash
   python sunup/manage.py migrate
   python sunup/manage.py runserver
   ```

4. **В отдельных терминалах запустите Celery Worker и Celery Beat:**
   ```bash
   cd sunup
   celery -A sunup worker --loglevel=info --pool=solo
   celery -A sunup beat --loglevel=info
   ```

---

## 🧪 Тестирование

Для запуска тестов используется `pytest`:
```bash
pytest
```

---

## 📝 Планы по развитию (To-Do)

- [ ] Подключение Telegram-бота для отправки дайджестов.
- [ ] Добавление пользовательских RSS-лент в личном кабинете.
- [ ] История отправленных дайджестов в личном кабинете пользователя.

---

## 👩‍💻 Автор

**Альвина Магасумова** — Python / Django Developer  
GitHub: [Alvina-Magasumova](https://github.com)