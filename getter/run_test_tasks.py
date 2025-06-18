import os
import time
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'getter.settings')
django.setup()

# Импортируем задачи
from main.tasks import (
    update_product_availability,
    update_order_statuses,
    calculate_product_ratings,
    generate_daily_sales_report,
    clean_old_reviews
)
from users.tasks import send_inactive_users_reminder

if __name__ == "__main__":
    print("Запуск серии тестовых задач Celery...")
    
    # Запуск каждой задачи и печать результата
    print("\n1. Запуск update_product_availability")
    task1 = update_product_availability.delay()
    print(f"Задача {task1.id} отправлена")
    
    # Небольшая пауза между задачами
    time.sleep(2)
    
    print("\n2. Запуск update_order_statuses")
    task2 = update_order_statuses.delay()
    print(f"Задача {task2.id} отправлена")
    
    time.sleep(2)
    
    print("\n3. Запуск calculate_product_ratings")
    task3 = calculate_product_ratings.delay()
    print(f"Задача {task3.id} отправлена")
    
    time.sleep(2)
    
    print("\n4. Запуск generate_daily_sales_report")
    task4 = generate_daily_sales_report.delay()
    print(f"Задача {task4.id} отправлена")
    
    time.sleep(2)
    
    print("\n5. Запуск clean_old_reviews")
    task5 = clean_old_reviews.delay()
    print(f"Задача {task5.id} отправлена")
    
    time.sleep(2)
    
    print("\n6. Запуск send_inactive_users_reminder")
    task6 = send_inactive_users_reminder.delay()
    print(f"Задача {task6.id} отправлена")
    
    print("\nВсе тестовые задачи отправлены. Проверьте их статус в Flower: http://localhost:5556") 