#!/usr/bin/env python
"""
Скрипт для запуска Celery worker.
"""
import os
import subprocess

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'getter.settings')
    
    # Упрощенный запуск Celery worker
    subprocess.call([
        'celery', 
        '-A', 'getter', 
        'worker', 
        '--loglevel=info'
    ]) 