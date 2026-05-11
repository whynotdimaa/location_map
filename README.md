# Location Map API

Django REST API для карти локацій з можливістю залишати відгуки, ставити оцінки та підписуватись на оновлення.

## Технології

- Django 6.0.5
- Django REST Framework 3.15.2
- PostgreSQL 16
- Redis 7
- Celery
- Docker

## Встановлення

### Локально

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker

```bash
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## API Endpoints

### Аутентифікація
- `POST /api/auth/register/` - реєстрація
- `POST /api/auth/login/` - вхід
- `POST /api/auth/logout/` - вихід

### Локації
- `GET /api/locations/` - список локацій
- `POST /api/locations/` - створити локацію
- `GET /api/locations/{id}/` - деталі локації
- `PUT/PATCH /api/locations/{id}/` - оновити локацію
- `DELETE /api/locations/{id}/` - видалити локацію
- `GET /api/locations/export/?export_format=csv` - експорт CSV
- `GET /api/locations/export/?export_format=json` - експорт JSON

Фільтри: `?category=museum&search=назва&ordering=-avg_rating`

### Відгуки
- `GET /api/reviews/` - список відгуків
- `POST /api/reviews/` - створити відгук
- `POST /api/reviews/{id}/vote/` - проголосувати (like/dislike)

### Підписки
- `GET /api/subscriptions/` - мої підписки
- `POST /api/subscriptions/` - підписатись
- `DELETE /api/subscriptions/{id}/` - відписатись

## Документація

Swagger UI доступний за адресою: `http://localhost:8000/api/docs/`

## Змінні оточення

```env
DB_NAME=location_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/1
```

## Запуск Celery

```bash
celery -A config worker -l info
```

## Структура проекту

```
location_map/
├── apps/
│   ├── locations/     # Локації
│   ├── reviews/       # Відгуки та рейтинги
│   ├── subscriptions/ # Підписки
│   └── users/         # Користувачі
├── config/            # Налаштування Django
├── docker-compose.yml
└── requirements.txt
```

## Примітки

- Session-based аутентифікація
- Кешування через Redis (15 хв)
- Email нотифікації через Celery
- Один відгук на локацію від користувача
