#!/usr/bin/env python
"""
Скрипт для запуска Celery beat.
"""
import os
import subprocess
from django.conf import settings

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'getter.settings')
    
    # Запуск Celery beat с дополнительными параметрами
    subprocess.call([
        'celery', 
        '-A', 'getter', 
        'beat', 
        '--loglevel=info', 
        '--scheduler', 'django_celery_beat.schedulers:DatabaseScheduler',
        '--pidfile=', # Отключаем создание pid-файла, чтобы избежать конфликтов
    ]) 