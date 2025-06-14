# Скрипт для тестирования системы Celery
# Этот скрипт запускает Redis, Celery worker, Celery beat и Flower в отдельных окнах PowerShell

# Текущий путь к проекту
$projectPath = Get-Location

# Запускаем Redis в Docker
Write-Output "Запуск Redis..."
# Выполняем содержимое скрипта run_redis.ps1 напрямую
$redisScript = Get-Content -Path "$projectPath\run_redis.ps1" -Raw
Invoke-Expression $redisScript

# Даем Redis время на запуск
Start-Sleep -Seconds 3

# Запускаем Celery worker
Write-Output "Запуск Celery worker..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; python run_celery_worker.py"

# Даем worker время на запуск
Start-Sleep -Seconds 3

# Запускаем Celery beat
Write-Output "Запуск Celery beat..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; python run_celery_beat.py"

# Даем beat время на запуск
Start-Sleep -Seconds 3

# Запускаем Flower
Write-Output "Запуск Flower..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; .\run_flower.ps1"

# Даем Flower время на запуск
Start-Sleep -Seconds 3

# Запускаем тестовые задачи
Write-Output "Запуск тестовых задач..."
python manage.py test_celery_tasks update_product_availability --async --repeat 3 --countdown 5
python manage.py test_celery_tasks calculate_product_ratings --async --countdown 10
python manage.py test_celery_tasks generate_daily_sales_report --async --countdown 15

Write-Output "Система Celery запущена и работает!"
Write-Output "Flower доступен по адресу: http://localhost:5555"
Write-Output "Для остановки закройте все открытые окна PowerShell." 