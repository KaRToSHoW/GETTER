#!/bin/bash

# Скрипт для деплоймента проекта Getter на сервер

set -e  # Остановка скрипта при ошибке

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Начинаем деплоймент проекта Getter...${NC}"

# Проверка наличия переменных окружения
if [ ! -f .env ]; then
    echo -e "${RED}Ошибка: Файл .env не найден. Создайте его из .env.example${NC}"
    exit 1
fi

# Обновление кода из репозитория
echo -e "${GREEN}Обновление кода из репозитория...${NC}"
git pull

# Активация виртуального окружения
echo -e "${GREEN}Активация виртуального окружения...${NC}"
source venv/bin/activate

# Установка/обновление зависимостей
echo -e "${GREEN}Установка/обновление зависимостей...${NC}"
pip install -r requirements.txt

# Применение миграций
echo -e "${GREEN}Применение миграций базы данных...${NC}"
python manage.py migrate

# Сборка статических файлов
echo -e "${GREEN}Сборка статических файлов...${NC}"
python manage.py collectstatic --noinput

# Перезапуск сервисов
echo -e "${GREEN}Перезапуск сервисов...${NC}"

# Проверка наличия systemd и sudo прав
if command -v systemctl &> /dev/null && [ -d /etc/systemd/system ]; then
    echo -e "${GREEN}Перезапуск Django (Gunicorn)...${NC}"
    sudo systemctl restart getter.service
    
    echo -e "${GREEN}Перезапуск Celery Worker...${NC}"
    sudo systemctl restart getter-celery-worker.service
    
    echo -e "${GREEN}Перезапуск Celery Beat...${NC}"
    sudo systemctl restart getter-celery-beat.service
    
    echo -e "${GREEN}Перезапуск Flower...${NC}"
    sudo systemctl restart getter-flower.service
    
    echo -e "${GREEN}Проверка статуса сервисов...${NC}"
    sudo systemctl status getter.service --no-pager
    sudo systemctl status getter-celery-worker.service --no-pager
    sudo systemctl status getter-celery-beat.service --no-pager
else
    echo -e "${YELLOW}Предупреждение: systemd не найден или нет прав sudo. Ручной перезапуск сервисов:${NC}"
    echo "1. Перезапустите Django (Gunicorn)"
    echo "2. Перезапустите Celery Worker и Beat"
fi

# Проверка наличия Nginx
if command -v nginx &> /dev/null; then
    echo -e "${GREEN}Проверка конфигурации Nginx...${NC}"
    sudo nginx -t
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Перезагрузка Nginx...${NC}"
        sudo systemctl reload nginx
    else
        echo -e "${RED}Ошибка в конфигурации Nginx. Пожалуйста, исправьте и перезапустите вручную.${NC}"
    fi
fi

echo -e "${GREEN}Деплоймент завершен успешно!${NC}" 