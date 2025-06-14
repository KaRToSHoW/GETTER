# Скрипт для запуска системы Celery
# Этот скрипт запускает Redis, Celery worker, Celery beat и Flower

# Сначала останавливаем все существующие процессы Celery
Write-Output "Остановка существующих процессов Celery..."
try {
    $celeryProcesses = Get-Process | Where-Object { $_.ProcessName -like "*celery*" -or $_.CommandLine -like "*celery*" }
    if ($celeryProcesses) {
        $celeryProcesses | ForEach-Object {
            Write-Output "Останавливаем процесс: $($_.Id)"
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    $pythonProcesses = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*celery*" -or $_.CommandLine -like "*flower*" }
    if ($pythonProcesses) {
        $pythonProcesses | ForEach-Object {
            Write-Output "Останавливаем Python процесс: $($_.Id)"
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
} catch {
    Write-Output "Ошибка при остановке процессов: $_"
}

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
Start-Sleep -Seconds 5

# Запускаем Celery beat
Write-Output "Запуск Celery beat..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; python run_celery_beat.py"

# Даем beat время на запуск
Start-Sleep -Seconds 3

# Запускаем Flower на другом порту (5556)
Write-Output "Запуск Flower..."
$env:DJANGO_SETTINGS_MODULE = "getter.settings"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$projectPath'; celery -A getter --broker=redis://localhost:6379/0 flower --port=5556"

# Даем Flower время на запуск
Start-Sleep -Seconds 3

# Запускаем тестовую задачу
Write-Output "Запуск тестовой задачи..."
python manage.py test_celery_tasks update_product_availability

Write-Output "Система Celery запущена и работает!"
Write-Output "Flower доступен по адресу: http://localhost:5556"
Write-Output "Для остановки запустите скрипт stop_celery.ps1" 