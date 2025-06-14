"""
Настройки расписания периодических задач Celery.
"""

from celery.schedules import crontab
from typing import Dict, Any

# Расписание периодических задач
CELERY_BEAT_SCHEDULE: Dict[str, Dict[str, Any]] = {
    # Задачи для приложения main
    'update_product_availability': {
        'task': 'main.tasks.update_product_availability',
        'schedule': crontab(minute='0', hour='*/3'),  # Каждые 3 часа
        'options': {'expires': 3600}  # Задача истекает через 1 час
    },
    'generate_daily_sales_report': {
        'task': 'main.tasks.generate_daily_sales_report',
        'schedule': crontab(minute='0', hour='7'),  # Каждый день в 7:00
        'options': {'expires': 7200}  # Задача истекает через 2 часа
    },
    'update_order_statuses': {
        'task': 'main.tasks.update_order_statuses',
        'schedule': crontab(minute='*/30'),  # Каждые 30 минут
        'options': {'expires': 1800}  # Задача истекает через 30 минут
    },
    'calculate_product_ratings': {
        'task': 'main.tasks.calculate_product_ratings',
        'schedule': crontab(minute='0', hour='3'),  # Каждый день в 3:00
        'options': {'expires': 7200}  # Задача истекает через 2 часа
    },
    'clean_old_reviews': {
        'task': 'main.tasks.clean_old_reviews',
        'schedule': crontab(minute='0', hour='2', day_of_week='1'),  # Каждый понедельник в 2:00
        'options': {'expires': 14400}  # Задача истекает через 4 часа
    },
    
    # Задачи для приложения users
    'send_inactive_users_reminder': {
        'task': 'users.tasks.send_inactive_users_reminder',
        'schedule': crontab(minute='0', hour='10', day_of_week='1,4'),  # Понедельник и четверг в 10:00
        'options': {'expires': 7200}  # Задача истекает через 2 часа
    },
    'cleanup_inactive_accounts': {
        'task': 'users.tasks.cleanup_inactive_accounts',
        'schedule': crontab(minute='0', hour='1', day_of_month='1'),  # Первое число каждого месяца в 1:00
        'options': {'expires': 14400}  # Задача истекает через 4 часа
    },
    'user_activity_report': {
        'task': 'users.tasks.user_activity_report',
        'schedule': crontab(minute='0', hour='6', day_of_week='1'),  # Каждый понедельник в 6:00
        'options': {'expires': 7200}  # Задача истекает через 2 часа
    },
} 