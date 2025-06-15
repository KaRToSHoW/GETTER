# Скрипт для запуска Flower - веб-интерфейса мониторинга Celery

# Устанавливаем переменную окружения для настроек Django
$env:DJANGO_SETTINGS_MODULE = "getter.settings"
 
Write-Output "Запуск Flower на http://localhost:5555"
celery -A getter --broker=redis://localhost:6379/0 flower --port=5555 