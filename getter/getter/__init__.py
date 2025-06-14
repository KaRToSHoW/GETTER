"""
Инициализация проекта Getter.
Включает настройку Celery для асинхронных задач.
"""

# Импорт конфигурации Celery
from .celery import app as celery_app

__all__ = ['celery_app']
