# А.Н.И. — Альбом народных историй

Django-приложение для публикации семейных историй на интерактивной карте.
Пользователи могут регистрироваться по email, добавлять истории с медиафайлами
и оставлять отзывы. Администратор модерирует публикации и пользователей.

## Локальный запуск

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

По умолчанию проект использует SQLite и выводит письма подтверждения в консоль.
Для продакшена задайте секреты и подключения через переменные окружения.

## Переменные окружения

- `DJANGO_SECRET_KEY` — секретный ключ Django.
- `DJANGO_DEBUG` — `1` только для локальной разработки.
- `DJANGO_ALLOWED_HOSTS` — список разрешённых доменов через запятую.
- `DJANGO_CSRF_TRUSTED_ORIGINS` — доверенные HTTPS-источники через запятую.
- `DJANGO_SECURE_SSL_REDIRECT` — `1` для HTTPS-редиректа в продакшене.
- `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE` — `1` для HTTPS-cookie.
- `DATABASE_URL` — строка подключения к базе данных.
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` — учётные данные SMTP.
- `YANDEX_MAPS_API_KEY` — ключ JavaScript API Яндекс Карт.
- `ANI_ADMIN_PHONE`, `ANI_ADMIN_PASSWORD` — данные главного администратора.

## Администратор

```bash
python manage.py create_admin_owner --phone +79990000000 --password strong-password
```

Команда создаёт или обновляет главного администратора, не выводя пароль в лог.

## Основные модули

- `stories/models.py` — пользователи, истории, медиафайлы и отзывы.
- `stories/forms.py` — формы регистрации, входа и публикации.
- `stories/views.py` — пользовательские и административные сценарии.
- `templates/stories/` — страницы приложения.
- `static/stories/` — стили и изображения интерфейса.
