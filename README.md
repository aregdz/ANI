# А.Н.И. — живая карта историй

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

## Основные модули

- `stories/models.py` — пользователи, истории, медиафайлы и отзывы.
- `stories/forms.py` — формы регистрации, входа и публикации.
- `stories/views.py` — пользовательские и административные сценарии.
- `templates/stories/` — страницы приложения.
- `static/stories/` — стили и изображения интерфейса.
