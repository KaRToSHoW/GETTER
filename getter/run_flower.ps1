# Скрипт для запуска Flower - веб-интерфейса мониторинга Celery

# Устанавливаем переменную окружения для настроек Django
$env:DJANGO_SETTINGS_MODULE = "getter.settings"
$flowerDb = Join-Path (Get-Location) "flower_db"

# Создаем директорию для базы данных Flower, если она не существует
if (-not (Test-Path $flowerDb)) {
    New-Item -ItemType Directory -Path $flowerDb
}

Write-Output "Запускаем Flower на порту 5556 с персистентным хранилищем..."

# Запускаем Flower с дополнительными параметрами
celery -A getter --broker=redis://localhost:6379/0 flower `
    --port=5556 `
    --persistent=True `
    --db=$flowerDb\flower.db `
    --broker_api=redis://localhost:6379/0 `
    --max-tasks=10000 `
    --tasks-columns=name,uuid,state,received,started,runtime,worker 