# Task Bot

Telegram-бот список задач и покупок. Бэкенд на Django с REST API, бот на aiogram 3, база данных PostgreSQL, деплой через Docker.

## Стек

- Python 3.12
- Django 5 + Django REST Framework
- aiogram 3
- PostgreSQL 16
- Docker Compose
- Caddy (reverse proxy + SSL)

## Возможности

- Создание задач с приоритетом, описанием и дедлайном
- Смена статуса задачи (к выполнению / в процессе / выполнено)
- Статистика по задачам
- Списки покупок с отметкой купленных позиций
- Django Admin для управления данными

## Локальный запуск

Заполнить '.env'по '.env_example':

```
BOT_TOKEN=токен_бота
USE_POLLING=True
```

Запуск:

```bash
docker compose up --build
docker compose exec web python manage.py makemigrations users tasks shopping
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

Admin панель: `http://localhost:8000/admin/`

## Деплой на сервер

В `.env` указать:

```
DEBUG=False
USE_POLLING=False
WEBHOOK_HOST=https://ваш_домен.com
ALLOWED_HOSTS=ваш_домен.com
```

В `Caddyfile` заменить домен, затем:

```bash
docker compose up -d --build
docker compose exec web python manage.py makemigrations users tasks shopping
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

SSL-сертификат Caddy получает автоматически.
