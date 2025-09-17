Shop API (Django REST + JWT + Celery)

Веб-приложение интернет-магазина с корзиной, оформлением заказов, асинхронными уведомлениями и документацией API.

---

## Функциональность
- Регистрация и авторизация пользователей (JWT)
- Просмотр списка товаров и подробной информации о каждом
- Добавление и удаление товаров из корзины
- Оформление заказа (перенос содержимого корзины в заказ)
- История заказов пользователя
- Админ-панель для управления товарами и пользователями (только для staff)
- Асинхронные уведомления о заказе через Celery + Redis
- REST API с авторизацией (JWT)
- Swagger и Redoc документация API
- Поиск, фильтрация и сортировка товаров
- Кэширование списка товаров (30 секунд)
- Ограничение частоты запросов (throttling)

---

## Технологии
- Python 3.13
- Django 5.2
- Django REST Framework
- PostgreSQL
- Celery + Redis
- drf-spectacular (Swagger / OpenAPI)
- pytest + pytest-django

---

## Установка

Клонировать проект:
```bash
git clone https://github.com/dzmitrysafronau/shop_project.git
cd shop_project
```

Создать и активировать виртуальное окружение:
```
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```


Установить зависимости:
```
pip install -r requirements.txt
```


Создать файл .env на основе примера .env.example:
```
SECRET_KEY="your-django-secret-key"
DEBUG=True

DB_NAME="shop_db"
DB_USER="shop_user"
DB_PASSWORD="shop_pass"
DB_HOST="127.0.0.1"
DB_PORT="5432"

REDIS_URL="redis://127.0.0.1:6379/0"
ACCESS_TOKEN_LIFETIME_MIN=60
```


Применить миграции и создать суперпользователя:
```
python manage.py migrate
python manage.py createsuperuser
```
Запуск

Django сервер:
```
python manage.py runserver
```

Redis:
```
brew services start redis  # или redis-server вручную
```

Celery воркер:
```
celery -A config worker -l info
```
API

Базовый адрес API:
```
http://127.0.0.1:8000/api/
```
Документация

Swagger UI: http://127.0.0.1:8000/api/docs/

OpenAPI schema: http://127.0.0.1:8000/api/schema/

Тесты

Запуск тестов:
```
pytest --cov=shop -q
```
Пример запросов (curl)

Регистрация:
```
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "email": "user1@example.com", "password": "password123"}'
```

Авторизация (получение JWT):
```
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user1", "password": "password123"}'
```

Получение списка товаров:
```
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  http://127.0.0.1:8000/api/products/
```

Добавление товара в корзину:
```
curl -X POST http://127.0.0.1:8000/api/cart/add/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2}'
```

Оформление заказа:
```
curl -X POST http://127.0.0.1:8000/api/orders/create_order/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>"
```
