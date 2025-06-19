#!/usr/bin/env python
"""
Скрипт для запуска Celery worker.
"""
import os
import subprocess

# Установка переменной окружения для настроек Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "getter.settings")

if __name__ == "__main__":
    # Запуск Celery worker с событиями для мониторинга
    # Используем solo pool вместо prefork для обхода ошибки with _loc
    subprocess.call([
        'celery', 
        '-A', 'getter', 
        'worker', 
        '--loglevel=info',
        '--events',  # Включаем события для мониторинга в Flower
        '--pool=solo',  # Используем solo pool для обхода проблемы с billiard
        '-Ofair',  # Используем fair scheduling для более предсказуемого выполнения задач
    ])