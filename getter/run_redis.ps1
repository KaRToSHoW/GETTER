# Скрипт для запуска Redis в Docker

# Проверяем, запущен ли уже контейнер с Redis
$running = docker ps --filter "name=redis-getter" --format "{{.ID}}"

if ($running) {
    Write-Output "Redis уже запущен в контейнере $running"
} else {
    # Проверяем, существует ли остановленный контейнер
    $stopped = docker ps -a --filter "status=exited" --filter "name=redis-getter" --format "{{.ID}}"
    
    if ($stopped) {
        Write-Output "Запускаем существующий контейнер Redis..."
        docker start $stopped
    } else {
        Write-Output "Создаем и запускаем новый контейнер Redis..."
        docker run -d --name redis-getter -p 6379:6379 redis
    }
}

Write-Output "Redis запущен и доступен на localhost:6379"