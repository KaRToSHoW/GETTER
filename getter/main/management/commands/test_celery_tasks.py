from django.core.management.base import BaseCommand
from main.tasks import (
    update_product_availability,
    generate_daily_sales_report,
    update_order_statuses,
    calculate_product_ratings,
    clean_old_reviews
)
from users.tasks import (
    send_inactive_users_reminder,
    cleanup_inactive_accounts,
    user_activity_report
)
import time
from typing import Any, Optional


class Command(BaseCommand):
    """
    Команда для тестирования задач Celery.
    Запускает выбранную задачу и выводит результат.
    """
    help = 'Тестирование задач Celery'

    def add_arguments(self, parser: Any) -> None:
        """
        Добавляет аргументы командной строки.
        
        Args:
            parser: Парсер аргументов
        """
        parser.add_argument(
            'task',
            type=str,
            help='Имя задачи для запуска',
            choices=[
                'update_product_availability',
                'generate_daily_sales_report',
                'update_order_statuses',
                'calculate_product_ratings',
                'clean_old_reviews',
                'send_inactive_users_reminder',
                'cleanup_inactive_accounts',
                'user_activity_report',
                'all'
            ]
        )
        
        parser.add_argument(
            '--async',
            action='store_true',
            dest='async_mode',
            help='Запустить задачу асинхронно'
        )
        
        parser.add_argument(
            '--countdown',
            type=int,
            default=0,
            help='Задержка перед выполнением задачи (в секундах)'
        )
        
        parser.add_argument(
            '--repeat',
            type=int,
            default=1,
            help='Количество повторений задачи'
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        """
        Обработчик команды.
        
        Args:
            args: Позиционные аргументы
            options: Именованные аргументы
            
        Returns:
            Сообщение о результате выполнения
        """
        task_name = options['task']
        async_mode = options.get('async_mode', False)
        countdown = options.get('countdown', 0)
        repeat = options.get('repeat', 1)
        
        tasks = {
            'update_product_availability': update_product_availability,
            'generate_daily_sales_report': generate_daily_sales_report,
            'update_order_statuses': update_order_statuses,
            'calculate_product_ratings': calculate_product_ratings,
            'clean_old_reviews': clean_old_reviews,
            'send_inactive_users_reminder': send_inactive_users_reminder,
            'cleanup_inactive_accounts': cleanup_inactive_accounts,
            'user_activity_report': user_activity_report,
        }
        
        if task_name == 'all':
            self.stdout.write(self.style.WARNING('Запуск всех задач...'))
            results = {}
            
            for name, task in tasks.items():
                self.stdout.write(f"Запуск задачи: {name}")
                
                for i in range(repeat):
                    if async_mode:
                        result = task.apply_async(countdown=countdown)
                        self.stdout.write(f"Задача {name} #{i+1} запущена асинхронно, ID: {result.id}")
                    else:
                        results[f"{name}_{i+1}"] = task()
            
            if not async_mode:
                for name, result in results.items():
                    self.stdout.write(f"{name}: {result}")
                
            self.stdout.write(self.style.SUCCESS('Все задачи выполнены или запланированы'))
            return
        
        if task_name in tasks:
            task = tasks[task_name]
            self.stdout.write(self.style.WARNING(f'Запуск задачи {task_name}...'))
            
            results = []
            
            for i in range(repeat):
                if async_mode:
                    result = task.apply_async(countdown=countdown)
                    self.stdout.write(f"Задача запущена асинхронно #{i+1}. ID: {result.id}, задержка: {countdown} сек.")
                    
                    # Добавляем небольшую задержку между запусками для лучшей видимости в Flower
                    if repeat > 1 and i < repeat - 1:
                        time.sleep(0.5)
                else:
                    start_time = time.time()
                    task_result = task()
                    execution_time = time.time() - start_time
                    results.append(task_result)
                    
                    self.stdout.write(self.style.SUCCESS(
                        f"Задача #{i+1} выполнена за {execution_time:.2f} сек. Результат: {task_result}"
                    ))
            
            if async_mode:
                self.stdout.write(self.style.SUCCESS(f"Запланировано {repeat} выполнений задачи {task_name}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Все {repeat} выполнений задачи {task_name} завершены"))
        else:
            self.stdout.write(self.style.ERROR(f'Задача {task_name} не найдена'))
            return 