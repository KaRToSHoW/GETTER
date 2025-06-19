# Getter - Интернет-магазин электроники

Getter — это современный интернет-магазин электроники, разработанный на Django и Vue.js. Проект включает в себя административную панель, каталог товаров, корзину, систему заказов и многое другое.

## Содержание
- [Технологии](#технологии)
- [Требования](#требования)
- [Установка](#установка)
  - [Бэкенд](#бэкенд)
  - [Фронтенд](#фронтенд)
- [Настройка переменных окружения](#настройка-переменных-окружения)
- [Работа с базой данных](#работа-с-базой-данных)
- [Запуск проекта](#запуск-проекта)
  - [Режим разработки](#режим-разработки)
  - [Продакшен](#продакшен)
- [Celery для фоновых задач](#celery-для-фоновых-задач)
- [API Документация](#api-документация)
- [Тестирование](#тестирование)
- [Деплоймент](#деплоймент)

## Технологии

### Бэкенд
- Python 3.9+
- Django 5.1.4
- Django REST Framework
- PostgreSQL (опционально, по умолчанию SQLite)
- Celery + Redis (фоновые задачи)
- JWT для аутентификации

### Фронтенд
- Vue.js 2
- Vuex
- Vue Router
- Bootstrap 5

## Требования

- Python 3.9+
- Node.js 16+
- Redis (для Celery)
- PostgreSQL (опционально)

## Установка

### Клонирование репозитория

```bash
git clone https://github.com/yourusername/getter.git
cd getter
```

### Бэкенд

1. Создайте и активируйте виртуальное окружение:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта (можно скопировать из `.env.example`):

```bash
cp .env.example .env
```

4. Выполните миграции базы данных:

```bash
python manage.py migrate
```

5. Создайте суперпользователя:

```bash
python manage.py createsuperuser
```

6. Загрузите тестовые данные (опционально):

```bash
python manage.py generate_products
```

### Фронтенд

1. Перейдите в директорию фронтенда:

```bash
cd ../frontend
```

2. Установите зависимости:

```bash
npm install
```

## Настройка переменных окружения

Для правильной работы проекта необходимо настроить переменные окружения в файле `.env`. Ключевые переменные:

| Переменная | Описание | Пример |
|------------|----------|--------|
| DEBUG | Режим отладки (True/False) | True для разработки, False для продакшена |
| SECRET_KEY | Секретный ключ Django | django-insecure-*^45df%6t... |
| ALLOWED_HOSTS | Разрешенные хосты | localhost,127.0.0.1,example.com |
| DATABASE_ENGINE | Движок базы данных | django.db.backends.sqlite3 или django.db.backends.postgresql |
| DATABASE_NAME | Имя базы данных | db.sqlite3 или postgres_db |
| CELERY_BROKER_URL | URL брокера сообщений | redis://localhost:6379/0 |
| EMAIL_* | Настройки почты | EMAIL_HOST=smtp.gmail.com |

## Работа с базой данных

По умолчанию проект использует SQLite, но для продакшена рекомендуется PostgreSQL.

### Настройка PostgreSQL

1. Установите PostgreSQL
2. Создайте базу данных и пользователя
3. Обновите настройки в `.env`:

```
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=getter_db
DATABASE_USER=postgres
DATABASE_PASSWORD=yourpassword
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

## Запуск проекта

### Режим разработки

#### Бэкенд:

```bash
cd getter
python manage.py runserver
```

#### Фронтенд:

```bash
cd frontend
npm run serve
```

#### Запуск Celery:

```bash
# Запуск Redis (в отдельном терминале)
redis-server

# Запуск Celery Worker (в отдельном терминале)
cd getter
python run_celery_worker.py

# Запуск Celery Beat (в отдельном терминале)
cd getter
python run_celery_beat.py

# Запуск Flower для мониторинга Celery (опционально)
cd getter
celery -A getter flower
```

### Продакшен

Для продакшен-окружения рекомендуется использовать:

- Gunicorn для запуска Django
- Nginx в качестве прокси-сервера
- PostgreSQL в качестве базы данных
- Supervisord для управления процессами

Пример настройки можно найти в директории `nginx/` и `systemd/`.

## Celery для фоновых задач

Проект использует Celery для обработки фоновых задач. Подробная информация об использовании Celery доступна в [README_CELERY.md](README_CELERY.md).

## API Документация

API документация доступна по адресу `http://localhost:8000/api/docs/` после запуска сервера разработки.

## Тестирование

### Бэкенд-тесты:

```bash
cd getter
python manage.py test
```

### Фронтенд-тесты:

```bash
cd frontend
npm run test:unit
```

## Деплоймент

### Подготовка к деплойменту

1. Установите все зависимости из `requirements.txt`
2. Настройте `.env` файл с продакшен-значениями
3. Выполните collectstatic:

```bash
python manage.py collectstatic
```

4. Проверьте настройки в `settings.py`:
   - DEBUG=False
   - Подходящие ALLOWED_HOSTS
   - Безопасные настройки для cookies
   - CORS настройки
   - Настройки базы данных

### Типовая структура деплоймента

```
/var/www/getter/
├── backend/         # Django проект
├── frontend/        # Собранный Vue.js проект
├── media/           # Загруженные файлы
├── static/          # Статические файлы
├── venv/            # Виртуальное окружение Python
└── .env             # Файл с переменными окружения
```

### Настройка Nginx

В директории `nginx/` находятся примеры конфигураций для Nginx. 