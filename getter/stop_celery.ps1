# Скрипт для остановки всех процессов Celery

Write-Output "Остановка процессов Celery..."

# Находим и останавливаем процессы Celery
$celeryProcesses = Get-Process | Where-Object { $_.ProcessName -like "*celery*" -or $_.CommandLine -like "*celery*" }
if ($celeryProcesses) {
    $celeryProcesses | ForEach-Object {
        Write-Output "Останавливаем процесс: $($_.Id) $($_.ProcessName)"
        Stop-Process -Id $_.Id -Force
    }
} else {
    Write-Output "Процессы Celery не найдены"
}

# Находим и останавливаем процессы Python, которые могут быть связаны с Celery
$pythonProcesses = Get-Process -Name python | Where-Object { $_.CommandLine -like "*celery*" -or $_.CommandLine -like "*flower*" }
if ($pythonProcesses) {
    $pythonProcesses | ForEach-Object {
        Write-Output "Останавливаем Python процесс: $($_.Id)"
        Stop-Process -Id $_.Id -Force
    }
} else {
    Write-Output "Python процессы Celery не найдены"
}

Write-Output "Все процессы Celery остановлены" 