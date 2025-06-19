from celery import shared_task
from django.utils import timezone
from django.db.models import Avg, Count, F, Sum
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Order, Category, Review
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

@shared_task
def update_product_availability(*args, **kwargs) -> Dict[str, int]:
    """
    Периодическая задача для обновления доступности товаров.
    Товары с нулевым количеством помечаются как недоступные.
    
    Returns:
        Словарь с количеством обновленных товаров
    """
    updated = Product.objects.filter(stock=0, is_available=True).update(is_available=False)
    logger.info(f"Обновлено {updated} товаров со статусом 'недоступен'")
    
    # Также можно помечать товары как доступные, если они снова в наличии
    restored = Product.objects.filter(stock__gt=0, is_available=False).update(is_available=True)
    logger.info(f"Восстановлено {restored} товаров со статусом 'доступен'")
    
    return {'updated': updated, 'restored': restored}

@shared_task
def generate_daily_sales_report() -> Dict[str, Any]:
    """
    Периодическая задача для генерации ежедневного отчета о продажах.
    
    Returns:
        Словарь с данными отчета
    """
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    
    # Получаем заказы за вчерашний день
    orders = Order.objects.filter(
        created_at__date=yesterday
    )
    
    # Вычисляем статистику
    total_orders = orders.count()
    total_revenue = orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Самые продаваемые категории
    top_categories = Category.objects.filter(
        products__order_items__order__in=orders
    ).annotate(
        sales_count=Count('products__order_items')
    ).order_by('-sales_count')[:5]
    
    # Формируем отчет
    report = {
        'date': yesterday.strftime('%Y-%m-%d'),
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'top_categories': [
            {'name': cat.name, 'sales': cat.sales_count} 
            for cat in top_categories
        ]
    }
    
    logger.info(f"Сгенерирован отчет о продажах за {yesterday}")
    

    
    return report

@shared_task
def update_order_statuses(*args, **kwargs) -> Dict[str, int]:
    """
    Периодическая задача для автоматического обновления статусов заказов
    на основе времени их создания/обновления.
    
    Returns:
        Словарь с количеством обновленных заказов по статусам
    """
    from .models import Order
    
    updated_counts = {'canceled': 0, 'delivered': 0}
    
    # Получаем все заказы в ожидании или отправленные
    orders = Order.objects.filter(status__in=['pending', 'shipped'])
    
    for order in orders:
        # Вызываем метод обновления статуса для каждого заказа
        if order.update_status_by_time():
            if order.status == 'canceled':
                updated_counts['canceled'] += 1
            elif order.status == 'delivered':
                updated_counts['delivered'] += 1
    
    logger.info(f"Обновлены статусы заказов: {updated_counts}")
    return updated_counts

@shared_task
def calculate_product_ratings() -> Dict[str, int]:
    """
    Периодическая задача для пересчета средних рейтингов товаров.
    
    Returns:
        Словарь с количеством обновленных товаров и средним рейтингом
    """
    products_with_reviews = Product.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).filter(review_count__gt=0)
    
    count = products_with_reviews.count()
    avg_site_rating = products_with_reviews.aggregate(Avg('avg_rating'))['avg_rating__avg'] or 0
    
    logger.info(f"Пересчитаны рейтинги для {count} товаров. Средний рейтинг по сайту: {avg_site_rating:.2f}")
    
    return {
        'updated_products': count,
        'average_site_rating': float(avg_site_rating)
    }

@shared_task
def clean_old_reviews(*args, **kwargs) -> Dict[str, int]:
    """
    Периодическая задача для удаления отзывов без текста или с некорректными комментариями.
    
    Returns:
        Словарь с количеством удаленных отзывов
    """
    # Удаляем отзывы без комментария
    deleted_empty, _ = Review.objects.filter(
        comment__isnull=True
    ).delete()
    
    # Для удаления отзывов с некорректными комментариями, содержащими <generator object>,
    # нужно проверить каждый отзыв индивидуально, так как Django ORM не поддерживает поиск по таким строкам
    deleted_invalid = 0
    reviews = Review.objects.all()
    for review in reviews:
        comment_str = str(review.comment)
        if "<generator object" in comment_str:
            review.delete()
            deleted_invalid += 1
    
    total_deleted = deleted_empty + deleted_invalid
    
    logger.info(f"Удалено {deleted_empty} отзывов без текста и {deleted_invalid} отзывов с некорректными комментариями")
    
    return {'deleted_reviews': total_deleted} 