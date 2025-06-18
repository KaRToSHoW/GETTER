from celery import shared_task
from django.utils import timezone
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.conf import settings
from .models import User
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

@shared_task
def send_inactive_users_reminder(*args, **kwargs) -> Dict[str, int]:
    """
    Периодическая задача для отправки напоминаний неактивным пользователям.
    Отправляет email пользователям, которые не входили в систему более 30 дней.
    
    Returns:
        Словарь с количеством отправленных напоминаний
    """
    # Определяем порог неактивности (30 дней)
    threshold_date = timezone.now() - timezone.timedelta(days=30)
    
    # Получаем неактивных пользователей
    inactive_users = User.objects.filter(
        last_login__lt=threshold_date,
        is_active=True
    )
    
    sent_count = 0
    for user in inactive_users:
        try:
            send_mail(
                'Мы скучаем по вам!',
                f'Здравствуйте, {user.username}!\n\nМы заметили, что вы давно не заходили в наш магазин. '
                f'У нас появилось много новых товаров, которые могут вас заинтересовать.\n\n'
                f'Посетите наш сайт, чтобы узнать о новинках и специальных предложениях!',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
            sent_count += 1
        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания пользователю {user.username}: {e}")
    
    logger.info(f"Отправлено {sent_count} напоминаний неактивным пользователям")
    return {'sent_reminders': sent_count}

@shared_task
def cleanup_inactive_accounts(*args, **kwargs) -> Dict[str, int]:
    """
    Периодическая задача для деактивации учетных записей пользователей,
    которые не входили в систему более 365 дней.
    
    Returns:
        Словарь с количеством деактивированных учетных записей
    """
    # Определяем порог неактивности (365 дней)
    threshold_date = timezone.now() - timezone.timedelta(days=365)
    
    # Деактивируем учетные записи неактивных пользователей
    # Исключаем администраторов
    deactivated = User.objects.filter(
        last_login__lt=threshold_date,
        is_active=True,
        is_superuser=False,
        is_staff=False
    ).update(is_active=False)
    
    logger.info(f"Деактивировано {deactivated} неактивных учетных записей")
    return {'deactivated_accounts': deactivated}

@shared_task
def user_activity_report(*args, **kwargs) -> Dict[str, Any]:
    """
    Периодическая задача для генерации отчета об активности пользователей.
    
    Returns:
        Словарь с данными отчета
    """
    today = timezone.now().date()
    
    # Пользователи, зарегистрировавшиеся за последние 30 дней
    last_30_days = today - timezone.timedelta(days=30)
    new_users = User.objects.filter(date_joined__gte=last_30_days).count()
    
    # Активные пользователи за последние 7 дней
    last_7_days = today - timezone.timedelta(days=7)
    active_users = User.objects.filter(last_login__gte=last_7_days).count()
    
    # Общее количество пользователей
    total_users = User.objects.count()
    active_percent = (active_users / total_users * 100) if total_users > 0 else 0
    
    report = {
        'date': today.strftime('%Y-%m-%d'),
        'total_users': total_users,
        'new_users_30d': new_users,
        'active_users_7d': active_users,
        'active_percent': round(active_percent, 2)
    }
    
    logger.info(f"Сгенерирован отчет об активности пользователей: {report}")
    return report 