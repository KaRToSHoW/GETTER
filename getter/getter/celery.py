import os
from celery import Celery
from django.conf import settings
from typing import Any, List

# Установка переменной окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'getter.settings')

# Создание экземпляра приложения Celery
app = Celery('getter')

# Загрузка конфигурации из настроек Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение и регистрация задач из всех приложений Django
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(bind=True, ignore_result=True)
def debug_task(self: Any) -> None:
    """
    Отладочная задача для проверки работы Celery.
    
    Args:
        self: Экземпляр задачи
    """
    print(f'Request: {self.request!r}') 