import os
from celery import Celery

# Говорим Celery, где настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sunup.settings')

app = Celery('sunup')

# Читаем настройки Celery из settings.py с префиксом CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находим задачи во всех приложениях (tasks.py)
app.autodiscover_tasks()