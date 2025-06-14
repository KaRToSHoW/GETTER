# Настройка и запуск Celery в проекте Getter

## Установка

Для работы Celery необходимы следующие пакеты:

```bash
pip install celery redis django-celery-beat
```

## Запуск Redis

Перед запуском Celery необходимо запустить Redis сервер:

### Windows

Для Windows рекомендуется использовать Redis через WSL или Docker:

```bash
# Через Docker
docker run -d -p 6379:6379 redis
```

### Linux/Mac

```bash
# Установка Redis (Ubuntu)
sudo apt-get install redis-server

# Запуск Redis
sudo service redis-server start

# Проверка статуса
redis-cli ping
# Должен ответить: PONG
```

## Запуск Celery

### Запуск Celery Worker

```bash
# Из корневой директории проекта
python run_celery_worker.py

# Или напрямую через Celery CLI
celery -A getter worker --loglevel=info
```

### Запуск Celery Beat (планировщик)

```bash
# Из корневой директории проекта
python run_celery_beat.py

# Или напрямую через Celery CLI
celery -A getter beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

## Настройка периодических задач

Периодические задачи настраиваются в файле `getter/celery_schedule.py`.

Текущие периодические задачи:

### Приложение main

1. **update_product_availability** - Обновление доступности товаров (каждые 3 часа)
2. **generate_daily_sales_report** - Генерация ежедневного отчета о продажах (каждый день в 7:00)
3. **update_order_statuses** - Обновление статусов заказов (каждые 30 минут)
4. **calculate_product_ratings** - Пересчет рейтингов товаров (каждый день в 3:00)
5. **clean_old_reviews** - Удаление старых отзывов без текста (каждый понедельник в 2:00)

### Приложение users

1. **send_inactive_users_reminder** - Отправка напоминаний неактивным пользователям (понедельник и четверг в 10:00)
2. **cleanup_inactive_accounts** - Деактивация неактивных учетных записей (первое число каждого месяца в 1:00)
3. **user_activity_report** - Генерация отчета об активности пользователей (каждый понедельник в 6:00)

## Управление задачами через Django Admin

После миграций вы можете управлять периодическими задачами через Django Admin панель в разделе "Periodic Tasks".

## Запуск задач вручную

Для тестирования задачи можно запустить вручную:

```python
from main.tasks import update_product_availability
result = update_product_availability.delay()
print(result.get())  # Получение результата задачи
```

## Мониторинг

Для мониторинга Celery задач рекомендуется использовать Flower:

```bash
pip install flower
celery -A getter flower
```

После установки и запуска Flower будет доступен по адресу: http://localhost:5555 